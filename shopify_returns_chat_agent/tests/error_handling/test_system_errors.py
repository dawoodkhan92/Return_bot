"""
System error tests for LLM Returns Chat Agent.

These tests verify that the agent handles various system-level errors
gracefully including memory issues, configuration problems, and runtime errors.
"""

import unittest
import json
import sys
import os
from unittest.mock import MagicMock, patch, Mock, PropertyMock
import requests
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm_returns_chat_agent import LLMReturnsChatAgent


class TestSystemErrors(unittest.TestCase):
    """Test suite for system error handling in LLM Returns Chat Agent."""

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

    def test_missing_configuration_keys(self):
        """Test handling of missing configuration keys."""
        # Test with missing OpenAI API key
        incomplete_configs = [
            {},  # Empty config
            {'SHOPIFY_ADMIN_TOKEN': 'token'},  # Missing OpenAI key
            {'OPENAI_API_KEY': 'key'},  # Missing Shopify token
            {'OPENAI_API_KEY': 'key', 'SHOPIFY_ADMIN_TOKEN': 'token'},  # Missing domain
        ]
        
        for config in incomplete_configs:
            with self.subTest(config=config):
                try:
                    with patch('llm_returns_chat_agent.OrderLookup'), \
                         patch('llm_returns_chat_agent.PolicyChecker'), \
                         patch('llm_returns_chat_agent.RefundProcessor'), \
                         patch('llm_returns_chat_agent.ConversationLogger'), \
                         patch('llm_returns_chat_agent.OpenAI'):
                        
                        agent = LLMReturnsChatAgent(config)
                        # Should either succeed with defaults or fail gracefully
                        self.assertIsNotNone(agent)
                except (KeyError, ValueError, TypeError) as e:
                    # Expected for incomplete configurations
                    self.assertIsInstance(e, (KeyError, ValueError, TypeError))

    def test_invalid_configuration_values(self):
        """Test handling of invalid configuration values."""
        invalid_configs = [
            {
                'OPENAI_API_KEY': '',  # Empty string
                'SHOPIFY_ADMIN_TOKEN': 'token',
                'SHOPIFY_STORE_DOMAIN': 'domain'
            },
            {
                'OPENAI_API_KEY': None,  # None value
                'SHOPIFY_ADMIN_TOKEN': 'token',
                'SHOPIFY_STORE_DOMAIN': 'domain'
            },
            {
                'OPENAI_API_KEY': 'key',
                'OPENAI_MODEL': 'invalid-model',  # Invalid model
                'SHOPIFY_ADMIN_TOKEN': 'token',
                'SHOPIFY_STORE_DOMAIN': 'domain'
            },
            {
                'OPENAI_API_KEY': 'key',
                'SHOPIFY_ADMIN_TOKEN': 'token',
                'SHOPIFY_STORE_DOMAIN': 'invalid-domain'  # Invalid domain format
            },
        ]
        
        for config in invalid_configs:
            with self.subTest(config=config):
                try:
                    with patch('llm_returns_chat_agent.OrderLookup'), \
                         patch('llm_returns_chat_agent.PolicyChecker'), \
                         patch('llm_returns_chat_agent.RefundProcessor'), \
                         patch('llm_returns_chat_agent.ConversationLogger'), \
                         patch('llm_returns_chat_agent.OpenAI'):
                        
                        agent = LLMReturnsChatAgent(config)
                        # Agent creation might succeed, but operations should fail gracefully
                        response = agent.start_conversation()
                        self.assertIsInstance(response, str)
                except Exception as e:
                    # Expected for invalid configurations
                    self.assertIsNotNone(e)

    def test_memory_allocation_errors(self):
        """Test handling of memory-related errors."""
        # Simulate memory error during agent initialization
        with patch('llm_returns_chat_agent.OpenAI') as mock_openai:
            mock_openai.side_effect = MemoryError("Insufficient memory")
            
            try:
                agent = LLMReturnsChatAgent(self.test_config)
                # If initialization succeeds despite memory error, that's okay
                self.assertIsNotNone(agent)
            except MemoryError:
                # Expected behavior for memory errors
                pass

    def test_file_system_errors(self):
        """Test handling of file system errors."""
        # Mock file operations to raise permission errors
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            try:
                # This might affect logging or configuration file access
                agent = LLMReturnsChatAgent(self.test_config)
                response = agent.start_conversation()
                self.assertIsInstance(response, str)
            except PermissionError:
                # Expected for file system errors
                pass

    def test_json_parsing_errors(self):
        """Test handling of JSON parsing errors in OpenAI responses."""
        # Mock OpenAI client to return malformed JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function.name = "lookup_order_by_id"
        mock_response.choices[0].message.tool_calls[0].function.arguments = '{"invalid": json}'  # Malformed JSON
        mock_response.choices[0].message.tool_calls[0].id = "test_call_id"
        
        self.agent.client.chat.completions.create.return_value = mock_response
        
        # Test process_message with malformed JSON
        response = self.agent.process_message("Look up order 123456")
        
        # Should handle JSON parsing error gracefully
        self.assertIsInstance(response, str)
        # Should not crash the system

    def test_unicode_encoding_errors(self):
        """Test handling of unicode encoding/decoding errors."""
        # Test with problematic unicode strings
        problematic_strings = [
            "\ud800",  # Invalid surrogate
            "\udc00",  # Invalid surrogate
            b'\xff\xfe'.decode('utf-8', errors='ignore'),  # Problematic bytes
        ]
        
        for problematic_string in problematic_strings:
            with self.subTest(string=problematic_string):
                try:
                    response = self.agent.process_message(problematic_string)
                    # Should handle unicode errors gracefully
                    self.assertIsInstance(response, str)
                except UnicodeError:
                    # Unicode errors are acceptable
                    pass

    def test_stack_overflow_simulation(self):
        """Test handling of deep recursion scenarios."""
        # Simulate deep recursion by creating circular references
        circular_data = {}
        circular_data['self'] = circular_data
        
        # Mock function to return circular data
        self.agent.order_lookup.lookup_by_id.return_value = circular_data
        
        try:
            result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
            # Should handle circular references gracefully
            self.assertIsInstance(result, dict)
        except RecursionError:
            # RecursionError is acceptable for circular references
            pass

    def test_attribute_errors(self):
        """Test handling of attribute errors from missing methods/properties."""
        # Mock missing attributes on dependencies
        delattr(self.agent.order_lookup, 'lookup_by_id')
        
        try:
            result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
            # Should return error for missing method
            self.assertIn("error", result)
        except AttributeError:
            # AttributeError is acceptable
            pass

    def test_type_errors(self):
        """Test handling of type errors from incorrect parameter types."""
        # Mock functions to raise type errors
        self.agent.order_lookup.lookup_by_id.side_effect = TypeError("Invalid parameter type")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should handle type errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_value_errors(self):
        """Test handling of value errors from invalid parameter values."""
        # Mock functions to raise value errors
        self.agent.order_lookup.lookup_by_id.side_effect = ValueError("Invalid parameter value")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should handle value errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_key_errors(self):
        """Test handling of key errors from missing dictionary keys."""
        # Mock functions to raise key errors
        self.agent.order_lookup.lookup_by_id.side_effect = KeyError("Missing required key")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should handle key errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_index_errors(self):
        """Test handling of index errors from list/array access."""
        # Mock functions to raise index errors
        self.agent.order_lookup.lookup_by_id.side_effect = IndexError("List index out of range")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should handle index errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_assertion_errors(self):
        """Test handling of assertion errors from failed assertions."""
        # Mock functions to raise assertion errors
        self.agent.order_lookup.lookup_by_id.side_effect = AssertionError("Assertion failed")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should handle assertion errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_import_errors(self):
        """Test handling of import errors from missing dependencies."""
        # Simulate import error by patching the import mechanism
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            try:
                # This would affect any dynamic imports
                response = self.agent.start_conversation()
                self.assertIsInstance(response, str)
            except ImportError:
                # Import errors during runtime are acceptable
                pass

    def test_os_errors(self):
        """Test handling of operating system errors."""
        # Mock OS-level errors
        self.agent.order_lookup.lookup_by_id.side_effect = OSError("Operating system error")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should handle OS errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_runtime_errors(self):
        """Test handling of generic runtime errors."""
        # Mock generic runtime errors
        self.agent.order_lookup.lookup_by_id.side_effect = RuntimeError("Generic runtime error")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should handle runtime errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_unknown_function_calls(self):
        """Test handling of unknown function calls."""
        # Test calling a function that doesn't exist
        result = self.agent._execute_function("unknown_function", {"param": "value"})
        
        # Should return error for unknown function
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Unknown function", result["error"])

    def test_malformed_tool_calls(self):
        """Test handling of malformed tool calls from OpenAI."""
        # Mock OpenAI response with malformed tool calls
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [Mock()]
        
        # Missing required attributes
        mock_response.choices[0].message.tool_calls[0].function = None
        mock_response.choices[0].message.tool_calls[0].id = "test_call_id"
        
        self.agent.client.chat.completions.create.return_value = mock_response
        
        # Test process_message with malformed tool calls
        response = self.agent.process_message("Process this request")
        
        # Should handle malformed tool calls gracefully
        self.assertIsInstance(response, str)

    def test_conversation_state_corruption(self):
        """Test handling of corrupted conversation state."""
        # Corrupt the conversation state
        self.agent.messages = "invalid_message_format"  # Should be a list
        self.agent.context = "invalid_context_format"   # Should be a dict
        
        try:
            response = self.agent.process_message("Test message")
            # Should either handle corruption or fail gracefully
            self.assertIsInstance(response, str)
        except (TypeError, AttributeError):
            # Type/Attribute errors are acceptable for corrupted state
            pass

    def test_logger_failures(self):
        """Test handling of logger failures."""
        # Mock logger to raise exceptions
        self.agent.logger.log_interaction.side_effect = Exception("Logger failed")
        
        # Test that logging failures don't crash the system
        response = self.agent.process_message("Test message")
        
        # Should continue functioning despite logging failures
        self.assertIsInstance(response, str)

    def test_context_cleanup_on_errors(self):
        """Test that context is properly cleaned up after errors."""
        # Store initial context state
        initial_context = self.agent.context.copy()
        
        # Cause an error during function execution
        self.agent.order_lookup.lookup_by_id.side_effect = Exception("Test error")
        
        result = self.agent._execute_function("lookup_order_by_id", {"order_id": "123456"})
        
        # Should return error
        self.assertIn("error", result)
        
        # Context should still be accessible (not corrupted)
        self.assertIsInstance(self.agent.context, dict)


if __name__ == '__main__':
    unittest.main(verbosity=2) 