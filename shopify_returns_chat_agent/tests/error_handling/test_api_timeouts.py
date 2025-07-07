"""
API timeout tests for LLM Returns Chat Agent.

These tests verify that the agent handles various API timeout scenarios
gracefully and provides appropriate timeout-specific error responses.
"""

import unittest
import json
import sys
import os
import time
from unittest.mock import MagicMock, patch, Mock
import requests
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm_returns_chat_agent import LLMReturnsChatAgent


class TestAPITimeouts(unittest.TestCase):
    """Test suite for API timeout handling in LLM Returns Chat Agent."""

    def setUp(self):
        """Set up test fixtures with mocked dependencies."""
        self.test_config = {
            'OPENAI_API_KEY': 'test_openai_key',
            'OPENAI_MODEL': 'gpt-4o',
            'SHOPIFY_ADMIN_TOKEN': 'test_shopify_token',
            'SHOPIFY_STORE_DOMAIN': 'test-store.myshopify.com'
        }
        
        # Create mock objects for dependencies
        with patch('llm_returns_chat_agent.OrderLookup'), \
             patch('llm_returns_chat_agent.PolicyChecker'), \
             patch('llm_returns_chat_agent.RefundProcessor'), \
             patch('llm_returns_chat_agent.ConversationLogger'), \
             patch('llm_returns_chat_agent.OpenAI'):
            
            self.agent = LLMReturnsChatAgent(self.test_config)

    @patch('llm_returns_chat_agent.OpenAI')
    def test_openai_api_timeout(self, mock_openai_class):
        """Test handling of OpenAI API timeouts."""
        # Configure mock to raise timeout
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = requests.exceptions.Timeout("OpenAI API timeout")
        
        # Create new agent with the failing client
        agent = LLMReturnsChatAgent(self.test_config)
        agent.client = mock_client
        
        # Test start_conversation with timeout
        response = agent.start_conversation()
        
        # Should return fallback greeting
        self.assertIsInstance(response, str)
        self.assertIn("help you with your return", response.lower())

    @patch('llm_returns_chat_agent.OpenAI')
    def test_openai_read_timeout(self, mock_openai_class):
        """Test handling of OpenAI API read timeouts."""
        # Configure mock to raise read timeout
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = requests.exceptions.ReadTimeout("Read timeout")
        
        # Create new agent with the failing client
        agent = LLMReturnsChatAgent(self.test_config)
        agent.client = mock_client
        
        # Test process_message with read timeout
        response = agent.process_message("I want to return my order")
        
        # Should return error message
        self.assertIsInstance(response, str)
        self.assertIn("technical difficulties", response.lower())

    def test_shopify_api_connection_timeout(self):
        """Test handling of Shopify API connection timeouts."""
        # Mock order lookup to simulate connection timeout
        self.agent.order_lookup.lookup_by_id.side_effect = requests.exceptions.ConnectTimeout("Shopify connection timeout")
        
        # Test function execution with connection timeout
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Function execution failed", result["error"])

    def test_shopify_api_read_timeout(self):
        """Test handling of Shopify API read timeouts."""
        # Mock order lookup to simulate read timeout
        self.agent.order_lookup.lookup_by_id.side_effect = requests.exceptions.ReadTimeout("Shopify read timeout")
        
        # Test function execution with read timeout
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Function execution failed", result["error"])

    def test_policy_service_timeout(self):
        """Test handling of policy service timeouts."""
        # Mock policy checker to simulate timeout
        self.agent.policy_checker.check_eligibility.side_effect = requests.exceptions.Timeout("Policy service timeout")
        
        # Test function execution with policy service timeout
        result = self.agent._execute_function("check_return_eligibility", {
            "order_date": "2024-01-01T00:00:00Z",
            "item_id": "111",
            "return_reason": "wrong_size"
        })
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Function execution failed", result["error"])

    def test_refund_service_timeout(self):
        """Test handling of refund service timeouts."""
        # Mock refund processor to simulate timeout
        self.agent.refund_processor.process_refund.side_effect = requests.exceptions.Timeout("Refund service timeout")
        
        # Test function execution with refund service timeout
        result = self.agent._execute_function("process_refund", {
            "order_id": "123456",
            "line_item_id": "111"
        })
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Function execution failed", result["error"])

    def test_multiple_timeout_scenarios(self):
        """Test handling of multiple concurrent timeout scenarios."""
        # Configure multiple services to timeout
        timeout_error = requests.exceptions.Timeout("Service timeout")
        
        self.agent.order_lookup.lookup_by_id.side_effect = timeout_error
        self.agent.order_lookup.lookup_by_email.side_effect = timeout_error
        self.agent.policy_checker.check_eligibility.side_effect = timeout_error
        self.agent.refund_processor.process_refund.side_effect = timeout_error
        
        # Test all functions with timeouts
        functions_to_test = [
            ("lookup_order_by_id", {"order_id": "123456"}),
            ("lookup_order_by_email", {"email": "test@example.com"}),
            ("check_return_eligibility", {
                "order_date": "2024-01-01T00:00:00Z",
                "item_id": "111",
                "return_reason": "wrong_size"
            }),
            ("process_refund", {
                "order_id": "123456",
                "line_item_id": "111"
            })
        ]
        
        for function_name, args in functions_to_test:
            with self.subTest(function=function_name):
                result = self.agent._execute_function(function_name, args)
                self.assertIsInstance(result, dict)
                self.assertIn("error", result)

    def test_timeout_with_retry_logic(self):
        """Test timeout handling with simulated retry logic."""
        # Simulate service that times out then succeeds
        call_count = 0
        
        def timeout_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise requests.exceptions.Timeout("Service timeout")
            return {"id": "123456", "email": "test@example.com", "status": "fulfilled"}
        
        self.agent.order_lookup.lookup_by_id.side_effect = timeout_then_success
        
        # First two calls should timeout
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result1)
        
        result2 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result2)
        
        # Third call should succeed
        result3 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertNotIn("error", result3)
        self.assertEqual(result3["id"], "123456")

    def test_variable_timeout_durations(self):
        """Test handling of timeouts with different durations."""
        # Test short timeouts (immediate)
        self.agent.order_lookup.lookup_by_id.side_effect = requests.exceptions.Timeout("Immediate timeout")
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result1)
        
        # Test longer timeouts (simulated with delay)
        def delayed_timeout(*args, **kwargs):
            time.sleep(0.1)  # Small delay to simulate processing time
            raise requests.exceptions.Timeout("Delayed timeout")
        
        self.agent.order_lookup.lookup_by_id.side_effect = delayed_timeout
        result2 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result2)

    def test_timeout_during_conversation_flow(self):
        """Test timeout handling during a multi-step conversation flow."""
        # Set up a scenario where lookup succeeds but policy check times out
        self.agent.order_lookup.lookup_by_id.return_value = {
            "id": "123456",
            "email": "test@example.com",
            "created_at": "2024-01-01T00:00:00Z"
        }
        self.agent.policy_checker.check_eligibility.side_effect = requests.exceptions.Timeout("Policy check timeout")
        
        # Test order lookup (should work)
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertNotIn("error", result1)
        self.assertEqual(result1["id"], "123456")
        
        # Test policy check (should timeout)
        result2 = self.agent._execute_function("check_return_eligibility", {
            "order_date": "2024-01-01T00:00:00Z",
            "item_id": "111",
            "return_reason": "wrong_size"
        })
        self.assertIn("error", result2)

    def test_cascading_timeout_failures(self):
        """Test handling of cascading timeout failures across services."""
        # Simulate scenario where timeouts cause cascading failures
        
        # First service times out
        self.agent.order_lookup.lookup_by_id.side_effect = requests.exceptions.Timeout("Order service timeout")
        
        # Dependent services also configured to timeout
        self.agent.policy_checker.check_eligibility.side_effect = requests.exceptions.Timeout("Policy service timeout")
        self.agent.refund_processor.process_refund.side_effect = requests.exceptions.Timeout("Refund service timeout")
        
        # Test that each service fails independently
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result1)
        
        result2 = self.agent._execute_function("check_return_eligibility", {
            "order_date": "2024-01-01T00:00:00Z",
            "item_id": "111",
            "return_reason": "wrong_size"
        })
        self.assertIn("error", result2)
        
        result3 = self.agent._execute_function("process_refund", {
            "order_id": "123456",
            "line_item_id": "111"
        })
        self.assertIn("error", result3)

    def test_partial_timeout_scenarios(self):
        """Test scenarios where some operations timeout but others succeed."""
        # Order lookup succeeds
        self.agent.order_lookup.lookup_by_id.return_value = {
            "id": "123456",
            "email": "test@example.com",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Email lookup times out
        self.agent.order_lookup.lookup_by_email.side_effect = requests.exceptions.Timeout("Email lookup timeout")
        
        # Policy check succeeds
        self.agent.policy_checker.check_eligibility.return_value = {
            "eligible": True,
            "reason": "Within return window"
        }
        
        # Refund processing times out
        self.agent.refund_processor.process_refund.side_effect = requests.exceptions.Timeout("Refund timeout")
        
        # Test each operation
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertNotIn("error", result1)  # Should succeed
        
        result2 = self.agent._execute_function("lookup_order_by_email", {"email": "test@example.com"})
        self.assertIn("error", result2)  # Should timeout
        
        result3 = self.agent._execute_function("check_return_eligibility", {
            "order_date": "2024-01-01T00:00:00Z",
            "item_id": "111",
            "return_reason": "wrong_size"
        })
        self.assertNotIn("error", result3)  # Should succeed
        
        result4 = self.agent._execute_function("process_refund", {
            "order_id": "123456",
            "line_item_id": "111"
        })
        self.assertIn("error", result4)  # Should timeout

    def test_timeout_error_message_clarity(self):
        """Test that timeout error messages are clear and actionable."""
        # Configure timeout with specific error message
        timeout_error = requests.exceptions.Timeout("Request timeout after 30 seconds")
        self.agent.order_lookup.lookup_by_id.side_effect = timeout_error
        
        # Test function execution
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Verify error response structure
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIsInstance(result["error"], str)
        self.assertTrue(len(result["error"]) > 0)
        
        # Error message should be informative
        error_msg = result["error"]
        self.assertIn("Function execution failed", error_msg)

    @patch('llm_returns_chat_agent.OpenAI')
    def test_openai_timeout_with_fallback_conversation(self, mock_openai_class):
        """Test conversation continuation when OpenAI times out but tools work."""
        # Configure OpenAI to timeout but tools to work
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = requests.exceptions.Timeout("OpenAI timeout")
        
        # Configure tools to work normally
        self.agent.order_lookup.lookup_by_id.return_value = {
            "id": "123456",
            "email": "test@example.com",
            "status": "fulfilled"
        }
        
        # Create new agent with failing OpenAI client
        agent = LLMReturnsChatAgent(self.test_config)
        agent.client = mock_client
        agent.order_lookup = self.agent.order_lookup
        
        # Test start_conversation (should use fallback)
        response = agent.start_conversation()
        self.assertIsInstance(response, str)
        self.assertIn("help you with your return", response.lower())
        
        # Test process_message (should return error due to OpenAI timeout)
        response = agent.process_message("I want to look up order 123456")
        self.assertIsInstance(response, str)
        self.assertIn("technical difficulties", response.lower())


if __name__ == '__main__':
    unittest.main(verbosity=2) 