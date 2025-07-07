"""
Network failure tests for LLM Returns Chat Agent.

These tests verify that the agent handles various network-related failures
gracefully and provides appropriate fallback responses.
"""

import unittest
import json
import sys
import os
from unittest.mock import MagicMock, patch, Mock
import requests
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm_returns_chat_agent import LLMReturnsChatAgent


class TestNetworkFailures(unittest.TestCase):
    """Test suite for network failure handling in LLM Returns Chat Agent."""

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
    def test_openai_connection_timeout(self, mock_openai_class):
        """Test handling of OpenAI API connection timeouts."""
        # Configure mock to raise connection timeout
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = requests.exceptions.ConnectTimeout("Connection timeout")
        
        # Create new agent with the failing client
        agent = LLMReturnsChatAgent(self.test_config)
        agent.client = mock_client
        
        # Test start_conversation with timeout
        response = agent.start_conversation()
        
        # Should return fallback greeting
        self.assertIsInstance(response, str)
        self.assertIn("help you with your return", response.lower())
        # Should not contain OpenAI-generated content
        self.assertNotIn("technical difficulties", response.lower())

    @patch('llm_returns_chat_agent.OpenAI')
    def test_openai_connection_error(self, mock_openai_class):
        """Test handling of OpenAI API connection errors."""
        # Configure mock to raise connection error
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Create new agent with the failing client
        agent = LLMReturnsChatAgent(self.test_config)
        agent.client = mock_client
        
        # Test process_message with connection error
        response = agent.process_message("I want to return my order")
        
        # Should return error message
        self.assertIsInstance(response, str)
        self.assertIn("technical difficulties", response.lower())

    @patch('llm_returns_chat_agent.OpenAI')
    def test_openai_http_error(self, mock_openai_class):
        """Test handling of OpenAI API HTTP errors."""
        # Configure mock to raise HTTP error
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = requests.exceptions.HTTPError("HTTP 500 Error")
        
        # Create new agent with the failing client
        agent = LLMReturnsChatAgent(self.test_config)
        agent.client = mock_client
        
        # Test process_message with HTTP error
        response = agent.process_message("What's my order status?")
        
        # Should return error message
        self.assertIsInstance(response, str)
        self.assertIn("technical difficulties", response.lower())

    def test_shopify_api_connection_failure(self):
        """Test handling of Shopify API connection failures."""
        # Mock order lookup to simulate connection failure
        self.agent.order_lookup.lookup_by_id.side_effect = requests.exceptions.ConnectionError("Shopify API unreachable")
        
        # Test function execution with connection failure
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Function execution failed", result["error"])

    def test_shopify_api_timeout(self):
        """Test handling of Shopify API timeouts."""
        # Mock order lookup to simulate timeout
        self.agent.order_lookup.lookup_by_id.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Test function execution with timeout
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Function execution failed", result["error"])

    def test_shopify_api_http_errors(self):
        """Test handling of various Shopify API HTTP errors."""
        http_errors = [
            requests.exceptions.HTTPError("400 Bad Request"),
            requests.exceptions.HTTPError("401 Unauthorized"),
            requests.exceptions.HTTPError("403 Forbidden"),
            requests.exceptions.HTTPError("404 Not Found"),
            requests.exceptions.HTTPError("429 Rate Limited"),
            requests.exceptions.HTTPError("500 Internal Server Error"),
            requests.exceptions.HTTPError("502 Bad Gateway"),
            requests.exceptions.HTTPError("503 Service Unavailable"),
        ]
        
        for error in http_errors:
            with self.subTest(error=error):
                # Mock order lookup to simulate HTTP error
                self.agent.order_lookup.lookup_by_id.side_effect = error
                
                # Test function execution with HTTP error
                result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
                
                # Should return error response
                self.assertIsInstance(result, dict)
                self.assertIn("error", result)

    def test_network_intermittent_failures(self):
        """Test handling of intermittent network failures."""
        # Simulate intermittent failures (fail, then succeed)
        call_count = 0
        
        def side_effect_intermittent(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise requests.exceptions.ConnectionError("Intermittent failure")
            return {"id": "123456", "email": "test@example.com", "status": "fulfilled"}
        
        self.agent.order_lookup.lookup_by_id.side_effect = side_effect_intermittent
        
        # First call should fail
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result1)
        
        # Reset for second call
        call_count = 0
        self.agent.order_lookup.lookup_by_id.side_effect = side_effect_intermittent
        
        # Second call should succeed
        result2 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertNotIn("error", result2)
        self.assertEqual(result2["id"], "123456")

    def test_partial_network_failures(self):
        """Test scenarios where some services work but others fail."""
        # Order lookup works but policy checker fails
        self.agent.order_lookup.lookup_by_id.return_value = {
            "id": "123456",
            "email": "test@example.com",
            "created_at": "2024-01-01T00:00:00Z"
        }
        self.agent.policy_checker.check_eligibility.side_effect = requests.exceptions.ConnectionError("Policy service down")
        
        # Test order lookup (should work)
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertNotIn("error", result1)
        self.assertEqual(result1["id"], "123456")
        
        # Test policy check (should fail)
        result2 = self.agent._execute_function("check_return_eligibility", {
            "order_date": "2024-01-01T00:00:00Z",
            "item_id": "111",
            "return_reason": "wrong_size"
        })
        self.assertIn("error", result2)

    def test_dns_resolution_failures(self):
        """Test handling of DNS resolution failures."""
        # Mock DNS resolution failure
        dns_error = requests.exceptions.ConnectionError("Name or service not known")
        
        self.agent.order_lookup.lookup_by_id.side_effect = dns_error
        self.agent.order_lookup.lookup_by_email.side_effect = dns_error
        self.agent.policy_checker.check_eligibility.side_effect = dns_error
        self.agent.refund_processor.process_refund.side_effect = dns_error
        
        # Test all functions with DNS failure
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

    def test_ssl_certificate_errors(self):
        """Test handling of SSL certificate errors."""
        # Mock SSL certificate error
        ssl_error = requests.exceptions.SSLError("SSL certificate verification failed")
        
        self.agent.order_lookup.lookup_by_id.side_effect = ssl_error
        
        # Test function execution with SSL error
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    @patch('llm_returns_chat_agent.OpenAI')
    def test_complete_network_isolation(self, mock_openai_class):
        """Test agent behavior when completely isolated from network."""
        # Configure all network calls to fail
        network_error = requests.exceptions.ConnectionError("No network connection")
        
        # Mock OpenAI client to fail
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = network_error
        
        # Mock all agent tools to fail
        self.agent.order_lookup.lookup_by_id.side_effect = network_error
        self.agent.order_lookup.lookup_by_email.side_effect = network_error
        self.agent.policy_checker.check_eligibility.side_effect = network_error
        self.agent.refund_processor.process_refund.side_effect = network_error
        
        # Create new agent with failing client
        agent = LLMReturnsChatAgent(self.test_config)
        agent.client = mock_client
        agent.order_lookup = self.agent.order_lookup
        agent.policy_checker = self.agent.policy_checker
        agent.refund_processor = self.agent.refund_processor
        
        # Test start_conversation (should use fallback)
        response = agent.start_conversation()
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        
        # Test process_message (should return error)
        response = agent.process_message("I want to return my order")
        self.assertIsInstance(response, str)
        self.assertIn("technical difficulties", response.lower())

    def test_network_recovery_scenarios(self):
        """Test agent behavior during network recovery."""
        # Simulate network coming back online
        call_count = 0
        
        def network_recovery_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise requests.exceptions.ConnectionError("Network still down")
            # Network is back up
            return {"id": "123456", "email": "test@example.com", "status": "fulfilled"}
        
        self.agent.order_lookup.lookup_by_id.side_effect = network_recovery_side_effect
        
        # First two calls should fail
        result1 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result1)
        
        result2 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertIn("error", result2)
        
        # Third call should succeed (network recovered)
        result3 = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        self.assertNotIn("error", result3)
        self.assertEqual(result3["id"], "123456")


if __name__ == '__main__':
    unittest.main(verbosity=2) 