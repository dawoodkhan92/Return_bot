"""
Isolation tests for LLM-powered Returns Chat Agent

These tests verify the agent's functionality in isolation using mocked dependencies.
No external API calls are made during testing.
"""

import unittest
import json
import uuid
from unittest.mock import MagicMock, patch, Mock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_returns_chat_agent import LLMReturnsChatAgent


class TestLLMReturnsChatAgentIsolation(unittest.TestCase):
    """Test suite for LLM Returns Chat Agent in isolation."""

    def setUp(self):
        """Set up test fixtures with mocked dependencies."""
        self.test_config = {
            'OPENAI_API_KEY': 'test_api_key',
            'OPENAI_PROJECT_ID': 'test_project',
            'OPENAI_ORG_ID': 'test_org',
            'OPENAI_MODEL': 'gpt-4o',
            'SHOPIFY_ADMIN_TOKEN': 'test_shopify_token',
            'SHOPIFY_STORE_DOMAIN': 'test-store.myshopify.com'
        }
        
        # Sample test data
        self.sample_order = {
            'id': 'gid://shopify/Order/123456',
            'name': '#1001',
            'email': 'customer@example.com',
            'created_at': '2024-01-15T10:00:00Z',
            'line_items': {
                'edges': [
                    {
                        'node': {
                            'id': 'gid://shopify/LineItem/111',
                            'title': 'Test Product 1',
                            'quantity': 1,
                            'variant': {
                                'price': '29.99'
                            }
                        }
                    },
                    {
                        'node': {
                            'id': 'gid://shopify/LineItem/222',
                            'title': 'Test Product 2',
                            'quantity': 2,
                            'variant': {
                                'price': '49.99'
                            }
                        }
                    }
                ]
            }
        }
        
        self.sample_greeting_response = {
            'choices': [{
                'message': {
                    'content': 'Hello! I\'d be happy to help you with your return. Could you please provide your order number or email address?'
                }
            }]
        }
        
        self.sample_function_call_response = {
            'choices': [{
                'message': {
                    'tool_calls': [{
                        'id': 'call_123',
                        'function': {
                            'name': 'lookup_order_by_id',
                            'arguments': json.dumps({'order_id': '1001'})
                        }
                    }]
                }
            }]
        }
        
        # Mock all external dependencies
        self.mock_patches = []
        
        # Mock OpenAI client
        self.mock_openai_client = MagicMock()
        openai_patch = patch('llm_returns_chat_agent.OpenAI', return_value=self.mock_openai_client)
        self.mock_patches.append(openai_patch)
        
        # Mock tools
        self.mock_order_lookup = MagicMock()
        order_lookup_patch = patch('llm_returns_chat_agent.OrderLookup', return_value=self.mock_order_lookup)
        self.mock_patches.append(order_lookup_patch)
        
        self.mock_policy_checker = MagicMock()
        policy_patch = patch('llm_returns_chat_agent.PolicyChecker', return_value=self.mock_policy_checker)
        self.mock_patches.append(policy_patch)
        
        self.mock_refund_processor = MagicMock()
        refund_patch = patch('llm_returns_chat_agent.RefundProcessor', return_value=self.mock_refund_processor)
        self.mock_patches.append(refund_patch)
        
        self.mock_conversation_logger = MagicMock()
        logger_patch = patch('llm_returns_chat_agent.ConversationLogger', return_value=self.mock_conversation_logger)
        self.mock_patches.append(logger_patch)
        
        # Start all patches
        for patch_obj in self.mock_patches:
            patch_obj.start()
            
        # Initialize agent with mocked dependencies
        self.agent = LLMReturnsChatAgent(self.test_config)

    def tearDown(self):
        """Clean up patches after each test."""
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def test_initialization(self):
        """Test agent initialization with valid configuration."""
        self.assertEqual(self.agent.model, 'gpt-4o')
        self.assertIsNone(self.agent.conversation_id)
        self.assertEqual(self.agent.messages, [])
        self.assertEqual(self.agent.context, {})
        self.assertEqual(len(self.agent.tools), 4)
        
        # Verify OpenAI client was initialized with correct parameters
        self.mock_openai_client.assert_called_once()

    def test_start_conversation(self):
        """Test starting a new conversation."""
        # Mock OpenAI response
        self.mock_openai_client.chat.completions.create.return_value = self.sample_greeting_response
        
        greeting = self.agent.start_conversation()
        
        # Verify conversation was initialized
        self.assertIsNotNone(self.agent.conversation_id)
        self.assertEqual(len(self.agent.messages), 3)  # System, user, assistant
        self.assertEqual(self.agent.messages[0]['role'], 'system')
        self.assertEqual(self.agent.messages[1]['role'], 'user')
        self.assertEqual(self.agent.messages[2]['role'], 'assistant')
        
        # Verify OpenAI was called
        self.mock_openai_client.chat.completions.create.assert_called_once()
        
        # Verify conversation was logged
        self.mock_conversation_logger.log_interaction.assert_called_once()

    def test_process_message_with_function_call(self):
        """Test processing a message that triggers a function call."""
        # Setup conversation
        self.agent.conversation_id = str(uuid.uuid4())
        self.agent.messages = [{'role': 'system', 'content': 'test'}]
        
        # Mock OpenAI function call response
        self.mock_openai_client.chat.completions.create.return_value = self.sample_function_call_response
        
        # Mock order lookup tool
        self.mock_order_lookup.lookup_by_id.return_value = self.sample_order
        
        # Mock follow-up response after function execution
        follow_up_response = {
            'choices': [{
                'message': {
                    'content': 'I found your order #1001! It contains 2 items. Which item would you like to return?'
                }
            }]
        }
        self.mock_openai_client.chat.completions.create.side_effect = [
            self.sample_function_call_response,
            follow_up_response
        ]
        
        response = self.agent.process_message("I want to return order #1001")
        
        # Verify function was called
        self.mock_order_lookup.lookup_by_id.assert_called_once_with('1001')
        
        # Verify OpenAI was called twice (initial + follow-up)
        self.assertEqual(self.mock_openai_client.chat.completions.create.call_count, 2)
        
        # Verify conversation was logged
        self.mock_conversation_logger.log_interaction.assert_called()

    def test_execute_function_lookup_order_by_id(self):
        """Test executing the lookup_order_by_id function."""
        self.mock_order_lookup.lookup_by_id.return_value = self.sample_order
        
        result = self.agent._execute_function('lookup_order_by_id', {'order_id': '1001'})
        
        self.mock_order_lookup.lookup_by_id.assert_called_once_with('1001')
        self.assertEqual(result, self.sample_order)

    def test_execute_function_lookup_order_by_email(self):
        """Test executing the lookup_order_by_email function."""
        orders_response = {'orders': [self.sample_order]}
        self.mock_order_lookup.lookup_by_email.return_value = orders_response
        
        result = self.agent._execute_function('lookup_order_by_email', {'email': 'customer@example.com'})
        
        self.mock_order_lookup.lookup_by_email.assert_called_once_with('customer@example.com')
        self.assertEqual(result, orders_response)

    def test_execute_function_check_return_eligibility(self):
        """Test executing the check_return_eligibility function."""
        eligibility_response = {
            'decision': 'approve',
            'reason': 'Within return window'
        }
        self.mock_policy_checker.check_eligibility.return_value = eligibility_response
        
        result = self.agent._execute_function('check_return_eligibility', {
            'order_date': '2024-01-15T10:00:00Z',
            'item_id': 'gid://shopify/LineItem/111',
            'return_reason': 'wrong_size'
        })
        
        self.mock_policy_checker.check_eligibility.assert_called_once()
        self.assertEqual(result, eligibility_response)

    def test_execute_function_process_refund(self):
        """Test executing the process_refund function."""
        refund_response = {
            'success': True,
            'refund_id': 'gid://shopify/Refund/789',
            'amount': '29.99'
        }
        self.mock_refund_processor.process_refund.return_value = refund_response
        
        result = self.agent._execute_function('process_refund', {
            'order_id': 'gid://shopify/Order/123456',
            'line_item_id': 'gid://shopify/LineItem/111',
            'quantity': 1,
            'reason': 'wrong_size'
        })
        
        self.mock_refund_processor.process_refund.assert_called_once()
        self.assertEqual(result, refund_response)

    def test_execute_function_invalid_function_name(self):
        """Test executing an invalid function name."""
        result = self.agent._execute_function('invalid_function', {})
        
        self.assertIn('error', result)
        self.assertIn('Unknown function', result['error'])

    def test_conversation_state_management(self):
        """Test that conversation state is properly managed."""
        # Start conversation
        self.mock_openai_client.chat.completions.create.return_value = self.sample_greeting_response
        self.agent.start_conversation()
        
        initial_conversation_id = self.agent.conversation_id
        initial_message_count = len(self.agent.messages)
        
        # Process a message
        self.mock_openai_client.chat.completions.create.return_value = {
            'choices': [{
                'message': {
                    'content': 'Thank you for your message!'
                }
            }]
        }
        
        self.agent.process_message("Test message")
        
        # Verify state is maintained
        self.assertEqual(self.agent.conversation_id, initial_conversation_id)
        self.assertEqual(len(self.agent.messages), initial_message_count + 2)  # user + assistant

    def test_get_conversation_summary(self):
        """Test getting conversation summary."""
        # Setup conversation
        self.agent.conversation_id = str(uuid.uuid4())
        self.agent.messages = [
            {'role': 'system', 'content': 'System prompt'},
            {'role': 'user', 'content': 'I want to return my order'},
            {'role': 'assistant', 'content': 'I can help with that'}
        ]
        
        # Mock OpenAI summary response
        summary_response = {
            'choices': [{
                'message': {
                    'content': 'Customer initiated return request'
                }
            }]
        }
        self.mock_openai_client.chat.completions.create.return_value = summary_response
        
        summary = self.agent.get_conversation_summary()
        
        self.assertEqual(summary, 'Customer initiated return request')
        self.mock_openai_client.chat.completions.create.assert_called_once()

    def test_get_conversation_history(self):
        """Test getting conversation history."""
        # Setup conversation
        self.agent.messages = [
            {'role': 'user', 'content': 'Test message 1'},
            {'role': 'assistant', 'content': 'Test response 1'}
        ]
        
        history = self.agent.get_conversation_history()
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[1]['role'], 'assistant')

    def test_get_and_set_state(self):
        """Test getting and setting agent state."""
        # Setup initial state
        self.agent.conversation_id = 'test_id'
        self.agent.context = {'test': 'value'}
        self.agent.messages = [{'role': 'user', 'content': 'test'}]
        
        # Get state
        state = self.agent.get_state()
        
        self.assertEqual(state['conversation_id'], 'test_id')
        self.assertEqual(state['context'], {'test': 'value'})
        self.assertEqual(len(state['messages']), 1)
        
        # Set new state
        new_state = {
            'conversation_id': 'new_id',
            'context': {'new': 'context'},
            'messages': [{'role': 'assistant', 'content': 'new message'}]
        }
        
        self.agent.set_state(new_state)
        
        self.assertEqual(self.agent.conversation_id, 'new_id')
        self.assertEqual(self.agent.context, {'new': 'context'})
        self.assertEqual(len(self.agent.messages), 1)

    def test_error_handling_openai_failure(self):
        """Test error handling when OpenAI API fails."""
        # Mock OpenAI failure
        self.mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        
        with self.assertRaises(Exception):
            self.agent.start_conversation()

    def test_error_handling_tool_failure(self):
        """Test error handling when a tool fails."""
        # Setup conversation
        self.agent.conversation_id = str(uuid.uuid4())
        self.agent.messages = [{'role': 'system', 'content': 'test'}]
        
        # Mock tool failure
        self.mock_order_lookup.lookup_by_id.side_effect = Exception("Tool Error")
        
        result = self.agent._execute_function('lookup_order_by_id', {'order_id': '1001'})
        
        self.assertIn('error', result)
        self.assertIn('Tool Error', result['error'])

    def test_tool_function_schemas(self):
        """Test that tool function schemas are properly defined."""
        self.assertEqual(len(self.agent.tools), 4)
        
        tool_names = [tool['function']['name'] for tool in self.agent.tools]
        expected_names = [
            'lookup_order_by_id',
            'lookup_order_by_email', 
            'check_return_eligibility',
            'process_refund'
        ]
        
        for name in expected_names:
            self.assertIn(name, tool_names)
            
        # Verify each tool has required parameters
        for tool in self.agent.tools:
            self.assertIn('parameters', tool['function'])
            self.assertIn('properties', tool['function']['parameters'])
            self.assertIn('required', tool['function']['parameters'])


if __name__ == '__main__':
    unittest.main() 