"""Tool: OrderLookup
Fetch order details from Shopify Admin GraphQL API.

Example:
    from tools.order_lookup import OrderLookup
    from config import SHOPIFY_ADMIN_TOKEN, SHOPIFY_STORE_DOMAIN

    ol = OrderLookup(SHOPIFY_ADMIN_TOKEN, SHOPIFY_STORE_DOMAIN)
    order = ol.lookup_by_id("123456789")
"""

from __future__ import annotations

import logging
import requests
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class OrderLookup:
    """Lookup Shopify orders by ID or customer email."""

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

    # -----------------------------
    # Public methods
    # -----------------------------

    def lookup_by_id(self, order_id: str) -> Dict[str, Any]:
        """Return order JSON by Shopify numeric order ID.
        If not found, returns {"error": "not_found"}
        """
        if not order_id:
            return {"error": "missing_order_id"}

        query = _GET_ORDER_BY_ID_QUERY
        variables = {"id": f"gid://shopify/Order/{order_id}"}
        result = self._execute_query(query, variables)
        order = result.get("data", {}).get("order") if result else None
        return order if order else {"error": "not_found"}

    def lookup_by_email(self, email: str) -> List[Dict[str, Any]] | Dict[str, str]:
        """Return list of orders for customer email or error dict."""
        if not email:
            return {"error": "missing_email"}

        query = _GET_ORDERS_BY_EMAIL_QUERY
        variables = {"query": f"email:{email}"}
        result = self._execute_query(query, variables)
        edges = (
            result.get("data", {})
            .get("orders", {})
            .get("edges", [])
            if result else []
        )
        orders = [edge["node"] for edge in edges]
        return orders if orders else {"error": "not_found"}

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _execute_query(self, query: str, variables: Dict[str, Any]):
        payload = {"query": query, "variables": variables}
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # broad catch – network & Shopify errors
            logger.error("OrderLookup API error: %s", exc)
            return {"error": "api_error", "detail": str(exc)}


# -----------------------------
# GraphQL queries (multiline strings)
# -----------------------------

_GET_ORDER_BY_ID_QUERY = """
query getOrderById($id: ID!) {
  order(id: $id) {
    id
    name
    createdAt
    customer {
      email
      firstName
      lastName
    }
    lineItems(first: 10) {
      edges {
        node {
          id
          title
          quantity
          originalUnitPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
        }
      }
    }
    refunds {
      id
    }
  }
}
"""

_GET_ORDERS_BY_EMAIL_QUERY = """
query getOrdersByEmail($query: String!) {
  orders(first: 5, query: $query) {
    edges {
      node {
        id
        name
        createdAt
        customer {
          email
          firstName
          lastName
        }
        lineItems(first: 10) {
          edges {
            node {
              id
              title
              quantity
              originalUnitPriceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
        refunds {
          id
        }
      }
    }
  }
}
""" 