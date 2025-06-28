import pytest
import tempfile
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.refund_processor import RefundProcessor


class TestRefundProcessor:
    """Test cases for RefundProcessor tool"""
    
    def setup_method(self):
        """Set up test fixtures with temporary log file"""
        # Create a temporary log file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log_file = os.path.join(self.temp_dir, 'test_refunds.log')
        self.refund_processor = RefundProcessor(log_file_path=self.temp_log_file)
    
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test RefundProcessor initialization"""
        assert self.refund_processor.log_file_path == self.temp_log_file
        assert os.path.exists(os.path.dirname(self.temp_log_file))
    
    def test_process_refund_approve(self):
        """Test processing an approved refund"""
        result = self.refund_processor.process_refund(
            order_id="order_123",
            amount=50.00,
            decision="approve",
            additional_data={"test": "data"}
        )
        
        assert "Refund approved and logged" in result
        assert "order_123" in result
        assert "$50.00" in result
    
    def test_process_refund_deny(self):
        """Test processing a denied refund"""
        result = self.refund_processor.process_refund(
            order_id="order_456",
            amount=75.50,
            decision="deny"
        )
        
        assert "Refund denied and logged" in result
        assert "order_456" in result
        assert "$75.50" in result
    
    def test_process_refund_flag(self):
        """Test processing a flagged refund"""
        result = self.refund_processor.process_refund(
            order_id="order_789",
            amount=25.99,
            decision="flag"
        )
        
        assert "Refund flagged for manual review" in result
        assert "order_789" in result
        assert "$25.99" in result
    
    def test_process_refund_missing_order_id(self):
        """Test processing refund with missing order ID"""
        result = self.refund_processor.process_refund(
            order_id="",
            amount=50.00,
            decision="approve"
        )
        
        assert "ERROR" in result
        assert "Order ID is required" in result
    
    def test_process_refund_invalid_amount(self):
        """Test processing refund with invalid amount"""
        result = self.refund_processor.process_refund(
            order_id="order_123",
            amount=-10.00,
            decision="approve"
        )
        
        assert "ERROR" in result
        assert "Invalid refund amount" in result
    
    def test_process_refund_invalid_decision(self):
        """Test processing refund with invalid decision"""
        result = self.refund_processor.process_refund(
            order_id="order_123",
            amount=50.00,
            decision="invalid_decision"
        )
        
        assert "ERROR" in result
        assert "Invalid decision" in result
    
    def test_get_status_from_decision(self):
        """Test status mapping from decision"""
        assert self.refund_processor._get_status_from_decision("approve") == "processed"
        assert self.refund_processor._get_status_from_decision("deny") == "rejected"
        assert self.refund_processor._get_status_from_decision("flag") == "pending_review"
        assert self.refund_processor._get_status_from_decision("unknown") == "unknown"
    
    def test_get_refund_summary_empty(self):
        """Test getting refund summary when no refunds processed"""
        summary = self.refund_processor.get_refund_summary()
        
        assert isinstance(summary, dict)
        assert summary['total_entries'] == 0
        assert len(summary['recent_refunds']) == 0
        assert 'summary' in summary
    
    def test_get_refund_summary_with_data(self):
        """Test getting refund summary with processed refunds"""
        # Process some refunds first
        self.refund_processor.process_refund("order_1", 10.00, "approve")
        self.refund_processor.process_refund("order_2", 20.00, "deny")
        self.refund_processor.process_refund("order_3", 30.00, "flag")
        
        summary = self.refund_processor.get_refund_summary()
        
        assert isinstance(summary, dict)
        assert summary['total_entries'] >= 3
        assert len(summary['recent_refunds']) >= 3
        
        # Check summary counts
        assert 'processed' in summary['summary']
        assert 'rejected' in summary['summary']
        assert 'pending_review' in summary['summary']


if __name__ == '__main__':
    # Run a simple test
    import tempfile
    
    # Create temporary log file
    temp_dir = tempfile.mkdtemp()
    temp_log = os.path.join(temp_dir, 'test_refunds.log')
    
    try:
        processor = RefundProcessor(log_file_path=temp_log)
        
        # Test approve
        approve_result = processor.process_refund(
            order_id="test_order_123",
            amount=49.99,
            decision="approve"
        )
        print("Approve result:", approve_result)
        
        # Test deny
        deny_result = processor.process_refund(
            order_id="test_order_456",
            amount=25.00,
            decision="deny"
        )
        print("Deny result:", deny_result)
        
        # Test flag
        flag_result = processor.process_refund(
            order_id="test_order_789",
            amount=75.50,
            decision="flag"
        )
        print("Flag result:", flag_result)
        
        # Get summary
        summary = processor.get_refund_summary()
        print("Summary:", summary)
        
        print("RefundProcessor tests completed successfully!")
        
    finally:
        # Clean up
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir) 