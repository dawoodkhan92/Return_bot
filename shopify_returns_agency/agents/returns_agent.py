import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.policy_checker import PolicyChecker
from tools.action_logger import ActionLogger  
from tools.refund_processor import RefundProcessor

class ReturnsAgent:
    """
    Main agent for processing Shopify refund webhooks.
    
    Coordinates PolicyChecker, ActionLogger, and RefundProcessor tools
    to make automated approve/deny/flag decisions.
    """
    
    def __init__(self, return_window_days: int = 30, log_file_path: Optional[str] = None):
        """Initialize ReturnsAgent with tools"""
        self.policy_checker = PolicyChecker(return_window_days=return_window_days)
        self.action_logger = ActionLogger(log_file_path=log_file_path)
        self.refund_processor = RefundProcessor(log_file_path=log_file_path)
        
        # Set up agent logging
        self.logger = logging.getLogger('ReturnsAgent')
        self.logger.setLevel(logging.INFO)
    
    def process_refund_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Shopify refund webhook and make a decision.
        
        Args:
            webhook_data (dict): Shopify webhook payload
            
        Returns:
            dict: Processing result with decision and details
        """
        try:
            # Extract required information from webhook
            order_info = self._extract_order_info(webhook_data)
            
            # Generate unique event ID for tracking
            event_id = f"refund_{order_info['order_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Log the incoming webhook
            self.action_logger.log_action(
                event_id=event_id,
                decision="webhook_received",
                reason="Processing Shopify refund webhook",
                additional_data={
                    'order_id': order_info['order_id'],
                    'refund_amount': order_info['amount'],
                    'webhook_received_at': datetime.now().isoformat()
                }
            )
            
            # Check policy
            policy_result = self.policy_checker.check_policy(
                order_date=order_info['order_date'],
                item_id=order_info['item_id'],
                return_reason=order_info['return_reason']
            )
            
            decision = policy_result['decision']
            reason = policy_result['reason']
            
            # Log the policy decision
            self.action_logger.log_action(
                event_id=event_id,
                decision=decision,
                reason=reason,
                additional_data={
                    'policy_check_details': policy_result,
                    'order_info': order_info
                }
            )
            
            # Process based on decision
            if decision == 'approve':
                refund_result = self.refund_processor.process_refund(
                    order_id=order_info['order_id'],
                    amount=order_info['amount'],
                    decision='approve',
                    additional_data={'policy_result': policy_result}
                )
            elif decision == 'deny':
                refund_result = self.refund_processor.process_refund(
                    order_id=order_info['order_id'],
                    amount=order_info['amount'],
                    decision='deny',
                    additional_data={'policy_result': policy_result}
                )
            else:  # flag
                refund_result = self.refund_processor.process_refund(
                    order_id=order_info['order_id'],
                    amount=order_info['amount'],
                    decision='flag',
                    additional_data={'policy_result': policy_result}
                )
            
            # Return comprehensive result
            return {
                'event_id': event_id,
                'decision': decision,
                'reason': reason,
                'refund_result': refund_result,
                'order_info': order_info,
                'policy_details': policy_result,
                'processed_at': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            error_msg = f"Error processing refund webhook: {str(e)}"
            self.logger.error(error_msg)
            
            # Log the error
            self.action_logger.log_action(
                event_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                decision="error",
                reason=error_msg,
                additional_data={'webhook_data': webhook_data}
            )
            
            return {
                'status': 'error',
                'error': error_msg,
                'processed_at': datetime.now().isoformat()
            }
    
    def _extract_order_info(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract required order information from Shopify webhook.
        
        Args:
            webhook_data (dict): Shopify webhook payload
            
        Returns:
            dict: Extracted order information
        """
        try:
            # Example Shopify webhook structure - adjust based on actual webhook format
            # This is a simplified version for demonstration
            
            # Extract order ID
            order_id = webhook_data.get('order_id') or webhook_data.get('id', 'unknown')
            
            # Extract refund amount
            amount = float(webhook_data.get('amount', 0.0))
            
            # Extract order date (creation date)
            order_date = webhook_data.get('created_at', datetime.now().isoformat())
            
            # Extract item information (simplified - take first item)
            line_items = webhook_data.get('line_items', [])
            item_id = 'unknown'
            if line_items:
                item_id = line_items[0].get('id', 'unknown')
            
            # Extract return reason (might be in different places)
            return_reason = (
                webhook_data.get('reason') or 
                webhook_data.get('note') or 
                webhook_data.get('return_reason', 'not_specified')
            )
            
            # Extract customer email
            customer_email = webhook_data.get('email', 'unknown')
            
            return {
                'order_id': str(order_id),
                'amount': amount,
                'order_date': order_date,
                'item_id': str(item_id),
                'return_reason': return_reason.lower().replace(' ', '_'),
                'customer_email': customer_email,
                'raw_webhook': webhook_data
            }
            
        except Exception as e:
            # Return minimal info if extraction fails
            return {
                'order_id': 'extraction_failed',
                'amount': 0.0,
                'order_date': datetime.now().isoformat(),
                'item_id': 'unknown',
                'return_reason': 'extraction_error',
                'customer_email': 'unknown',
                'extraction_error': str(e),
                'raw_webhook': webhook_data
            }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of recent agent activities.
        
        Returns:
            dict: Summary of actions and refunds
        """
        try:
            # Get action log summary
            action_summary = self.action_logger.get_action_summary()
            
            # Get refund summary  
            refund_summary = self.refund_processor.get_refund_summary()
            
            return {
                'agent_status': 'operational',
                'last_updated': datetime.now().isoformat(),
                'actions': action_summary,
                'refunds': refund_summary
            }
            
        except Exception as e:
            return {
                'agent_status': 'error',
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            } 