import pytest
import json
import tempfile
import shutil
from pathlib import Path
import sys

# Adjust import path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tools.conversation_logger import ConversationLogger


class TestConversationLogger:

    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = ConversationLogger(log_dir=self.temp_dir)
        self.conversation_id = "test_conv_123"

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_interaction_basic(self):
        """Test basic interaction logging."""
        result = self.logger.log_interaction(
            self.conversation_id,
            user_msg="Hello",
            agent_msg="Hi there!"
        )
        assert result is True

        # Verify log file was created
        log_file = Path(self.temp_dir) / f"{self.conversation_id}.jsonl"
        assert log_file.exists()

        # Verify content
        with open(log_file, 'r') as f:
            log_entry = json.loads(f.read().strip())
            assert log_entry["conversation_id"] == self.conversation_id
            assert log_entry["user_message"] == "Hello"
            assert log_entry["agent_message"] == "Hi there!"
            assert "timestamp" in log_entry

    def test_log_interaction_with_tool_calls(self):
        """Test logging with tool calls."""
        tool_calls = [
            {
                "tool_name": "OrderLookup",
                "input": {"order_id": "123"},
                "output": {"status": "found"}
            }
        ]
        
        result = self.logger.log_interaction(
            self.conversation_id,
            user_msg="Check order 123",
            tool_calls=tool_calls
        )
        assert result is True

        history = self.logger.get_conversation_history(self.conversation_id)
        assert len(history) == 1
        assert len(history[0]["tool_calls"]) == 1
        assert history[0]["tool_calls"][0]["tool_name"] == "OrderLookup"

    def test_log_interaction_with_metadata(self):
        """Test logging with metadata."""
        metadata = {"session_id": "sess_456", "user_id": "user_789"}
        
        result = self.logger.log_interaction(
            self.conversation_id,
            user_msg="Test message",
            metadata=metadata
        )
        assert result is True

        history = self.logger.get_conversation_history(self.conversation_id)
        assert history[0]["metadata"] == metadata

    def test_log_interaction_invalid_conversation_id(self):
        """Test logging with invalid conversation ID."""
        result = self.logger.log_interaction("", user_msg="Test")
        assert result is False

    def test_get_conversation_history_existing(self):
        """Test retrieving history for existing conversation."""
        # Log multiple interactions
        self.logger.log_interaction(self.conversation_id, user_msg="First message")
        self.logger.log_interaction(self.conversation_id, agent_msg="First response")
        self.logger.log_interaction(self.conversation_id, user_msg="Second message")

        history = self.logger.get_conversation_history(self.conversation_id)
        assert len(history) == 3
        assert history[0]["user_message"] == "First message"
        assert history[1]["agent_message"] == "First response"
        assert history[2]["user_message"] == "Second message"

    def test_get_conversation_history_nonexistent(self):
        """Test retrieving history for non-existent conversation."""
        history = self.logger.get_conversation_history("nonexistent_conv")
        assert history == []

    def test_summarize_conversation_valid(self):
        """Test conversation summarization with valid data."""
        # Log various types of interactions
        self.logger.log_interaction(self.conversation_id, user_msg="Hello")
        self.logger.log_interaction(self.conversation_id, agent_msg="Hi there!")
        self.logger.log_interaction(
            self.conversation_id,
            user_msg="Check order",
            tool_calls=[{"tool_name": "OrderLookup", "input": {}, "output": {}}]
        )

        summary = self.logger.summarize_conversation(self.conversation_id)
        
        assert summary["conversation_id"] == self.conversation_id
        assert summary["messages"]["user"] == 2
        assert summary["messages"]["agent"] == 1
        assert summary["messages"]["total_interactions"] == 3
        assert summary["tool_calls"] == 1
        assert "start" in summary["duration"]
        assert "end" in summary["duration"]

    def test_summarize_conversation_nonexistent(self):
        """Test summarization for non-existent conversation."""
        summary = self.logger.summarize_conversation("nonexistent_conv")
        assert "error" in summary
        assert summary["error"] == "Conversation not found"

    def test_list_conversations(self):
        """Test listing all conversations."""
        # Create multiple conversations
        conv_ids = ["conv_1", "conv_2", "conv_3"]
        for conv_id in conv_ids:
            self.logger.log_interaction(conv_id, user_msg="Test")

        conversations = self.logger.list_conversations()
        assert len(conversations) == 3
        for conv_id in conv_ids:
            assert conv_id in conversations

    def test_delete_conversation_existing(self):
        """Test deleting an existing conversation."""
        # Create conversation
        self.logger.log_interaction(self.conversation_id, user_msg="Test")
        
        # Verify it exists
        assert self.conversation_id in self.logger.list_conversations()
        
        # Delete it
        result = self.logger.delete_conversation(self.conversation_id)
        assert result is True
        
        # Verify it's gone
        assert self.conversation_id not in self.logger.list_conversations()

    def test_delete_conversation_nonexistent(self):
        """Test deleting a non-existent conversation."""
        result = self.logger.delete_conversation("nonexistent_conv")
        assert result is False

    def test_log_tool_call_convenience_method(self):
        """Test the convenience method for logging tool calls."""
        result = self.logger.log_tool_call(
            self.conversation_id,
            tool_name="PolicyChecker",
            tool_input={"order_date": "2024-01-01", "reason": "defective"},
            tool_output={"decision": "approve", "reason": "Auto-approved"}
        )
        assert result is True

        history = self.logger.get_conversation_history(self.conversation_id)
        assert len(history) == 1
        assert len(history[0]["tool_calls"]) == 1
        
        tool_call = history[0]["tool_calls"][0]
        assert tool_call["tool_name"] == "PolicyChecker"
        assert tool_call["input"]["reason"] == "defective"
        assert tool_call["output"]["decision"] == "approve"

    def test_concurrent_logging(self):
        """Test that multiple interactions can be logged sequentially."""
        # Simulate rapid logging
        for i in range(10):
            result = self.logger.log_interaction(
                self.conversation_id,
                user_msg=f"Message {i}",
                agent_msg=f"Response {i}"
            )
            assert result is True

        history = self.logger.get_conversation_history(self.conversation_id)
        assert len(history) == 10
        
        # Verify order is preserved
        for i in range(10):
            assert history[i]["user_message"] == f"Message {i}"
            assert history[i]["agent_message"] == f"Response {i}"

    def test_unicode_handling(self):
        """Test handling of unicode characters in messages."""
        unicode_msg = "Hello 👋 World! 🌍 Testing émojis and accénts"
        
        result = self.logger.log_interaction(
            self.conversation_id,
            user_msg=unicode_msg
        )
        assert result is True

        history = self.logger.get_conversation_history(self.conversation_id)
        assert history[0]["user_message"] == unicode_msg 