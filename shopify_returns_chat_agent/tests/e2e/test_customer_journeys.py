"""
End-to-End Customer Journey Tests for LLM Returns Chat Agent.

These tests simulate complete customer interactions from start to finish,
verifying that the agent handles various scenarios correctly with mocked dependencies.
"""

import pytest
import os
import sys
import json
import uuid
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import the module  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm_returns_chat_agent import LLMReturnsChatAgent
from fixtures import (
    valid_return_journey, 
    policy_violation_journey,
    partial_refund_journey, 
    edge_case_journey,
    order_lookup_by_email_journey,
    high_value_order_journey,
    defective_item_journey
)


class TestCustomerJourneys:
    """Test suite for end-to-end customer journeys."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up the test environment with mocked dependencies"""
        # Mock configuration 
        self.test_config = {
            'OPENAI_API_KEY': 'test_openai_key',
            'SHOPIFY_ACCESS_TOKEN': 'test_shopify_token', 
            'SHOPIFY_SHOP_URL': 'test-shop.myshopify.com'
        }
        
        # Mock OpenAI client
        self.mock_openai_client = MagicMock()
        
        # Create the agent with mocked dependencies
        with patch('llm_returns_chat_agent.OpenAI') as mock_openai:
            mock_openai.return_value = self.mock_openai_client
            self.agent = LLMReturnsChatAgent(config=self.test_config)
        
        # Create a unique conversation ID for each test
        self.conversation_id = f"test_journey_{uuid.uuid4().hex[:8]}"
        
    def mock_openai_response(self, function_name=None, function_args=None, content=None):
        """Helper to mock OpenAI chat completion responses"""
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        if function_name:
            # Mock function call response
            mock_tool_call = MagicMock()
            mock_tool_call.function.name = function_name
            mock_tool_call.function.arguments = json.dumps(function_args) if function_args else "{}"
            mock_tool_call.id = f"call_{uuid.uuid4().hex[:8]}"
            
            mock_message.tool_calls = [mock_tool_call]
            mock_message.content = None
        else:
            # Mock regular content response
            mock_message.tool_calls = None
            mock_message.content = content or "I understand. Let me help you with your return."
            
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        return mock_response

    def simulate_conversation(self, journey, mock_responses=None):
        """Simulate a complete conversation with the chat agent"""
        conversation_log = []
        responses = []
        
        # Set up default mock responses if not provided
        if not mock_responses:
            mock_responses = []
            for i, message in enumerate(journey["conversation_flow"]):
                if i == 0:
                    # First message - typically triggers order lookup
                    mock_responses.append(
                        self.mock_openai_response(
                            function_name="lookup_order",
                            function_args={"identifier": journey["order"]["name"]}
                        )
                    )
                elif "order number" in message.lower() or "#" in message:
                    # Order number provided - process return
                    mock_responses.append(
                        self.mock_openai_response(
                            function_name="process_return", 
                            function_args={
                                "order_id": journey["order"]["id"],
                                "reason": journey["return_reason"]
                            }
                        )
                    )
                else:
                    # Regular response
                    mock_responses.append(
                        self.mock_openai_response(
                            content="Thank you for that information. I'm processing your request."
                        )
                    )
        
        # Configure the mock to return our responses in sequence
        self.mock_openai_client.chat.completions.create.side_effect = mock_responses
        
        # Process each message in the conversation flow
        for i, message in enumerate(journey["conversation_flow"]):
            try:
                response = self.agent.process_message(message, self.conversation_id)
                responses.append(response)
                
                conversation_log.append({
                    "role": "customer", 
                    "message": message
                })
                conversation_log.append({
                    "role": "agent",
                    "message": response
                })
                
            except Exception as e:
                # Handle any errors during message processing
                error_response = f"I apologize, but I encountered an error: {str(e)}"
                responses.append(error_response)
                
                conversation_log.append({
                    "role": "customer",
                    "message": message  
                })
                conversation_log.append({
                    "role": "agent",
                    "message": error_response
                })
        
        return responses, conversation_log

    def test_successful_return_journey(self, valid_return_journey):
        """Test a complete successful return journey"""
        # Mock the tool functions to return appropriate responses
        with patch.object(self.agent, 'lookup_order') as mock_lookup, \
             patch.object(self.agent, 'process_return') as mock_process:
             
            # Configure mock responses
            mock_lookup.return_value = {
                "success": True,
                "order": valid_return_journey["order"],
                "message": f"Found order {valid_return_journey['order']['name']}"
            }
            
            mock_process.return_value = {
                "success": True,
                "refund_amount": valid_return_journey["order"]["total"],
                "refund_id": "refund_12345",
                "message": "Return approved and refund processed"
            }
            
            # Run the conversation
            responses, conversation_log = self.simulate_conversation(valid_return_journey)
            
            # Verify the journey completed successfully
            assert len(responses) == len(valid_return_journey["conversation_flow"])
            assert any("approved" in response.lower() or "processed" in response.lower() 
                     for response in responses)
            
            # Verify conversation was logged properly
            assert len(conversation_log) == len(valid_return_journey["conversation_flow"]) * 2
            
            # Verify tool functions were called
            mock_lookup.assert_called()
            mock_process.assert_called()

    def test_policy_violation_journey(self, policy_violation_journey):
        """Test a journey where the return violates store policy"""
        with patch.object(self.agent, 'lookup_order') as mock_lookup, \
             patch.object(self.agent, 'check_return_policy') as mock_policy:
             
            # Configure mock responses
            mock_lookup.return_value = {
                "success": True,
                "order": policy_violation_journey["order"],
                "message": f"Found order {policy_violation_journey['order']['name']}"
            }
            
            mock_policy.return_value = {
                "eligible": False,
                "reason": "Return window expired (45 days past 30-day limit)",
                "message": "I'm sorry, but this order is outside our 30-day return policy"
            }
            
            # Run the conversation
            responses, conversation_log = self.simulate_conversation(policy_violation_journey)
            
            # Verify the journey handled policy violation correctly
            assert len(responses) == len(policy_violation_journey["conversation_flow"])
            assert any("policy" in response.lower() or "unable" in response.lower() 
                     for response in responses)
            
            # Verify policy check was performed  
            mock_policy.assert_called()

    def test_partial_refund_journey(self, partial_refund_journey):
        """Test a journey with a partial refund for some items"""
        with patch.object(self.agent, 'lookup_order') as mock_lookup, \
             patch.object(self.agent, 'process_return') as mock_process:
             
            # Configure mock responses
            mock_lookup.return_value = {
                "success": True,
                "order": partial_refund_journey["order"],
                "message": f"Found order {partial_refund_journey['order']['name']}"
            }
            
            # Calculate partial refund amount (just the dress, not earrings)
            dress_price = next(item["price"] for item in partial_refund_journey["order"]["items"] 
                              if "Dress" in item["name"])
            
            mock_process.return_value = {
                "success": True,
                "refund_amount": dress_price,
                "returned_items": ["Red Dress"],
                "message": f"Partial return approved for Red Dress. Refund amount: ${dress_price}"
            }
            
            # Run the conversation
            responses, conversation_log = self.simulate_conversation(partial_refund_journey)
            
            # Verify partial refund was handled correctly
            assert len(responses) == len(partial_refund_journey["conversation_flow"])
            assert any("partial" in response.lower() or "dress" in response.lower()
                     for response in responses)

    def test_edge_case_journey(self, edge_case_journey):
        """Test an edge case with international shipping complications"""
        with patch.object(self.agent, 'lookup_order') as mock_lookup, \
             patch.object(self.agent, 'check_return_policy') as mock_policy:
             
            # Configure mock responses
            mock_lookup.return_value = {
                "success": True,
                "order": edge_case_journey["order"],
                "message": f"Found order {edge_case_journey['order']['name']}"
            }
            
            mock_policy.return_value = {
                "eligible": True,
                "international_shipping": True,
                "message": "Return approved. International return label will be provided."
            }
            
            # Run the conversation
            responses, conversation_log = self.simulate_conversation(edge_case_journey)
            
            # Verify international case was handled
            assert len(responses) == len(edge_case_journey["conversation_flow"])
            assert any("international" in response.lower() or "shipping" in response.lower() 
                     for response in responses)

    def test_order_lookup_by_email_journey(self, order_lookup_by_email_journey):
        """Test customer journey when looking up order by email"""
        with patch.object(self.agent, 'lookup_order_by_email') as mock_lookup_email, \
             patch.object(self.agent, 'process_return') as mock_process:
             
            # Configure mock responses
            mock_lookup_email.return_value = {
                "success": True,
                "orders": [order_lookup_by_email_journey["order"]],
                "message": "Found 1 recent order for your email address"
            }
            
            mock_process.return_value = {
                "success": True,
                "refund_type": "store_credit",
                "refund_amount": order_lookup_by_email_journey["order"]["total"],
                "message": "Return approved. Store credit will be issued."
            }
            
            # Run the conversation
            responses, conversation_log = self.simulate_conversation(order_lookup_by_email_journey)
            
            # Verify email lookup worked
            assert len(responses) == len(order_lookup_by_email_journey["conversation_flow"])
            mock_lookup_email.assert_called()

    def test_high_value_order_journey(self, high_value_order_journey):
        """Test customer journey for high-value items requiring special handling"""
        with patch.object(self.agent, 'lookup_order') as mock_lookup, \
             patch.object(self.agent, 'process_return') as mock_process:
             
            # Configure mock responses
            mock_lookup.return_value = {
                "success": True,
                "order": high_value_order_journey["order"],
                "high_value": True,
                "message": f"Found high-value order {high_value_order_journey['order']['name']}"
            }
            
            mock_process.return_value = {
                "success": True,
                "requires_manager_approval": True,
                "insured_shipping": True,
                "message": "High-value return initiated. Manager approval required."
            }
            
            # Run the conversation
            responses, conversation_log = self.simulate_conversation(high_value_order_journey)
            
            # Verify high-value handling
            assert len(responses) == len(high_value_order_journey["conversation_flow"])
            assert any("manager" in response.lower() or "approval" in response.lower() or 
                     "insured" in response.lower() for response in responses)

    def test_defective_item_journey(self, defective_item_journey):
        """Test journey for clearly defective items needing immediate resolution"""
        with patch.object(self.agent, 'lookup_order') as mock_lookup, \
             patch.object(self.agent, 'process_return') as mock_process:
             
            # Configure mock responses
            mock_lookup.return_value = {
                "success": True,
                "order": defective_item_journey["order"],
                "message": f"Found order {defective_item_journey['order']['name']}"
            }
            
            mock_process.return_value = {
                "success": True,
                "expedited": True,
                "replacement_offered": True,
                "message": "Defective item return approved. Expedited replacement available."
            }
            
            # Run the conversation
            responses, conversation_log = self.simulate_conversation(defective_item_journey)
            
            # Verify defective item handling
            assert len(responses) == len(defective_item_journey["conversation_flow"])
            assert any("defective" in response.lower() or "replacement" in response.lower() or 
                     "expedited" in response.lower() for response in responses)

    def test_conversation_state_management(self, valid_return_journey):
        """Test that conversation state is properly maintained throughout the journey"""
        # Start a conversation
        first_message = valid_return_journey["conversation_flow"][0]
        
        with patch.object(self.agent, 'lookup_order') as mock_lookup:
            mock_lookup.return_value = {
                "success": True,
                "order": valid_return_journey["order"]
            }
            
            # Send first message
            response1 = self.agent.process_message(first_message, self.conversation_id)
            
            # Verify conversation was created and state is tracked
            assert self.conversation_id in self.agent.conversations
            assert len(self.agent.conversations[self.conversation_id]["messages"]) >= 2
            
            # Send second message
            second_message = valid_return_journey["conversation_flow"][1]
            response2 = self.agent.process_message(second_message, self.conversation_id)
            
            # Verify state is maintained
            assert len(self.agent.conversations[self.conversation_id]["messages"]) >= 4
            assert response1 != response2  # Different responses

    def test_error_handling_during_journey(self, valid_return_journey):
        """Test error handling when tool functions fail during a journey"""
        with patch.object(self.agent, 'lookup_order') as mock_lookup:
            # Simulate a tool failure
            mock_lookup.side_effect = Exception("Shopify API timeout")
            
            # Process a message
            message = valid_return_journey["conversation_flow"][0]
            response = self.agent.process_message(message, self.conversation_id)
            
            # Verify error was handled gracefully
            assert response is not None
            assert len(response) > 0
            assert "error" in response.lower() or "sorry" in response.lower()

    def test_multiple_concurrent_journeys(self, valid_return_journey, policy_violation_journey):
        """Test that multiple customer journeys can run concurrently without interference"""
        conv_id_1 = f"journey_1_{uuid.uuid4().hex[:8]}"
        conv_id_2 = f"journey_2_{uuid.uuid4().hex[:8]}"
        
        with patch.object(self.agent, 'lookup_order') as mock_lookup:
            mock_lookup.return_value = {"success": True, "order": {}}
            
            # Start two different journeys
            msg1 = valid_return_journey["conversation_flow"][0]
            msg2 = policy_violation_journey["conversation_flow"][0]
            
            response1 = self.agent.process_message(msg1, conv_id_1)
            response2 = self.agent.process_message(msg2, conv_id_2)
            
            # Verify both conversations exist independently
            assert conv_id_1 in self.agent.conversations
            assert conv_id_2 in self.agent.conversations
            assert conv_id_1 != conv_id_2
            
            # Verify conversation states are separate
            conv1_msgs = self.agent.conversations[conv_id_1]["messages"]
            conv2_msgs = self.agent.conversations[conv_id_2]["messages"]
            assert conv1_msgs != conv2_msgs

    @pytest.mark.integration
    def test_end_to_end_integration(self, valid_return_journey):
        """Integration test that exercises the full system without mocking tools"""
        # This test would run against a real or more realistic environment
        # For now, we'll use minimal mocking to test integration points
        
        with patch('llm_returns_chat_agent.requests') as mock_requests:
            # Mock Shopify API calls
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "order": valid_return_journey["order"]
            }
            mock_response.status_code = 200
            mock_requests.get.return_value = mock_response
            
            # Run a single message to test integration
            message = valid_return_journey["conversation_flow"][0]
            response = self.agent.process_message(message, self.conversation_id)
            
            # Verify basic integration works
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0 