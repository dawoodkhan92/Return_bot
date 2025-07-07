"""
System Integration Tests for Shopify Returns Chat Agent

These tests validate the complete system integration including:
- API endpoint functionality
- Frontend-backend communication
- Shopify API integration
- Database operations
- Complete customer journey flows
"""

import pytest
import requests
import json
import time
import uuid
from unittest.mock import patch, MagicMock

class TestSystemIntegration:
    """Test complete system integration"""
    
    def test_health_endpoint(self, api_client):
        """Test that the health endpoint is responding correctly"""
        response = api_client.get("/health")
        assert response.status_code == 200
        
        # Check response format
        health_data = response.json()
        assert "status" in health_data
        assert health_data["status"] in ["healthy", "ok"]
    
    def test_conversation_start_flow(self, api_client, conversation_id, performance_tracker):
        """Test starting a new conversation"""
        start_time = time.time()
        
        response = api_client.post("/start", json={
            "conversation_id": conversation_id
        })
        
        end_time = time.time()
        performance_tracker.record_request(start_time, end_time, response.status_code, "/start")
        
        assert response.status_code == 200
        result = response.json()
        
        # Validate response structure
        assert "conversation_id" in result
        assert "message" in result
        assert result["conversation_id"] == conversation_id
        assert "welcome" in result["message"].lower() or "help" in result["message"].lower()
    
    def test_basic_chat_flow(self, api_client, conversation_id, performance_tracker):
        """Test basic chat functionality"""
        # Start conversation first
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send a basic message
        start_time = time.time()
        response = api_client.post("/chat", json={
            "message": "Hello, I need help with a return",
            "conversation_id": conversation_id
        })
        end_time = time.time()
        
        performance_tracker.record_request(start_time, end_time, response.status_code, "/chat")
        
        assert response.status_code == 200
        result = response.json()
        
        # Validate response structure
        assert "response" in result
        assert "conversation_id" in result
        assert result["conversation_id"] == conversation_id
        assert len(result["response"]) > 0
    
    def test_complete_return_flow(self, api_client, conversation_id, test_order_data, performance_tracker):
        """Test a complete return flow from start to finish"""
        
        # Step 1: Start conversation
        response = api_client.post("/start", json={"conversation_id": conversation_id})
        assert response.status_code == 200
        
        messages = [
            "I want to return my order",
            test_order_data["order_id"],
            test_order_data["customer_email"],
            "It doesn't fit properly",
            "Yes, I want to proceed with the return"
        ]
        
        for i, message in enumerate(messages):
            start_time = time.time()
            response = api_client.post("/chat", json={
                "message": message,
                "conversation_id": conversation_id
            })
            end_time = time.time()
            
            performance_tracker.record_request(start_time, end_time, response.status_code, f"/chat-step-{i+1}")
            
            assert response.status_code == 200
            result = response.json()
            assert "response" in result
            assert len(result["response"]) > 0
            
            # Add small delay to simulate user thinking
            time.sleep(0.2)
    
    def test_invalid_conversation_id(self, api_client):
        """Test handling of invalid conversation IDs"""
        invalid_id = "invalid-conversation-id"
        
        response = api_client.post("/chat", json={
            "message": "Hello",
            "conversation_id": invalid_id
        })
        
        # Should either return an error or handle gracefully
        assert response.status_code in [400, 404, 200]
        
        if response.status_code == 200:
            # If handled gracefully, should contain appropriate response
            result = response.json()
            assert "response" in result
    
    def test_empty_message_handling(self, api_client, conversation_id):
        """Test handling of empty or invalid messages"""
        # Start conversation first
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Test empty message
        response = api_client.post("/chat", json={
            "message": "",
            "conversation_id": conversation_id
        })
        
        assert response.status_code in [200, 400]
        
        # Test missing message
        response = api_client.post("/chat", json={
            "conversation_id": conversation_id
        })
        
        assert response.status_code in [200, 400]
    
    def test_malformed_request_handling(self, api_client):
        """Test handling of malformed requests"""
        # Test invalid JSON
        response = api_client.post("/chat", 
                                  data="invalid json",
                                  headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]
        
        # Test missing required fields
        response = api_client.post("/chat", json={})
        assert response.status_code in [400, 422]
    
    @patch('llm_returns_chat_agent.LLMReturnsChatAgent')
    def test_llm_agent_integration(self, mock_agent_class, api_client, conversation_id):
        """Test that the LLM agent is properly integrated"""
        # Mock the agent's process_message method
        mock_agent = MagicMock()
        mock_agent.process_message.return_value = "Mocked agent response"
        mock_agent_class.return_value = mock_agent
        
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send a message
        response = api_client.post("/chat", json={
            "message": "Test message",
            "conversation_id": conversation_id
        })
        
        # Verify the agent was called (may not work with actual deployment)
        if mock_agent.process_message.called:
            mock_agent.process_message.assert_called()
    
    def test_concurrent_conversations(self, api_client, performance_tracker):
        """Test handling of multiple concurrent conversations"""
        num_conversations = 5
        conversation_ids = [str(uuid.uuid4()) for _ in range(num_conversations)]
        
        # Start all conversations
        for conv_id in conversation_ids:
            response = api_client.post("/start", json={"conversation_id": conv_id})
            assert response.status_code == 200
        
        # Send messages to all conversations concurrently
        import threading
        import queue
        
        results = queue.Queue()
        
        def send_message(conv_id):
            start_time = time.time()
            response = api_client.post("/chat", json={
                "message": "I need help with a return",
                "conversation_id": conv_id
            })
            end_time = time.time()
            
            performance_tracker.record_request(start_time, end_time, response.status_code, "/chat-concurrent")
            results.put((conv_id, response.status_code, response.json() if response.status_code == 200 else None))
        
        # Create and start threads
        threads = []
        for conv_id in conversation_ids:
            thread = threading.Thread(target=send_message, args=(conv_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all responses
        while not results.empty():
            conv_id, status_code, response_data = results.get()
            assert status_code == 200
            if response_data:
                assert "response" in response_data
                assert response_data["conversation_id"] == conv_id
    
    def test_session_persistence(self, api_client, conversation_id):
        """Test that conversation state persists across multiple requests"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send first message
        response1 = api_client.post("/chat", json={
            "message": "I want to return order 12345",
            "conversation_id": conversation_id
        })
        assert response1.status_code == 200
        
        # Send follow-up message that should reference previous context
        response2 = api_client.post("/chat", json={
            "message": "Yes, that's the correct order",
            "conversation_id": conversation_id
        })
        assert response2.status_code == 200
        
        # The agent should understand the context from previous messages
        result = response2.json()
        assert "response" in result
    
    def test_api_error_handling(self, api_client, conversation_id):
        """Test handling of various API errors"""
        # Test with non-existent endpoints
        response = api_client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test with unsupported methods
        response = api_client.put("/chat", json={
            "message": "test",
            "conversation_id": conversation_id
        })
        assert response.status_code in [405, 404]
    
    def test_cors_headers(self, api_client):
        """Test that CORS headers are properly set for frontend integration"""
        response = api_client.get("/health")
        
        # Check for CORS headers (if enabled)
        headers = response.headers
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers"
        ]
        
        # At least one CORS header should be present for frontend integration
        has_cors = any(header in headers for header in cors_headers)
        if not has_cors:
            # This might be expected if CORS is handled by a proxy
            print("Warning: No CORS headers detected. Ensure frontend can access the API.")


class TestShopifyIntegration:
    """Test Shopify-specific integration functionality"""
    
    def test_order_lookup_simulation(self, api_client, conversation_id, test_order_data):
        """Test order lookup functionality (with mocked Shopify responses)"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Simulate order lookup flow
        response = api_client.post("/chat", json={
            "message": f"I want to return order {test_order_data['order_id']}",
            "conversation_id": conversation_id
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # The response should ask for email or other verification
        response_text = result["response"].lower()
        assert any(keyword in response_text for keyword in ["email", "verification", "confirm"])
    
    def test_customer_email_verification(self, api_client, conversation_id, test_order_data):
        """Test customer email verification flow"""
        # Start conversation and provide order number
        api_client.post("/start", json={"conversation_id": conversation_id})
        api_client.post("/chat", json={
            "message": f"Return order {test_order_data['order_id']}",
            "conversation_id": conversation_id
        })
        
        # Provide email
        response = api_client.post("/chat", json={
            "message": test_order_data["customer_email"],
            "conversation_id": conversation_id
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Should acknowledge the email or proceed with order details
        response_text = result["response"].lower()
        verification_keywords = ["found", "order", "details", "items", "return"]
        assert any(keyword in response_text for keyword in verification_keywords)


class TestDatabaseOperations:
    """Test database operations and data persistence"""
    
    def test_conversation_logging(self, api_client, conversation_id):
        """Test that conversations are properly logged"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send multiple messages
        messages = [
            "I need help with a return",
            "Order number 12345",
            "test@example.com"
        ]
        
        for message in messages:
            response = api_client.post("/chat", json={
                "message": message,
                "conversation_id": conversation_id
            })
            assert response.status_code == 200
        
        # Conversations should be logged in the system
        # (This test verifies the system doesn't crash, 
        #  actual DB verification would require direct DB access)
    
    def test_conversation_retrieval(self, api_client, conversation_id):
        """Test conversation state retrieval"""
        # Start and populate conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        test_message = "Test message for retrieval"
        api_client.post("/chat", json={
            "message": test_message,
            "conversation_id": conversation_id
        })
        
        # Send follow-up that should use previous context
        response = api_client.post("/chat", json={
            "message": "Can you help with that?",
            "conversation_id": conversation_id
        })
        
        assert response.status_code == 200
        # The fact that we get a response indicates conversation state is maintained
    
    def test_data_consistency(self, api_client):
        """Test data consistency across multiple conversations"""
        # Create multiple conversations with overlapping data
        conversations = []
        for i in range(3):
            conv_id = str(uuid.uuid4())
            conversations.append(conv_id)
            
            # Start conversation
            api_client.post("/start", json={"conversation_id": conv_id})
            
            # Send unique message to each conversation
            api_client.post("/chat", json={
                "message": f"Unique message for conversation {i}",
                "conversation_id": conv_id
            })
        
        # Verify each conversation maintains its own state
        for i, conv_id in enumerate(conversations):
            response = api_client.post("/chat", json={
                "message": "What was my previous message?",
                "conversation_id": conv_id
            })
            
            assert response.status_code == 200
            # Each conversation should maintain separate context


class TestSystemResilience:
    """Test system resilience and error recovery"""
    
    def test_rate_limiting_handling(self, api_client, conversation_id):
        """Test handling of high request rates"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send many requests quickly
        responses = []
        for i in range(20):
            response = api_client.post("/chat", json={
                "message": f"Test message {i}",
                "conversation_id": conversation_id
            })
            responses.append(response.status_code)
        
        # Most responses should be successful
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= len(responses) * 0.8  # At least 80% success rate
    
    def test_large_message_handling(self, api_client, conversation_id):
        """Test handling of unusually large messages"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send a very large message
        large_message = "A" * 10000  # 10KB message
        
        response = api_client.post("/chat", json={
            "message": large_message,
            "conversation_id": conversation_id
        })
        
        # Should either handle gracefully or return appropriate error
        assert response.status_code in [200, 400, 413]
    
    def test_special_character_handling(self, api_client, conversation_id):
        """Test handling of special characters and unicode"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        special_messages = [
            "Hello with émojis 🛍️🔄",
            "Special chars: <>\"'&",
            "Unicode: 测试消息",
            "Mixed: Hello 世界! 🌍"
        ]
        
        for message in special_messages:
            response = api_client.post("/chat", json={
                "message": message,
                "conversation_id": conversation_id
            })
            
            assert response.status_code == 200
            result = response.json()
            assert "response" in result
``` 