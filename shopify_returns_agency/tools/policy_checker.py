from datetime import datetime, timedelta
import json
from typing import Dict, Any

class PolicyChecker:
    """
    Tool for checking if return requests meet policy requirements.
    
    Validates:
    - Return window (default 30 days)
    - Item eligibility 
    - Return reason validity
    """
    
    def __init__(self, return_window_days: int = 30):
        """Initialize PolicyChecker with configuration"""
        self.return_window_days = return_window_days
        
        # Valid return reasons
        self.valid_return_reasons = {
            'defective': True,
            'wrong_size': True,
            'wrong_color': True,
            'not_as_described': True,
            'damaged_in_shipping': True,
            'changed_mind': True,
            'duplicate_order': True
        }
        
        # Item categories that can be returned
        self.returnable_categories = {
            'clothing': True,
            'shoes': True,
            'accessories': True,
            'bags': False,  # Example: bags might not be returnable
            'underwear': False,  # Example: underwear might not be returnable
            'sale_items': False  # Example: sale items might not be returnable
        }
    
    def check_policy(self, order_date: str, item_id: str, return_reason: str, 
                    item_category: str = 'clothing') -> Dict[str, Any]:
        """
        Check if return request meets policy requirements.
        
        Args:
            order_date (str): ISO format date string (YYYY-MM-DD)
            item_id (str): Unique identifier for the item
            return_reason (str): Reason for return
            item_category (str): Category of the item being returned
            
        Returns:
            Dict containing decision, reason, and details
        """
        try:
            # Validate inputs
            if not all([order_date, item_id, return_reason]):
                return {
                    'decision': 'deny',
                    'reason': 'Missing required fields',
                    'details': {
                        'order_date': bool(order_date),
                        'item_id': bool(item_id),
                        'return_reason': bool(return_reason)
                    }
                }
            
            # Parse order date
            try:
                order_datetime = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    'decision': 'deny',
                    'reason': 'Invalid order date format',
                    'details': {'expected_format': 'YYYY-MM-DD or ISO format'}
                }
            
            # Check return window
            days_since_order = (datetime.now() - order_datetime.replace(tzinfo=None)).days
            if days_since_order > self.return_window_days:
                return {
                    'decision': 'deny',
                    'reason': f'Return window exceeded ({days_since_order} days > {self.return_window_days} days)',
                    'details': {
                        'days_since_order': days_since_order,
                        'return_window_days': self.return_window_days
                    }
                }
            
            # Check return reason validity
            if return_reason.lower() not in self.valid_return_reasons:
                return {
                    'decision': 'flag',
                    'reason': 'Invalid return reason - requires manual review',
                    'details': {
                        'provided_reason': return_reason,
                        'valid_reasons': list(self.valid_return_reasons.keys())
                    }
                }
            
            # Check item eligibility
            if not self.returnable_categories.get(item_category.lower(), True):
                return {
                    'decision': 'deny',
                    'reason': f'Item category "{item_category}" is not returnable',
                    'details': {
                        'item_category': item_category,
                        'returnable_categories': {k: v for k, v in self.returnable_categories.items() if v}
                    }
                }
            
            # If all checks pass
            return {
                'decision': 'approve',
                'reason': 'Return request meets all policy requirements',
                'details': {
                    'days_since_order': days_since_order,
                    'return_window_days': self.return_window_days,
                    'return_reason': return_reason,
                    'item_category': item_category
                }
            }
            
        except Exception as e:
            return {
                'decision': 'flag',
                'reason': f'Error processing policy check: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Return summary of current policy settings"""
        return {
            'return_window_days': self.return_window_days,
            'valid_return_reasons': list(self.valid_return_reasons.keys()),
            'returnable_categories': {k: v for k, v in self.returnable_categories.items() if v},
            'non_returnable_categories': {k: v for k, v in self.returnable_categories.items() if not v}
        } 