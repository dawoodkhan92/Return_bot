import json
from pathlib import Path
from unittest.mock import patch

import pytest

# Adjust import path when running tests directly
import sys, os
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tools.order_lookup import OrderLookup

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


def test_lookup_by_id_found():
    order_json = {"data": {"order": {"id": "123", "name": "#1001"}}}
    with patch("requests.post", return_value=_mock_response(json_data=order_json)) as _:
        ol = OrderLookup(ADMIN_TOKEN, STORE_DOMAIN)
        result = ol.lookup_by_id("123")
        assert result["id"] == "123"


def test_lookup_by_id_not_found():
    order_json = {"data": {"order": None}}
    with patch("requests.post", return_value=_mock_response(json_data=order_json)):
        ol = OrderLookup(ADMIN_TOKEN, STORE_DOMAIN)
        result = ol.lookup_by_id("999")
        assert result["error"] == "not_found"


def test_lookup_by_email_found():
    orders_json = {
        "data": {
            "orders": {
                "edges": [
                    {"node": {"id": "123", "name": "#1001"}},
                    {"node": {"id": "124", "name": "#1002"}},
                ]
            }
        }
    }
    with patch("requests.post", return_value=_mock_response(json_data=orders_json)):
        ol = OrderLookup(ADMIN_TOKEN, STORE_DOMAIN)
        results = ol.lookup_by_email("test@example.com")
        assert len(results) == 2


def test_lookup_by_email_not_found():
    orders_json = {"data": {"orders": {"edges": []}}}
    with patch("requests.post", return_value=_mock_response(json_data=orders_json)):
        ol = OrderLookup(ADMIN_TOKEN, STORE_DOMAIN)
        result = ol.lookup_by_email("no@example.com")
        assert result["error"] == "not_found" 