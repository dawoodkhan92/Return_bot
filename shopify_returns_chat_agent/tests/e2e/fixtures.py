"""
Customer journey fixtures for end-to-end testing.

These fixtures define realistic customer scenarios for testing the complete
returns process including successful returns, policy violations, edge cases, etc.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
import uuid


@pytest.fixture
def valid_return_journey():
    """Customer with valid return within policy window"""
    return {
        "customer": {
            "id": "cust_12345",
            "name": "Jane Smith",
            "email": "jane@example.com"
        },
        "order": {
            "id": "gid://shopify/Order/ord_78901",
            "name": "#1001",
            "date": (datetime.now() - timedelta(days=15)).isoformat(),
            "items": [
                {
                    "id": "gid://shopify/LineItem/item_001", 
                    "name": "Blue T-Shirt", 
                    "price": "29.99", 
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_001",
                        "title": "Medium / Blue",
                        "sku": "TSHIRT-M-BLUE"
                    }
                }
            ],
            "total": "29.99",
            "financial_status": "paid",
            "fulfillment_status": "fulfilled"
        },
        "return_reason": "wrong_size",
        "conversation_flow": [
            "I need to return my blue t-shirt",
            "My order number is #1001",
            "It's the wrong size - I need a larger size",
            "Yes, I have the original packaging",
            "I'd like a refund to my original payment method"
        ]
    }


@pytest.fixture
def policy_violation_journey():
    """Customer with return outside policy window"""
    return {
        "customer": {
            "id": "cust_23456",
            "name": "John Doe", 
            "email": "john@example.com"
        },
        "order": {
            "id": "gid://shopify/Order/ord_89012",
            "name": "#1002",
            "date": (datetime.now() - timedelta(days=45)).isoformat(),
            "items": [
                {
                    "id": "gid://shopify/LineItem/item_002",
                    "name": "Black Jeans",
                    "price": "59.99", 
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_002",
                        "title": "32x32 / Black",
                        "sku": "JEANS-32-32-BLACK"
                    }
                }
            ],
            "total": "59.99",
            "financial_status": "paid",
            "fulfillment_status": "fulfilled"
        },
        "return_reason": "changed_mind",
        "conversation_flow": [
            "I want to return my black jeans",
            "My order number is #1002",
            "I just changed my mind about them",
            "I ordered them about 45 days ago",
            "Can you make an exception to your policy?"
        ]
    }


@pytest.fixture
def partial_refund_journey():
    """Customer returning only some items from an order"""
    return {
        "customer": {
            "id": "cust_34567",
            "name": "Alice Johnson",
            "email": "alice@example.com"
        },
        "order": {
            "id": "gid://shopify/Order/ord_90123",
            "name": "#1003",
            "date": (datetime.now() - timedelta(days=10)).isoformat(),
            "items": [
                {
                    "id": "gid://shopify/LineItem/item_003",
                    "name": "Red Dress",
                    "price": "89.99",
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_003",
                        "title": "Large / Red",
                        "sku": "DRESS-L-RED"
                    }
                },
                {
                    "id": "gid://shopify/LineItem/item_004",
                    "name": "Silver Earrings",
                    "price": "29.99",
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_004",
                        "title": "Silver",
                        "sku": "EARRINGS-SILVER"
                    }
                }
            ],
            "total": "119.98",
            "financial_status": "paid",
            "fulfillment_status": "fulfilled"
        },
        "return_reason": "defective",
        "return_items": ["gid://shopify/LineItem/item_003"],
        "conversation_flow": [
            "I need to return the red dress I ordered",
            "My order number is #1003",
            "The dress has a tear in the seam",
            "I want to keep the earrings though",
            "Yes, I can provide photos of the defect"
        ]
    }


@pytest.fixture  
def edge_case_journey():
    """Edge case: International customer with shipping complications"""
    return {
        "customer": {
            "id": "cust_45678",
            "name": "François Dubois",
            "email": "francois@example.fr",
            "country": "France"
        },
        "order": {
            "id": "gid://shopify/Order/ord_01234", 
            "name": "#1004",
            "date": (datetime.now() - timedelta(days=25)).isoformat(),
            "items": [
                {
                    "id": "gid://shopify/LineItem/item_005",
                    "name": "Winter Coat",
                    "price": "199.99",
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_005",
                        "title": "XL / Navy",
                        "sku": "COAT-XL-NAVY"
                    }
                }
            ],
            "total": "199.99",
            "financial_status": "paid",
            "fulfillment_status": "fulfilled",
            "shipping": {
                "method": "international",
                "cost": "35.00",
                "tracking": "INTL123456789"
            }
        },
        "return_reason": "not_as_described",
        "conversation_flow": [
            "Je voudrais retourner mon manteau",
            "Sorry, I want to return my coat", 
            "Order number #1004",
            "The color is different from the website",
            "Do I need to pay for international return shipping?",
            "Can I get a return label?"
        ]
    }


@pytest.fixture
def order_lookup_by_email_journey():
    """Customer who doesn't have order number but knows email"""
    return {
        "customer": {
            "id": "cust_56789",
            "name": "Maria Garcia",
            "email": "maria@example.com"
        },
        "order": {
            "id": "gid://shopify/Order/ord_11111",
            "name": "#1005", 
            "date": (datetime.now() - timedelta(days=8)).isoformat(),
            "items": [
                {
                    "id": "gid://shopify/LineItem/item_006",
                    "name": "Running Shoes",
                    "price": "129.99",
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_006",
                        "title": "Size 8 / White",
                        "sku": "SHOES-8-WHITE"
                    }
                }
            ],
            "total": "129.99",
            "financial_status": "paid", 
            "fulfillment_status": "fulfilled"
        },
        "return_reason": "wrong_size",
        "conversation_flow": [
            "I want to return some running shoes",
            "I don't have the order number but my email is maria@example.com",
            "They're too small, I need a bigger size",
            "I ordered them about a week ago",
            "Yes, I'd like store credit instead of a refund"
        ]
    }


@pytest.fixture
def high_value_order_journey():
    """Customer with high-value order requiring special handling"""
    return {
        "customer": {
            "id": "cust_67890",
            "name": "Robert Chen",
            "email": "robert@example.com"
        },
        "order": {
            "id": "gid://shopify/Order/ord_22222",
            "name": "#1006",
            "date": (datetime.now() - timedelta(days=5)).isoformat(),
            "items": [
                {
                    "id": "gid://shopify/LineItem/item_007",
                    "name": "Designer Watch",
                    "price": "899.99",
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_007",
                        "title": "Gold / Leather Band",
                        "sku": "WATCH-GOLD-LEATHER"
                    }
                }
            ],
            "total": "899.99",
            "financial_status": "paid",
            "fulfillment_status": "fulfilled"
        },
        "return_reason": "not_as_described",
        "conversation_flow": [
            "I need to return an expensive watch I bought",
            "Order number #1006",
            "The watch looks different from the photos online",
            "It was $899.99",
            "Do I need any special return process for expensive items?",
            "I want to make sure it's insured for shipping back"
        ]
    }


@pytest.fixture
def defective_item_journey():
    """Customer with clearly defective item needing immediate resolution"""
    return {
        "customer": {
            "id": "cust_78901", 
            "name": "Sarah Wilson",
            "email": "sarah@example.com"
        },
        "order": {
            "id": "gid://shopify/Order/ord_33333",
            "name": "#1007",
            "date": (datetime.now() - timedelta(days=3)).isoformat(),
            "items": [
                {
                    "id": "gid://shopify/LineItem/item_008",
                    "name": "Bluetooth Headphones",
                    "price": "79.99",
                    "quantity": 1,
                    "variant": {
                        "id": "gid://shopify/ProductVariant/var_008",
                        "title": "Black / Wireless",
                        "sku": "HEADPHONES-BLACK-BT"
                    }
                }
            ],
            "total": "79.99",
            "financial_status": "paid",
            "fulfillment_status": "fulfilled"
        },
        "return_reason": "defective",
        "conversation_flow": [
            "I received defective headphones",
            "Order #1007",
            "They won't turn on at all, completely dead",
            "I tried charging them overnight",
            "This is clearly a manufacturing defect",
            "I need a replacement or immediate refund"
        ]
    }


@pytest.fixture
def all_journey_fixtures():
    """Convenience fixture that returns all journey scenarios"""
    return [
        "valid_return_journey",
        "policy_violation_journey", 
        "partial_refund_journey",
        "edge_case_journey",
        "order_lookup_by_email_journey",
        "high_value_order_journey",
        "defective_item_journey"
    ] 