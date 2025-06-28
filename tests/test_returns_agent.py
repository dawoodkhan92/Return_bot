import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.returns_agent import ReturnsAgent

class TestReturnsAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = ReturnsAgent(return_window_days=30)
        
        # Sample webhook data
        self.sample_webhook = {
            'order_id': '12345',
            'amount': 99.99,
            'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
            'line_items': [{'id': 'item_123'}],
            'reason': 'defective',
            'email': 'customer@example.com'
        }
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertIsNotNone(self.agent.policy_checker)
        self.assertIsNotNone(self.agent.action_logger)
        self.assertIsNotNone(self.agent.refund_processor)
    
    @patch('agents.returns_agent.PolicyChecker')
    @patch('agents.returns_agent.ActionLogger')
    @patch('agents.returns_agent.RefundProcessor')
    def test_process_refund_webhook_approve(self, mock_refund, mock_logger, mock_policy):
        """Test webhook processing with approve decision"""
        # Mock policy checker to return approve
        mock_policy.return_value.check_policy.return_value = {
            'decision': 'approve',
            'reason': 'Within return window and valid reason'
        }
        
        # Mock refund processor
        mock_refund.return_value.process_refund.return_value = {
            'status': 'processed',
            'transaction_id': 'txn_123'
        }
        
        # Mock action logger
        mock_logger.return_value.log_action.return_value = None
        
        # Create agent with mocked tools
        agent = ReturnsAgent()
        agent.policy_checker = mock_policy.return_value
        agent.action_logger = mock_logger.return_value
        agent.refund_processor = mock_refund.return_value
        
        result = agent.process_refund_webhook(self.sample_webhook)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['decision'], 'approve')
        self.assertIn('event_id', result)
    
    def test_extract_order_info(self):
        """Test order information extraction from webhook"""
        order_info = self.agent._extract_order_info(self.sample_webhook)
        
        self.assertEqual(order_info['order_id'], '12345')
        self.assertEqual(order_info['amount'], 99.99)
        self.assertEqual(order_info['return_reason'], 'defective')
        self.assertEqual(order_info['customer_email'], 'customer@example.com')
    
    def test_extract_order_info_missing_data(self):
        """Test order extraction with missing data"""
        incomplete_webhook = {'order_id': '999'}
        
        order_info = self.agent._extract_order_info(incomplete_webhook)
        
        self.assertEqual(order_info['order_id'], '999')
        self.assertEqual(order_info['amount'], 0.0)
        self.assertEqual(order_info['return_reason'], 'not_specified')
    
    def test_process_webhook_error_handling(self):
        """Test error handling in webhook processing"""
        # Invalid webhook data
        invalid_webhook = "not a dict"
        
        result = self.agent.process_refund_webhook(invalid_webhook)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_get_status_summary(self):
        """Test status summary method"""
        summary = self.agent.get_status_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('agent_status', summary)

if __name__ == '__main__':
    unittest.main() 