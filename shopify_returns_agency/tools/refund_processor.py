import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

class RefundProcessor:
    """
    Tool for processing refund actions.
    
    Currently logs refund actions - can be extended to integrate with
    payment processors, Shopify Admin API, etc.
    """
    
    def __init__(self, log_file_path: Optional[str] = None):
        """Initialize RefundProcessor with configuration"""
        if log_file_path is None:
            log_file_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'refunds.log')
        
        self.log_file_path = log_file_path
        
        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up logging
        self.logger = logging.getLogger('RefundProcessor')
        self.logger.setLevel(logging.INFO)
    
    def process_refund(self, order_id: str, amount: float, decision: str, 
                      additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a refund action (currently logs the action).
        
        Args:
            order_id (str): Shopify order ID
            amount (float): Refund amount
            decision (str): The decision made (approve/deny/flag)
            additional_data (dict, optional): Additional context data
            
        Returns:
            str: Confirmation message
        """
        try:
            # Validate inputs
            if not order_id:
                return "ERROR: Order ID is required"
            
            if amount <= 0:
                return f"ERROR: Invalid refund amount: {amount}"
            
            if decision not in ['approve', 'deny', 'flag']:
                return f"ERROR: Invalid decision: {decision}"
            
            # Create refund record
            refund_record = {
                'timestamp': datetime.now().isoformat(),
                'order_id': order_id,
                'amount': amount,
                'decision': decision.lower(),
                'status': self._get_status_from_decision(decision),
                'additional_data': additional_data or {}
            }
            
            # Write to log file
            with open(self.log_file_path, 'a') as f:
                f.write(f"REFUND_LOG: {json.dumps(refund_record)}\n")
            
            # Return appropriate message based on decision
            if decision.lower() == 'approve':
                return f"Refund approved and logged for order {order_id}: ${amount:.2f}"
            elif decision.lower() == 'deny':
                return f"Refund denied and logged for order {order_id}: ${amount:.2f}"
            else:  # flag
                return f"Refund flagged for manual review - order {order_id}: ${amount:.2f}"
            
        except Exception as e:
            return f"ERROR: Error processing refund: {str(e)}"
    
    def _get_status_from_decision(self, decision: str) -> str:
        """Convert decision to status"""
        status_map = {
            'approve': 'processed',
            'deny': 'rejected',
            'flag': 'pending_review'
        }
        return status_map.get(decision.lower(), 'unknown')
    
    def get_refund_summary(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get summary of recent refund actions.
        
        Args:
            limit (int): Number of recent entries to return
            
        Returns:
            dict: Summary of refund actions
        """
        try:
            if not os.path.exists(self.log_file_path):
                return {
                    'total_entries': 0,
                    'recent_refunds': [],
                    'summary': {'processed': 0, 'rejected': 0, 'pending_review': 0}
                }
            
            with open(self.log_file_path, 'r') as f:
                lines = f.readlines()
            
            # Parse recent refund entries
            recent_refunds = []
            summary = {'processed': 0, 'rejected': 0, 'pending_review': 0}
            
            for line in lines[-limit:]:
                if 'REFUND_LOG:' in line:
                    try:
                        json_part = line.split('REFUND_LOG: ')[1].strip()
                        entry = json.loads(json_part)
                        recent_refunds.append(entry)
                        
                        # Update summary
                        status = entry.get('status', 'unknown')
                        if status in summary:
                            summary[status] += 1
                            
                    except (IndexError, json.JSONDecodeError):
                        continue
            
            return {
                'total_entries': len(recent_refunds),
                'recent_refunds': recent_refunds,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_entries': 0,
                'recent_refunds': [],
                'summary': {'processed': 0, 'rejected': 0, 'pending_review': 0}
            }
 