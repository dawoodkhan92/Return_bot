#!/usr/bin/env python3
"""
Test script for enhanced logging functionality.
"""

import os
import sys
import tempfile
import shutil
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from tools.action_logger import ActionLogger

def test_enhanced_logging():
    """Test the enhanced logging functionality"""
    print("Testing enhanced logging functionality...")
    
    # Create a temporary directory for testing
    test_log_dir = tempfile.mkdtemp(prefix='test_logs_')
    
    try:
        # Initialize the enhanced logger
        logger = ActionLogger(log_dir=test_log_dir)
        
        print(f"Test log directory: {test_log_dir}")
        
        # Test 1: Basic logging methods
        print("\nTest 1: Basic logging methods")
        logger.log_info("Test info message")
        logger.log_warning("Test warning message")
        logger.log_error("Test error message")
        logger.log_debug("Test debug message")
        print("✓ Basic logging methods work")
        
        # Test 2: Action logging
        print("\nTest 2: Action logging")
        result = logger.log_action(
            event_id="test_event_001",
            decision="approve",
            reason="Test approval reason",
            additional_data={"test_key": "test_value"}
        )
        print(f"Action log result: {result}")
        assert "Successfully logged" in result
        print("✓ Action logging works")
        
        # Test 3: Webhook logging
        print("\nTest 3: Webhook logging")
        test_webhook = {
            "id": "webhook_123",
            "order_id": "order_456",
            "amount": 99.99,
            "reason": "defective"
        }
        result = logger.log_webhook_received(test_webhook)
        print(f"Webhook log result: {result}")
        assert "Successfully logged" in result
        print("✓ Webhook logging works")
        
        # Test 4: Policy check logging
        print("\nTest 4: Policy check logging")
        policy_result = {
            "decision": "approve",
            "reason": "Within return window",
            "details": {"days_since_order": 15, "return_window": 30}
        }
        result = logger.log_policy_check("test_event_001", policy_result)
        print(f"Policy log result: {result}")
        assert "Successfully logged" in result
        print("✓ Policy check logging works")
        
        # Test 5: Refund action logging
        print("\nTest 5: Refund action logging")
        refund_result = {
            "status": "processed",
            "message": "Refund approved and processed",
            "details": {"amount": 99.99, "method": "original_payment"}
        }
        result = logger.log_refund_action("test_event_001", refund_result)
        print(f"Refund log result: {result}")
        assert "Successfully logged" in result
        print("✓ Refund action logging works")
        
        # Test 6: Log file creation
        print("\nTest 6: Log file creation")
        main_log_file = os.path.join(test_log_dir, 'returns_agent.log')
        action_log_file = os.path.join(test_log_dir, 'actions.log')
        
        assert os.path.exists(main_log_file), "Main log file should exist"
        assert os.path.exists(action_log_file), "Action log file should exist"
        print("✓ Log files created correctly")
        
        # Test 7: Recent logs retrieval
        print("\nTest 7: Recent logs retrieval")
        recent_logs = logger.get_recent_logs(limit=5)
        print(f"Retrieved {len(recent_logs)} recent log entries")
        assert len(recent_logs) > 0, "Should have recent log entries"
        
        # Verify structure of log entries
        for entry in recent_logs:
            assert 'timestamp' in entry
            assert 'event_id' in entry
            assert 'decision' in entry
            assert 'reason' in entry
        print("✓ Recent logs retrieval works")
        
        # Test 8: Action summary
        print("\nTest 8: Action summary")
        summary = logger.get_action_summary()
        print(f"Action summary: {json.dumps(summary, indent=2)}")
        assert 'total_actions' in summary
        assert 'decisions' in summary
        assert 'recent_activity' in summary
        assert 'log_file_size' in summary
        assert summary['total_actions'] > 0
        print("✓ Action summary works")
        
        # Test 9: Log file content verification
        print("\nTest 9: Log file content verification")
        with open(main_log_file, 'r') as f:
            main_content = f.read()
        with open(action_log_file, 'r') as f:
            action_content = f.read()
        
        # Check that main log contains expected messages
        assert "Test info message" in main_content
        assert "Test warning message" in main_content
        assert "Test error message" in main_content
        assert "Action logged" in main_content
        
        # Check that action log contains structured JSON
        assert "ACTION_LOG:" in action_content
        assert "test_event_001" in action_content
        assert "approve" in action_content
        
        print("✓ Log file content verification passed")
        
        # Test 10: Error handling
        print("\nTest 10: Error handling")
        result = logger.log_action("", "", "")  # Empty values should fail gracefully
        assert "ERROR" in result
        print("✓ Error handling works")
        
        print("\n✅ All enhanced logging tests passed!")
        
    finally:
        # Clean up test directory
        try:
            shutil.rmtree(test_log_dir)
            print(f"Cleaned up test directory: {test_log_dir}")
        except Exception as e:
            print(f"Warning: Could not clean up test directory: {e}")

def test_rotating_file_simulation():
    """Test that rotating file handlers are configured correctly"""
    print("\nTesting rotating file handler configuration...")
    
    test_log_dir = tempfile.mkdtemp(prefix='test_rotating_')
    
    try:
        logger = ActionLogger(log_dir=test_log_dir)
        
        # Check that rotating handlers are set up
        main_logger = logger.logger
        action_logger = logger.action_logger
        
        # Verify main logger has rotating file handler
        main_handlers = [h for h in main_logger.handlers if hasattr(h, 'maxBytes')]
        assert len(main_handlers) > 0, "Main logger should have rotating file handler"
        
        # Verify action logger has rotating file handler
        action_handlers = [h for h in action_logger.handlers if hasattr(h, 'maxBytes')]
        assert len(action_handlers) > 0, "Action logger should have rotating file handler"
        
        # Check configuration
        main_handler = main_handlers[0]
        action_handler = action_handlers[0]
        
        assert main_handler.maxBytes == 10485760, "Main logger should have 10MB max size"
        assert main_handler.backupCount == 5, "Main logger should keep 5 backups"
        
        assert action_handler.maxBytes == 5242880, "Action logger should have 5MB max size"
        assert action_handler.backupCount == 10, "Action logger should keep 10 backups"
        
        print("✓ Rotating file handlers configured correctly")
        
    finally:
        try:
            shutil.rmtree(test_log_dir)
        except Exception:
            pass

if __name__ == '__main__':
    try:
        test_enhanced_logging()
        test_rotating_file_simulation()
        print("\n🎉 All enhanced logging tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 