"""Shared pytest fixtures for shopify_returns_chat_agent tests."""

import pytest
import json
import os
from unittest.mock import MagicMock
from pathlib import Path

# Add parent directory to path for imports
import sys
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))


@pytest.fixture
def mock_shopify_order():
    """Mock Shopify order data for testing."""
    return {
        "id": "gid://shopify/Order/12345",
        "name": "#1001",
        "createdAt": "2023-01-15T12:00:00Z",
        "customer": {
            "email": "customer@example.com",
            "firstName": "John",
            "lastName": "Doe"
        },
        "lineItems": {
            "edges": [
                {
                    "node": {
                        "id": "gid://shopify/LineItem/67890",
                        "title": "Test Product",
                        "quantity": 2,
                        "originalUnitPriceSet": {
                            "shopMoney": {
                                "amount": "29.99",
                                "currencyCode": "USD"
                            }
                        }
                    }
                },
                {
                    "node": {
                        "id": "gid://shopify/LineItem/67891", 
                        "title": "Another Product",
                        "quantity": 1,
                        "originalUnitPriceSet": {
                            "shopMoney": {
                                "amount": "49.99",
                                "currencyCode": "USD"
                            }
                        }
                    }
                }
            ]
        },
        "refunds": []
    }


@pytest.fixture
def mock_order_lookup(mock_shopify_order):
    """Create a mocked OrderLookup instance."""
    mock = MagicMock()
    
    # Setup mock responses
    mock.lookup_by_id.return_value = mock_shopify_order
    mock.lookup_by_email.return_value = [mock_shopify_order]
    
    return mock


@pytest.fixture
def mock_policy_checker():
    """Create a mocked PolicyChecker instance."""
    mock = MagicMock()
    
    # Default to approval
    mock.check_eligibility.return_value = {
        "decision": "approve",
        "reason": "Return is within policy guidelines"
    }
    
    return mock


@pytest.fixture
def mock_refund_processor():
    """Create a mocked RefundProcessor instance."""
    mock = MagicMock()
    
    # Default to successful refund
    mock.process_refund.return_value = {
        "success": True,
        "refund_id": "gid://shopify/Refund/12345",
        "created_at": "2024-01-01T10:00:00Z",
        "message": "Refund processed successfully"
    }
    
    return mock


@pytest.fixture
def mock_conversation_logger():
    """Create a mocked ConversationLogger instance."""
    mock = MagicMock()
    
    # Default responses
    mock.log_interaction.return_value = None
    mock.log_tool_call.return_value = None
    mock.summarize_conversation.return_value = {
        "conversation_id": "test-123",
        "total_interactions": 5,
        "summary": "Customer returned Test Product successfully"
    }
    
    return mock


@pytest.fixture
def test_config():
    """Test configuration for chat agent."""
    return {
        "SHOPIFY_ADMIN_TOKEN": "test_token",
        "SHOPIFY_STORE_DOMAIN": "test-store.myshopify.com"
    }


@pytest.fixture
def mock_http_response():
    """Factory for creating mock HTTP responses."""
    def _create_response(status_code=200, json_data=None):
        class MockResponse:
            def __init__(self):
                self.status_code = status_code
                self._json = json_data or {}

            def json(self):
                return self._json

            def raise_for_status(self):
                if not (200 <= self.status_code < 300):
                    raise Exception(f"HTTP {self.status_code} error")

        return MockResponse()
    
    return _create_response


@pytest.fixture
def sample_line_items():
    """Sample line items for testing."""
    return [
        {
            "id": "gid://shopify/LineItem/67890",
            "title": "Test Product",
            "quantity": 2,
            "originalUnitPriceSet": {
                "shopMoney": {
                    "amount": "29.99",
                    "currencyCode": "USD"
                }
            }
        },
        {
            "id": "gid://shopify/LineItem/67891",
            "title": "Another Product", 
            "quantity": 1,
            "originalUnitPriceSet": {
                "shopMoney": {
                    "amount": "49.99",
                    "currencyCode": "USD"
                }
            }
        }
    ] 