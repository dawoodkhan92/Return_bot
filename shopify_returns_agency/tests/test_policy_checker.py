import pytest
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.policy_checker import PolicyChecker


class TestPolicyChecker:
    """Test cases for PolicyChecker tool"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.policy_checker = PolicyChecker(return_window_days=30)
        
        # Test data
        self.valid_order_date = (datetime.now() - timedelta(days=10)).isoformat()
        self.expired_order_date = (datetime.now() - timedelta(days=35)).isoformat()
        self.valid_item_id = "test_item_123"
        self.valid_return_reason = "defective"
    
    def test_initialization(self):
        """Test PolicyChecker initialization"""
        pc = PolicyChecker(return_window_days=45)
        assert pc.return_window_days == 45
        assert 'defective' in pc.valid_return_reasons
        assert 'clothing' in pc.returnable_categories
    
    def test_valid_return_request(self):
        """Test a valid return request that should be approved"""
        result = self.policy_checker.check_policy(
            order_date=self.valid_order_date,
            item_id=self.valid_item_id,
            return_reason=self.valid_return_reason
        )
        
        assert result['decision'] == 'approve'
        assert 'meets all policy requirements' in result['reason']
        assert 'days_since_order' in result['details']
    
    def test_expired_return_window(self):
        """Test return request outside the allowed window"""
        result = self.policy_checker.check_policy(
            order_date=self.expired_order_date,
            item_id=self.valid_item_id,
            return_reason=self.valid_return_reason
        )
        
        assert result['decision'] == 'deny'
        assert 'Return window exceeded' in result['reason']
        assert result['details']['days_since_order'] > 30
    
    def test_invalid_return_reason(self):
        """Test return with invalid reason"""
        result = self.policy_checker.check_policy(
            order_date=self.valid_order_date,
            item_id=self.valid_item_id,
            return_reason="invalid_reason"
        )
        
        assert result['decision'] == 'flag'
        assert 'Invalid return reason' in result['reason']
        assert 'valid_reasons' in result['details']
    
    def test_missing_required_fields(self):
        """Test return with missing fields"""
        result = self.policy_checker.check_policy(
            order_date="",
            item_id=self.valid_item_id,
            return_reason=self.valid_return_reason
        )
        
        assert result['decision'] == 'deny'
        assert 'Missing required fields' in result['reason']
    
    def test_invalid_date_format(self):
        """Test return with invalid date format"""
        result = self.policy_checker.check_policy(
            order_date="invalid-date",
            item_id=self.valid_item_id,
            return_reason=self.valid_return_reason
        )
        
        assert result['decision'] == 'deny'
        assert 'Invalid order date format' in result['reason']
    
    def test_non_returnable_category(self):
        """Test return for non-returnable item category"""
        result = self.policy_checker.check_policy(
            order_date=self.valid_order_date,
            item_id=self.valid_item_id,
            return_reason=self.valid_return_reason,
            item_category="underwear"  # Non-returnable in our test config
        )
        
        assert result['decision'] == 'deny'
        assert 'not returnable' in result['reason']
    
    def test_get_policy_summary(self):
        """Test getting policy summary"""
        summary = self.policy_checker.get_policy_summary()
        
        assert 'return_window_days' in summary
        assert 'valid_return_reasons' in summary
        assert 'returnable_categories' in summary
        assert summary['return_window_days'] == 30


if __name__ == '__main__':
    # Run a simple test
    pc = PolicyChecker()
    
    # Test valid case
    valid_result = pc.check_policy(
        order_date=(datetime.now() - timedelta(days=10)).isoformat(),
        item_id="test_123",
        return_reason="defective"
    )
    print("Valid test result:", valid_result)
    
    # Test expired case
    expired_result = pc.check_policy(
        order_date=(datetime.now() - timedelta(days=35)).isoformat(),
        item_id="test_123",
        return_reason="defective"
    )
    print("Expired test result:", expired_result)
    
    print("PolicyChecker tests completed successfully!") 