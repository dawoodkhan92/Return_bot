import pytest
import tempfile
import os
import json
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.action_logger import ActionLogger


class TestActionLogger:
    """Test cases for ActionLogger tool"""
    
    def setup_method(self):
        """Set up test fixtures with temporary log file"""
        # Create a temporary log file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log_file = os.path.join(self.temp_dir, 'test_actions.log')
        self.action_logger = ActionLogger(log_file_path=self.temp_log_file)
    
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test ActionLogger initialization"""
        assert self.action_logger.log_file_path == self.temp_log_file
        assert os.path.exists(os.path.dirname(self.temp_log_file))
    
    def test_log_action_success(self):
        """Test successful action logging"""
        result = self.action_logger.log_action(
            event_id="test_001",
            decision="approve",
            reason="Test approval",
            additional_data={"test": "data"}
        )
        
        assert "Successfully logged action" in result
        assert "test_001" in result
        assert os.path.exists(self.temp_log_file)
    
    def test_log_action_missing_fields(self):
        """Test logging with missing required fields"""
        result = self.action_logger.log_action(
            event_id="",
            decision="approve",
            reason="Test approval"
        )
        
        assert "ERROR" in result
        assert "Missing required fields" in result
    
    def test_log_webhook_received(self):
        """Test webhook logging"""
        webhook_data = {
            'id': 'webhook_123',
            'order_id': 'order_456',
            'amount': 50.00,
            'other_data': 'test'
        }
        
        result = self.action_logger.log_webhook_received(webhook_data)
        
        assert "Successfully logged action" in result
        assert "webhook_webhook_123" in result
    
    def test_log_policy_check(self):
        """Test policy check logging"""
        policy_result = {
            'decision': 'approve',
            'reason': 'Policy requirements met',
            'details': {'return_window': '10 days'}
        }
        
        result = self.action_logger.log_policy_check("test_event", policy_result)
        
        assert "Successfully logged action" in result
        assert "policy_test_event" in result
    
    def test_log_refund_action(self):
        """Test refund action logging"""
        refund_result = {
            'status': 'processed',
            'message': 'Refund approved',
            'details': {'amount': 50.00}
        }
        
        result = self.action_logger.log_refund_action("test_refund", refund_result)
        
        assert "Successfully logged action" in result
        assert "refund_test_refund" in result
    
    def test_get_recent_logs_empty(self):
        """Test getting recent logs when file is empty"""
        recent_logs = self.action_logger.get_recent_logs()
        assert isinstance(recent_logs, list)
        assert len(recent_logs) == 0
    
    def test_get_recent_logs_with_data(self):
        """Test getting recent logs with data"""
        # Log some actions first
        self.action_logger.log_action("event_1", "approve", "Test 1")
        self.action_logger.log_action("event_2", "deny", "Test 2")
        
        recent_logs = self.action_logger.get_recent_logs(limit=5)
        
        assert isinstance(recent_logs, list)
        assert len(recent_logs) >= 2
        
        # Check the structure of log entries
        if recent_logs:
            log_entry = recent_logs[0]
            assert 'timestamp' in log_entry
            assert 'event_id' in log_entry
            assert 'decision' in log_entry
            assert 'reason' in log_entry
    
    def test_log_file_creation(self):
        """Test that log file is created correctly"""
        # Log an action
        self.action_logger.log_action("test_create", "approve", "Test file creation")
        
        # Check file exists and has content
        assert os.path.exists(self.temp_log_file)
        
        with open(self.temp_log_file, 'r') as f:
            content = f.read()
            assert "ACTION_LOG:" in content
            assert "test_create" in content


if __name__ == '__main__':
    # Run a simple test
    import tempfile
    
    # Create temporary log file
    temp_dir = tempfile.mkdtemp()
    temp_log = os.path.join(temp_dir, 'test.log')
    
    try:
        logger = ActionLogger(log_file_path=temp_log)
        
        # Test basic logging
        result = logger.log_action(
            event_id="test_123",
            decision="approve",
            reason="Test logging functionality"
        )
        print("Log result:", result)
        
        # Test webhook logging
        webhook_result = logger.log_webhook_received({
            'id': 'webhook_test',
            'order_id': 'order_123',
            'amount': 25.99
        })
        print("Webhook result:", webhook_result)
        
        # Get recent logs
        recent = logger.get_recent_logs()
        print("Recent logs count:", len(recent))
        
        print("ActionLogger tests completed successfully!")
        
    finally:
        # Clean up
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir) 