"""Tool: RefundProcessor
Process refunds via Shopify Admin API for approved returns.

Example:
    from tools.refund_processor import RefundProcessor
    from config import SHOPIFY_ADMIN_TOKEN, SHOPIFY_STORE_DOMAIN
    
    rp = RefundProcessor(SHOPIFY_ADMIN_TOKEN, SHOPIFY_STORE_DOMAIN)
    result = rp.process_refund("123456789", line_item_id="item_123")
"""

from __future__ import annotations

import logging
import requests
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RefundProcessor:
    """Process refunds for approved returns via Shopify Admin API."""

    API_VERSION = "2023-10"

    def __init__(self, admin_token: str, store_domain: str):
        if not admin_token or not store_domain:
            raise ValueError("admin_token and store_domain are required")
        self.admin_token = admin_token
        self.store_domain = store_domain.rstrip("/")
        self.base_url = f"https://{self.store_domain}/admin/api/{self.API_VERSION}/graphql.json"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.admin_token,
        }

    def process_refund(
        self, 
        order_id: str, 
        line_item_id: Optional[str] = None, 
        amount: Optional[float] = None, 
        quantity: Optional[int] = None,
        reason: str = "customer_request"
    ) -> Dict[str, Any]:
        """Process a refund for a specific order.
        
        Args:
            order_id: Shopify order ID (numeric or GID format)
            line_item_id: Specific line item to refund (optional)
            amount: Specific amount to refund (optional)
            quantity: Quantity to refund for line item (optional, defaults to 1)
            reason: Reason for the refund
            
        Returns:
            Dict with success/error status and refund details
        """
        # Validation
        if not order_id:
            return {"error": "order_id is required"}
        
        if not line_item_id and not amount:
            return {"error": "Either line_item_id or amount must be specified"}

        # Format IDs for GraphQL
        order_gid = self._format_order_id(order_id)
        line_item_gid = self._format_line_item_id(line_item_id) if line_item_id else None

        # Process refund based on what's specified
        if line_item_gid:
            return self._refund_line_item(order_gid, line_item_gid, quantity or 1, reason)
        elif amount:
            return self._refund_amount(order_gid, amount, reason)

    def _refund_line_item(self, order_id: str, line_item_id: str, quantity: int, reason: str) -> Dict[str, Any]:
        """Refund a specific line item."""
        mutation = _REFUND_LINE_ITEM_MUTATION
        variables = {
            "orderId": order_id,
            "lineItemId": line_item_id,
            "quantity": quantity,
            "reason": reason
        }
        return self._execute_mutation(mutation, variables)

    def _refund_amount(self, order_id: str, amount: float, reason: str) -> Dict[str, Any]:
        """Refund a specific amount."""
        mutation = _REFUND_AMOUNT_MUTATION
        variables = {
            "orderId": order_id,
            "amount": str(amount),
            "reason": reason
        }
        return self._execute_mutation(mutation, variables)

    def _execute_mutation(self, mutation: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL mutation against Shopify Admin API."""
        payload = {"query": mutation, "variables": variables}
        
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=15)
            response.raise_for_status()
            result = response.json()
        except Exception as exc:
            logger.error("RefundProcessor API error: %s", exc)
            return {"error": "api_error", "detail": str(exc)}

        # Check for GraphQL errors
        if "errors" in result:
            error_msg = result["errors"][0]["message"]
            logger.error("GraphQL error: %s", error_msg)
            return {"error": error_msg}

        # Check for user errors
        refund_data = result.get("data", {}).get("refundCreate", {})
        user_errors = refund_data.get("userErrors", [])
        if user_errors:
            error_msg = user_errors[0]["message"]
            logger.error("User error: %s", error_msg)
            return {"error": error_msg}

        # Extract refund info
        refund = refund_data.get("refund", {})
        if refund:
            return {
                "success": True,
                "refund_id": refund.get("id"),
                "created_at": refund.get("createdAt"),
                "message": "Refund processed successfully"
            }

        return {"error": "Unknown error occurred during refund processing"}

    def _format_order_id(self, order_id: str) -> str:
        """Format order ID for GraphQL."""
        if order_id.startswith("gid://"):
            return order_id
        return f"gid://shopify/Order/{order_id}"

    def _format_line_item_id(self, line_item_id: str) -> str:
        """Format line item ID for GraphQL."""
        if line_item_id.startswith("gid://"):
            return line_item_id
        return f"gid://shopify/LineItem/{line_item_id}"


# GraphQL mutations
_REFUND_LINE_ITEM_MUTATION = """
mutation refundLineItem($orderId: ID!, $lineItemId: ID!, $quantity: Int!, $reason: String) {
  refundCreate(input: {
    orderId: $orderId,
    shipping: { fullRefund: true },
    refundLineItems: [{ lineItemId: $lineItemId, quantity: $quantity }],
    note: $reason
  }) {
    refund {
      id
      createdAt
    }
    userErrors {
      field
      message
    }
  }
}
"""

_REFUND_AMOUNT_MUTATION = """
mutation refundAmount($orderId: ID!, $amount: String!, $reason: String) {
  refundCreate(input: {
    orderId: $orderId,
    shipping: { fullRefund: true },
    transactions: [{ amount: $amount }],
    note: $reason
  }) {
    refund {
      id
      createdAt
    }
    userErrors {
      field
      message
    }
  }
}
""" 