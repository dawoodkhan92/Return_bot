"""Tool: PolicyChecker
Determines if a return meets store policy requirements.

Example:
    from tools.policy_checker import PolicyChecker
    
    pc = PolicyChecker()
    result = pc.check_eligibility("2024-01-01T10:00:00Z", "item_123", "defective")
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any


class PolicyChecker:
    """Check return eligibility against store policies."""

    def __init__(self, store_policies: Dict[str, Any] = None):
        """Initialize with store policies or use defaults."""
        self.store_policies = store_policies or {
            "return_window_days": 30,
            "excluded_items": [],
            "valid_reasons": [
                "wrong_size",
                "defective", 
                "not_as_described",
                "changed_mind",
                "damaged_in_shipping",
                "wrong_item"
            ],
            "auto_approve_reasons": [
                "defective",
                "not_as_described",
                "damaged_in_shipping",
                "wrong_item"
            ]
        }

    def check_eligibility(self, order_date: str, item_id: str, return_reason: str) -> Dict[str, str]:
        """Check if return is eligible based on store policy.
        
        Args:
            order_date: ISO format date string when order was placed
            item_id: Shopify item/variant ID
            return_reason: Customer's reason for return
            
        Returns:
            Dict with 'decision' (approve/deny/flag) and 'reason' (explanation)
        """
        # Input validation
        if not all([order_date, item_id, return_reason]):
            return {
                "decision": "deny",
                "reason": "Missing required information (order_date, item_id, or return_reason)."
            }

        # Parse order date
        try:
            if isinstance(order_date, str):
                # Handle both Z and +00:00 timezone formats
                order_date_clean = order_date.replace('Z', '+00:00')
                order_dt = datetime.fromisoformat(order_date_clean)
            else:
                order_dt = order_date
        except (ValueError, TypeError):
            return {
                "decision": "deny", 
                "reason": "Invalid order date format."
            }

        # Check excluded items
        if item_id in self.store_policies["excluded_items"]:
            return {
                "decision": "deny",
                "reason": "This item is not eligible for returns."
            }

        # Check valid return reasons
        if return_reason not in self.store_policies["valid_reasons"]:
            return {
                "decision": "deny",
                "reason": f"Invalid return reason. Valid reasons: {', '.join(self.store_policies['valid_reasons'])}"
            }

        # Check return window
        current_date = datetime.now().replace(tzinfo=order_dt.tzinfo)
        days_since_order = (current_date - order_dt).days

        if days_since_order > self.store_policies["return_window_days"]:
            return {
                "decision": "deny",
                "reason": f"Return window of {self.store_policies['return_window_days']} days has expired."
            }

        # Auto-approve certain reasons
        if return_reason in self.store_policies["auto_approve_reasons"]:
            return {
                "decision": "approve",
                "reason": f"Return automatically approved for reason: {return_reason}"
            }

        # Flag near end of return window for manual review
        if days_since_order > (self.store_policies["return_window_days"] - 5):
            return {
                "decision": "flag",
                "reason": "Return is near the end of the return window. Flagged for manual review."
            }

        # Default approve
        return {
            "decision": "approve",
            "reason": "Return meets all policy requirements."
        }

    def get_policy_summary(self) -> Dict[str, Any]:
        """Return current policy configuration."""
        return self.store_policies.copy()

    def update_policy(self, policy_updates: Dict[str, Any]) -> None:
        """Update store policies."""
        self.store_policies.update(policy_updates) 