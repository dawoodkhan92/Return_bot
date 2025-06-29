import pytest
from unittest.mock import patch
from pathlib import Path
import sys

# Adjust import path  
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tools.refund_processor import RefundProcessor

ADMIN_TOKEN = "dummy_token"
STORE_DOMAIN = "example.myshopify.com"


def _mock_response(status_code=200, json_data=None):
    class _Resp:
        def __init__(self):
            self.status_code = status_code
            self._json = json_data or {}

        def json(self):
            return self._json

        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise Exception("HTTP error")

    return _Resp()


class TestRefundProcessor:

    def setup_method(self):
        """Set up test fixtures."""
        self.rp = RefundProcessor(ADMIN_TOKEN, STORE_DOMAIN)

    def test_successful_line_item_refund(self):
        """Test successful refund of a line item."""
        response_data = {
            "data": {
                "refundCreate": {
                    "refund": {
                        "id": "gid://shopify/Refund/123",
                        "createdAt": "2024-01-01T10:00:00Z"
                    },
                    "userErrors": []
                }
            }
        }
        
        with patch("requests.post", return_value=_mock_response(json_data=response_data)):
            result = self.rp.process_refund("123456", line_item_id="item_123")
            assert result["success"] is True
            assert "gid://shopify/Refund/123" in result["refund_id"]

    def test_successful_line_item_refund_with_quantity(self):
        """Test successful refund of a line item with specific quantity."""
        response_data = {
            "data": {
                "refundCreate": {
                    "refund": {
                        "id": "gid://shopify/Refund/124",
                        "createdAt": "2024-01-01T10:00:00Z"
                    },
                    "userErrors": []
                }
            }
        }
        
        with patch("requests.post", return_value=_mock_response(json_data=response_data)) as mock_post:
            result = self.rp.process_refund("123456", line_item_id="item_123", quantity=3)
            assert result["success"] is True
            assert "gid://shopify/Refund/124" in result["refund_id"]
            
            # Verify that the quantity was passed in the GraphQL variables
            call_args = mock_post.call_args
            posted_data = call_args[1]['json']
            assert posted_data['variables']['quantity'] == 3

    def test_successful_amount_refund(self):
        """Test successful refund of a specific amount."""
        response_data = {
            "data": {
                "refundCreate": {
                    "refund": {
                        "id": "gid://shopify/Refund/456",
                        "createdAt": "2024-01-01T10:00:00Z"
                    },
                    "userErrors": []
                }
            }
        }
        
        with patch("requests.post", return_value=_mock_response(json_data=response_data)):
            result = self.rp.process_refund("123456", amount=50.00)
            assert result["success"] is True
            assert "gid://shopify/Refund/456" in result["refund_id"]

    def test_user_error_handling(self):
        """Test handling of Shopify user errors."""
        response_data = {
            "data": {
                "refundCreate": {
                    "refund": None,
                    "userErrors": [
                        {
                            "field": "orderId",
                            "message": "Order not found"
                        }
                    ]
                }
            }
        }
        
        with patch("requests.post", return_value=_mock_response(json_data=response_data)):
            result = self.rp.process_refund("999999", line_item_id="item_123")
            assert "error" in result
            assert "Order not found" in result["error"]

    def test_graphql_error_handling(self):
        """Test handling of GraphQL errors."""
        response_data = {
            "errors": [
                {
                    "message": "Invalid query syntax"
                }
            ]
        }
        
        with patch("requests.post", return_value=_mock_response(json_data=response_data)):
            result = self.rp.process_refund("123456", line_item_id="item_123")
            assert "error" in result
            assert "Invalid query syntax" in result["error"]

    def test_missing_parameters(self):
        """Test validation of required parameters."""
        # Missing order_id
        result = self.rp.process_refund("", line_item_id="item_123")
        assert "error" in result
        assert "order_id is required" in result["error"]
        
        # Missing both line_item_id and amount
        result = self.rp.process_refund("123456")
        assert "error" in result
        assert "Either line_item_id or amount must be specified" in result["error"]

    def test_id_formatting(self):
        """Test proper formatting of IDs for GraphQL."""
        # Test that numeric IDs get converted to GIDs
        assert self.rp._format_order_id("123456") == "gid://shopify/Order/123456"
        assert self.rp._format_line_item_id("item_123") == "gid://shopify/LineItem/item_123"
        
        # Test that existing GIDs are preserved
        existing_gid = "gid://shopify/Order/123456"
        assert self.rp._format_order_id(existing_gid) == existing_gid

    def test_network_error_handling(self):
        """Test handling of network errors."""
        with patch("requests.post", side_effect=Exception("Network error")):
            result = self.rp.process_refund("123456", line_item_id="item_123")
            assert "error" in result
            assert "api_error" in result["error"]

    def test_initialization_validation(self):
        """Test validation during initialization."""
        with pytest.raises(ValueError):
            RefundProcessor("", STORE_DOMAIN)
        
        with pytest.raises(ValueError):
            RefundProcessor(ADMIN_TOKEN, "")

    def test_unknown_error_handling(self):
        """Test handling when refund creation returns unexpected structure."""
        response_data = {
            "data": {
                "refundCreate": {
                    "refund": None,
                    "userErrors": []
                }
            }
        }
        
        with patch("requests.post", return_value=_mock_response(json_data=response_data)):
            result = self.rp.process_refund("123456", line_item_id="item_123")
            assert "error" in result
            assert "Unknown error occurred" in result["error"] 