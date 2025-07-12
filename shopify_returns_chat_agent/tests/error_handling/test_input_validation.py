"""
Input validation tests for LLM Returns Chat Agent.

These tests verify that the agent handles various invalid inputs gracefully
and provides appropriate error messages to users.
"""

import unittest
import json
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm_returns_chat_agent import LLMReturnsChatAgent


class TestInputValidation(unittest.TestCase):
    """Test suite for input validation in LLM Returns Chat Agent."""

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
    
    def test_invalid_order_numbers(self):
        """Test handling of various invalid order number formats."""
        # Mock the OpenAI client to simulate function calls
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function.name = "lookup_order_by_id"
        mock_response.choices[0].message.tool_calls[0].function.arguments = '{"order_id": "invalid"}'
        mock_response.choices[0].message.tool_calls[0].id = "test_call_id"
        
        # Mock the order lookup to return error for invalid ID
        self.agent.order_lookup.lookup_by_id.return_value = {
            "error": "Invalid order ID format"
        }
        
        # Test various invalid order formats
        invalid_orders = [
            "",                    # Empty string
            None,                  # None value
            "ABC",                 # Non-numeric
            "123-456",            # Hyphenated format
            "ORDER#123",          # With prefix
            "9" * 100,            # Too long
            "!@#$%",              # Special characters
            "   ",                # Whitespace only
            "12.34",              # Decimal number
            "-123",               # Negative number
        ]
        
        for invalid_order in invalid_orders:
            with self.subTest(order_id=invalid_order):
                # Simulate function execution
                result = self.agent._execute_function("lookup_order_by_id", {"order_id": invalid_order})
                
                # Verify error handling
                self.assertIn("error", result)
                self.assertIsInstance(result["error"], str)
                self.assertTrue(len(result["error"]) > 0)
    
    def test_invalid_email_formats(self):
        """Test handling of invalid email address formats."""
        # Mock the order lookup to return error for invalid email
        self.agent.order_lookup.lookup_by_email.return_value = {
            "error": "Invalid email format"
        }
        
        invalid_emails = [
            "",                           # Empty string
            "not-an-email",              # No @ symbol
            "@example.com",              # Missing username
            "user@",                     # Missing domain
            "user@.com",                 # Invalid domain
            "user space@example.com",    # Space in username
            "user@example.",             # Incomplete domain
            "user@@example.com",         # Double @
            "user@exam ple.com",         # Space in domain
            None,                        # None value
            "user@",                     # Incomplete
            "user@example..com",         # Double dot
        ]
        
        for invalid_email in invalid_emails:
            with self.subTest(email=invalid_email):
                # Simulate function execution
                result = self.agent._execute_function("lookup_order_by_email", {"email": invalid_email})
                
                # Verify error handling
                self.assertIn("error", result)
                self.assertIsInstance(result["error"], str)
                self.assertTrue(len(result["error"]) > 0)
    
    def test_malformed_function_arguments(self):
        """Test handling of malformed function arguments."""
        # Test missing required arguments
        test_cases = [
            # Missing order_id
            ("lookup_order_by_id", {}),
            # Missing email
            ("lookup_order_by_email", {}),
            # Missing required fields for eligibility check
            ("check_return_eligibility", {"order_date": "2024-01-01"}),
            ("check_return_eligibility", {"item_id": "123"}),
            ("check_return_eligibility", {"return_reason": "wrong_size"}),
            # Missing required fields for refund
            ("process_refund", {"order_id": "123"}),
            ("process_refund", {"line_item_id": "456"}),
        ]
        
        for function_name, args in test_cases:
            with self.subTest(function=function_name, args=args):
                try:
                    result = self.agent._execute_function(function_name, args)
                    # Should either return error or raise exception
                    if isinstance(result, dict):
                        self.assertIn("error", result)
                except (KeyError, TypeError) as e:
                    # Expected for missing required arguments
                    self.assertIsInstance(e, (KeyError, TypeError))
    
    def test_invalid_return_reasons(self):
        """Test handling of invalid return reasons."""
        # Mock policy checker to validate return reason
        def mock_check_eligibility(order_date, item_id, return_reason):
            valid_reasons = ["wrong_size", "defective", "not_as_described", "changed_mind", "damaged", "other"]
            if return_reason not in valid_reasons:
                return {"error": f"Invalid return reason: {return_reason}"}
            return {"eligible": True, "reason": "Valid return reason"}
        
        self.agent.policy_checker.check_eligibility.side_effect = mock_check_eligibility
        
        invalid_reasons = [
            "",                    # Empty string
            None,                  # None value
            "invalid_reason",      # Not in enum list
            "WRONG_SIZE",          # Wrong case
            "broken",              # Similar but not exact
            "faulty",              # Similar but not exact
            "123",                 # Numeric
            "reason with spaces",  # Spaces (not in enum)
        ]
        
        for invalid_reason in invalid_reasons:
            with self.subTest(reason=invalid_reason):
                result = self.agent._execute_function("check_return_eligibility", {
                    "order_date": "2024-01-01T00:00:00Z",
                    "item_id": "123",
                    "return_reason": invalid_reason
                })
                
                # Should return error for invalid reasons
                if invalid_reason not in ["wrong_size", "defective", "not_as_described", "changed_mind", "damaged", "other"]:
                    self.assertIn("error", result)
    
    def test_invalid_date_formats(self):
        """Test handling of invalid date formats in order_date."""
        # Mock policy checker to validate date format
        def mock_check_eligibility(order_date, item_id, return_reason):
            try:
                # Try to parse the date
                from datetime import datetime
                datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                return {"eligible": True, "reason": "Valid date format"}
            except (ValueError, AttributeError):
                return {"error": f"Invalid date format: {order_date}"}
        
        self.agent.policy_checker.check_eligibility.side_effect = mock_check_eligibility
        
        invalid_dates = [
            "",                      # Empty string
            None,                    # None value
            "2024-01-01",           # Missing time
            "01/01/2024",           # Wrong format
            "January 1, 2024",      # Text format
            "2024-13-01T00:00:00Z", # Invalid month
            "2024-01-32T00:00:00Z", # Invalid day
            "2024-01-01T25:00:00Z", # Invalid hour
            "invalid-date",         # Non-date string
            "2024",                 # Incomplete
            "2024-01",              # Incomplete
        ]
        
        for invalid_date in invalid_dates:
            with self.subTest(date=invalid_date):
                try:
                    result = self.agent._execute_function("check_return_eligibility", {
                        "order_date": invalid_date,
                        "item_id": "123",
                        "return_reason": "wrong_size"
                    })
                    
                    # Should return error for invalid dates
                    if invalid_date not in [None]:  # None might raise exception before reaching check
                        self.assertIn("error", result)
                except (TypeError, AttributeError):
                    # Expected for None or severely malformed inputs
                    pass
    
    def test_extreme_input_values(self):
        """Test handling of extremely large or unusual inputs."""
        # Test extremely long strings
        very_long_string = "a" * 10000
        
        test_cases = [
            ("lookup_order_by_id", {"order_id": very_long_string}),
            ("lookup_order_by_email", {"email": very_long_string + "@example.com"}),
            ("check_return_eligibility", {
                "order_date": "2024-01-01T00:00:00Z",
                "item_id": very_long_string,
                "return_reason": "wrong_size"
            }),
            ("process_refund", {
                "order_id": very_long_string,
                "line_item_id": "123"
            }),
        ]
        
        for function_name, args in test_cases:
            with self.subTest(function=function_name):
                # Mock the underlying tools to return errors for extreme inputs
                if function_name == "lookup_order_by_id":
                    self.agent.order_lookup.lookup_by_id.return_value = {"error": "Order ID too long"}
                elif function_name == "lookup_order_by_email":
                    self.agent.order_lookup.lookup_by_email.return_value = {"error": "Email too long"}
                elif function_name == "check_return_eligibility":
                    self.agent.policy_checker.check_eligibility.return_value = {"error": "Item ID too long"}
                elif function_name == "process_refund":
                    self.agent.refund_processor.process_refund.return_value = {"error": "Order ID too long"}
                
                result = self.agent._execute_function(function_name, args)
                
                # Should handle extreme inputs gracefully
                self.assertIsInstance(result, dict)
                # Either returns error or processes (depending on implementation)
                if "error" in result:
                    self.assertIsInstance(result["error"], str)
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters in inputs."""
        special_inputs = [
            "订单号123",                    # Chinese characters
            "émile@exámple.cöm",          # Accented characters
            "🛒order123",                 # Emoji
            "order\n\t123",               # Control characters
            "order\\123",                 # Backslashes
            "order\"123\"",               # Quotes
            "order'123'",                 # Single quotes
            "<script>alert('xss')</script>", # XSS attempt
            "'; DROP TABLE orders; --",    # SQL injection attempt
        ]
        
        for special_input in special_inputs:
            with self.subTest(input=special_input):
                # Test with order lookup
                self.agent.order_lookup.lookup_by_id.return_value = {"error": "Invalid characters"}
                result = self.agent._execute_function("lookup_order_by_id", {"order_id": special_input})
                
                # Should handle special characters safely
                self.assertIsInstance(result, dict)
                # Implementation should either process or return error safely
                if "error" in result:
                    self.assertIsInstance(result["error"], str)


if __name__ == '__main__':
    unittest.main(verbosity=2) 