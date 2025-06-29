import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Adjust import path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from returns_chat_agent import ReturnsChatAgent


class TestReturnsChatAgent:

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'SHOPIFY_ADMIN_TOKEN': 'test_token',
            'SHOPIFY_STORE_DOMAIN': 'test-store.myshopify.com'
        }
        
        # Mock all tools to isolate agent logic
        with patch('returns_chat_agent.OrderLookup') as mock_order_lookup, \
             patch('returns_chat_agent.PolicyChecker') as mock_policy_checker, \
             patch('returns_chat_agent.RefundProcessor') as mock_refund_processor, \
             patch('returns_chat_agent.ConversationLogger') as mock_logger:
            
            self.agent = ReturnsChatAgent(self.config)
            self.mock_order_lookup = mock_order_lookup.return_value
            self.mock_policy_checker = mock_policy_checker.return_value
            self.mock_refund_processor = mock_refund_processor.return_value
            self.mock_logger = mock_logger.return_value

    def test_initialization_valid_config(self):
        """Test successful initialization with valid config."""
        assert self.agent.current_state == "greeting"
        assert self.agent.conversation_id is None
        assert self.agent.context == {}

    def test_initialization_missing_config(self):
        """Test initialization fails with missing config."""
        with pytest.raises(ValueError, match="Config missing required key"):
            ReturnsChatAgent({})

    def test_start_conversation(self):
        """Test starting a new conversation."""
        greeting = self.agent.start_conversation()
        
        assert "returns assistant" in greeting.lower()
        assert self.agent.conversation_id is not None
        assert self.agent.current_state == "greeting"
        self.mock_logger.log_interaction.assert_called_once()

    def test_handle_greeting_with_order_number(self):
        """Test greeting with order number extraction."""
        self.agent.start_conversation()
        
        # Mock successful order lookup
        mock_order = {
            "id": "gid://shopify/Order/123456",
            "lineItems": {
                "edges": [
                    {"node": {"id": "item_1", "title": "Test Item", "quantity": 1}}
                ]
            }
        }
        self.mock_order_lookup.lookup_by_id.return_value = mock_order
        
        response = self.agent.process_message("I want to return order #1234")
        
        assert "found your order" in response.lower()
        assert self.agent.current_state == "item_selection"
        assert "1234" in self.agent.context['order_id']
        self.mock_order_lookup.lookup_by_id.assert_called_with("1234")

    def test_handle_greeting_with_email(self):
        """Test greeting with email extraction."""
        self.agent.start_conversation()
        
        # Mock successful order lookup by email
        mock_orders = {
            "orders": [{
                "id": "gid://shopify/Order/123456",
                "orderNumber": "1234",
                "lineItems": {
                    "edges": [
                        {"node": {"id": "item_1", "title": "Test Item", "quantity": 1}}
                    ]
                }
            }]
        }
        self.mock_order_lookup.lookup_by_email.return_value = mock_orders
        
        response = self.agent.process_message("My email is test@example.com")
        
        assert "found your order" in response.lower()
        assert self.agent.current_state == "item_selection"
        assert "test@example.com" in self.agent.context['email']

    def test_handle_order_not_found(self):
        """Test handling when order is not found."""
        self.agent.start_conversation()
        
        # Mock order not found
        self.mock_order_lookup.lookup_by_id.return_value = {"error": "Order not found"}
        
        response = self.agent.process_message("Order #9999")
        
        assert "couldn't find an order" in response.lower()
        assert self.agent.current_state == "order_lookup"

    def test_handle_item_selection(self):
        """Test item selection from order."""
        self.agent.start_conversation()
        self.agent.current_state = "item_selection"
        self.agent.context['line_items'] = [
            {"id": "item_1", "title": "Test Item 1", "quantity": 1},
            {"id": "item_2", "title": "Test Item 2", "quantity": 2}
        ]
        
        response = self.agent.process_message("1")
        
        assert "test item 1" in response.lower()
        assert "reason for your return" in response.lower()
        assert self.agent.current_state == "reason_collection"
        assert self.agent.context['selected_item']['id'] == "item_1"

    def test_handle_invalid_item_selection(self):
        """Test invalid item selection."""
        self.agent.start_conversation()
        self.agent.current_state = "item_selection"
        self.agent.context['line_items'] = [
            {"id": "item_1", "title": "Test Item", "quantity": 1}
        ]
        
        response = self.agent.process_message("5")
        
        assert "select a number between" in response.lower()
        assert self.agent.current_state == "item_selection"

    def test_handle_reason_collection(self):
        """Test return reason collection."""
        self.agent.start_conversation()
        self.agent.current_state = "reason_collection"
        self.agent.context.update({
            'order': {'createdAt': '2024-01-01T10:00:00Z'},
            'selected_item': {'id': 'item_1', 'title': 'Test Item'},
        })
        
        # Mock policy approval
        self.mock_policy_checker.check_eligibility.return_value = {
            'decision': 'approve',
            'reason': 'Return approved'
        }
        
        response = self.agent.process_message("2")  # Defective
        
        assert "approved" in response.lower()
        assert "process the refund" in response.lower()
        assert self.agent.current_state == "confirmation"
        assert self.agent.context['return_reason'] == "defective"

    def test_handle_policy_denial(self):
        """Test policy denial scenario."""
        self.agent.start_conversation()
        self.agent.current_state = "reason_collection"
        self.agent.context.update({
            'order': {'createdAt': '2023-01-01T10:00:00Z'},  # Old order
            'selected_item': {'id': 'item_1', 'title': 'Test Item'},
        })
        
        # Mock policy denial
        self.mock_policy_checker.check_eligibility.return_value = {
            'decision': 'deny',
            'reason': 'Return window expired'
        }
        
        response = self.agent.process_message("1")  # Wrong size
        
        assert "cannot be processed" in response.lower()
        assert "return window expired" in response.lower()
        assert self.agent.current_state == "greeting"

    def test_handle_confirmation_yes(self):
        """Test confirmation with yes response."""
        self.agent.start_conversation()
        self.agent.current_state = "confirmation"
        self.agent.context.update({
            'order': {'id': 'order_123'},
            'selected_item': {'id': 'item_1'},
            'return_reason': 'defective'
        })
        
        # Mock successful refund
        self.mock_refund_processor.process_refund.return_value = {
            'success': True,
            'refund_id': 'refund_123'
        }
        
        response = self.agent.process_message("yes")
        
        assert "processed successfully" in response.lower()
        assert "refund_123" in response
        assert self.agent.current_state == "greeting"
        assert self.agent.context == {}  # Context cleared

    def test_handle_confirmation_no(self):
        """Test confirmation with no response."""
        self.agent.start_conversation()
        self.agent.current_state = "confirmation"
        
        response = self.agent.process_message("no")
        
        assert "cancelled" in response.lower()
        assert self.agent.current_state == "greeting"

    def test_handle_refund_failure(self):
        """Test refund processing failure."""
        self.agent.start_conversation()
        self.agent.current_state = "confirmation"
        self.agent.context.update({
            'order': {'id': 'order_123'},
            'selected_item': {'id': 'item_1'},
            'return_reason': 'defective'
        })
        
        # Mock refund failure
        self.mock_refund_processor.process_refund.return_value = {
            'error': 'Payment gateway error'
        }
        
        response = self.agent.process_message("yes")
        
        assert "issue processing" in response.lower()
        assert "payment gateway error" in response.lower()
        assert self.agent.current_state == "greeting"

    def test_conversation_logging(self):
        """Test that all interactions are logged."""
        self.agent.start_conversation()
        self.agent.process_message("Hello")
        
        # Should have logged greeting and user message
        assert self.mock_logger.log_interaction.call_count >= 2

    def test_get_conversation_summary(self):
        """Test conversation summary retrieval."""
        self.agent.start_conversation()
        
        # Mock summary
        self.mock_logger.summarize_conversation.return_value = {
            "conversation_id": self.agent.conversation_id,
            "messages": {"total_interactions": 1}
        }
        
        summary = self.agent.get_conversation_summary()
        
        assert summary["conversation_id"] == self.agent.conversation_id
        self.mock_logger.summarize_conversation.assert_called_with(self.agent.conversation_id)

    def test_get_conversation_summary_no_active_conversation(self):
        """Test summary when no conversation is active."""
        summary = self.agent.get_conversation_summary()
        assert "error" in summary
        assert "No active conversation" in summary["error"]

    def test_fallback_state_handling(self):
        """Test fallback for unknown states."""
        self.agent.start_conversation()
        self.agent.current_state = "unknown_state"
        
        response = self.agent.process_message("test")
        
        assert "not sure how to help" in response.lower()
        assert self.agent.current_state == "greeting"

    def test_no_line_items_in_order(self):
        """Test handling order with no returnable items."""
        self.agent.start_conversation()
        
        # Mock order with no line items
        mock_order = {
            "id": "gid://shopify/Order/123456",
            "lineItems": {"edges": []}
        }
        self.mock_order_lookup.lookup_by_id.return_value = mock_order
        
        response = self.agent.process_message("Order #1234")
        
        assert "doesn't have any items" in response.lower()
        assert self.agent.current_state == "greeting" 