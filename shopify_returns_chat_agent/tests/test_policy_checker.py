import pytest
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Adjust import path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tools.policy_checker import PolicyChecker


class TestPolicyChecker:
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pc = PolicyChecker()
        self.recent_date = (datetime.now() - timedelta(days=5)).isoformat() + "Z"
        self.old_date = (datetime.now() - timedelta(days=35)).isoformat() + "Z"
        self.near_expiry_date = (datetime.now() - timedelta(days=27)).isoformat() + "Z"

    def test_approve_valid_return(self):
        """Test approval of valid return within window."""
        result = self.pc.check_eligibility(
            self.recent_date, "item_123", "wrong_size"
        )
        assert result["decision"] == "approve"
        assert "meets all policy requirements" in result["reason"]

    def test_auto_approve_defective(self):
        """Test auto-approval for defective items."""
        result = self.pc.check_eligibility(
            self.recent_date, "item_123", "defective"
        )
        assert result["decision"] == "approve"
        assert "automatically approved" in result["reason"]

    def test_deny_expired_return(self):
        """Test denial of return outside window."""
        result = self.pc.check_eligibility(
            self.old_date, "item_123", "wrong_size"
        )
        assert result["decision"] == "deny"
        assert "Return window" in result["reason"]
        assert "expired" in result["reason"]

    def test_deny_invalid_reason(self):
        """Test denial for invalid return reason."""
        result = self.pc.check_eligibility(
            self.recent_date, "item_123", "invalid_reason"
        )
        assert result["decision"] == "deny"
        assert "Invalid return reason" in result["reason"]

    def test_deny_excluded_item(self):
        """Test denial for excluded items."""
        # Update policy to exclude an item
        self.pc.update_policy({"excluded_items": ["excluded_item"]})
        result = self.pc.check_eligibility(
            self.recent_date, "excluded_item", "wrong_size"
        )
        assert result["decision"] == "deny"
        assert "not eligible for returns" in result["reason"]

    def test_flag_near_expiry(self):
        """Test flagging for returns near expiry."""
        result = self.pc.check_eligibility(
            self.near_expiry_date, "item_123", "wrong_size"
        )
        assert result["decision"] == "flag"
        assert "near the end" in result["reason"]

    def test_deny_missing_information(self):
        """Test denial when required info is missing."""
        result = self.pc.check_eligibility("", "item_123", "wrong_size")
        assert result["decision"] == "deny"
        assert "Missing required information" in result["reason"]

    def test_deny_invalid_date_format(self):
        """Test denial for invalid date format."""
        result = self.pc.check_eligibility(
            "invalid-date", "item_123", "wrong_size"
        )
        assert result["decision"] == "deny"
        assert "Invalid order date format" in result["reason"]

    def test_custom_policies(self):
        """Test with custom store policies."""
        custom_policies = {
            "return_window_days": 14,
            "excluded_items": ["no_return_item"],
            "valid_reasons": ["defective", "wrong_size"],
            "auto_approve_reasons": ["defective"]
        }
        pc_custom = PolicyChecker(custom_policies)
        
        # Test custom window
        old_date = (datetime.now() - timedelta(days=20)).isoformat() + "Z"
        result = pc_custom.check_eligibility(old_date, "item_123", "defective")
        assert result["decision"] == "deny"
        assert "14 days" in result["reason"]

    def test_get_policy_summary(self):
        """Test policy summary retrieval."""
        summary = self.pc.get_policy_summary()
        assert "return_window_days" in summary
        assert summary["return_window_days"] == 30

    def test_update_policy(self):
        """Test policy updates."""
        self.pc.update_policy({"return_window_days": 45})
        summary = self.pc.get_policy_summary()
        assert summary["return_window_days"] == 45 