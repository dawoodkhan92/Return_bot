"""Tool: ConversationLogger
Persist conversation messages, actions, and decisions for audit purposes.

Example:
    from tools.conversation_logger import ConversationLogger
    
    logger = ConversationLogger()
    logger.log_interaction("conv_123", user_msg="Hi", agent_msg="Hello!")
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ConversationLogger:
    """Log and retrieve conversation interactions for audit trails."""

    def __init__(self, log_dir: str = "logs"):
        """Initialize logger with specified log directory."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

    def log_interaction(
        self,
        conversation_id: str,
        user_msg: Optional[str] = None,
        agent_msg: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log a single interaction in the conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            user_msg: User's message (optional)
            agent_msg: Agent's response (optional)
            tool_calls: List of tool calls made during this interaction
            metadata: Additional metadata (timestamps, IDs, etc.)
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not conversation_id:
            return False

        # Generate timestamp
        timestamp = datetime.now().isoformat()

        # Create log entry
        log_entry = {
            "conversation_id": conversation_id,
            "timestamp": timestamp,
            "user_message": user_msg,
            "agent_message": agent_msg,
            "tool_calls": tool_calls or [],
            "metadata": metadata or {}
        }

        # Write to log file (JSONL format)
        log_file = self.log_dir / f"{conversation_id}.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return True
        except Exception:
            return False

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve the full history of a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of log entries, or empty list if conversation not found
        """
        log_file = self.log_dir / f"{conversation_id}.jsonl"
        
        if not log_file.exists():
            return []

        history = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        history.append(json.loads(line))
        except Exception:
            return []

        return history

    def summarize_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Generate a summary of the conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Summary dict with message counts, duration, etc.
        """
        history = self.get_conversation_history(conversation_id)

        if not history:
            return {"error": "Conversation not found"}

        # Count different types of interactions
        user_messages = sum(1 for entry in history if entry.get("user_message"))
        agent_messages = sum(1 for entry in history if entry.get("agent_message"))
        tool_calls_count = sum(len(entry.get("tool_calls", [])) for entry in history)

        # Get start and end times
        start_time = history[0]["timestamp"] if history else None
        end_time = history[-1]["timestamp"] if history else None

        # Calculate duration if both timestamps exist
        duration_seconds = None
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
                duration_seconds = (end_dt - start_dt).total_seconds()
            except ValueError:
                pass

        return {
            "conversation_id": conversation_id,
            "messages": {
                "user": user_messages,
                "agent": agent_messages,
                "total_interactions": len(history)
            },
            "tool_calls": tool_calls_count,
            "duration": {
                "start": start_time,
                "end": end_time,
                "seconds": duration_seconds
            }
        }

    def list_conversations(self) -> List[str]:
        """List all conversation IDs that have been logged.
        
        Returns:
            List of conversation IDs
        """
        try:
            conversation_files = self.log_dir.glob("*.jsonl")
            return [f.stem for f in conversation_files]
        except Exception:
            return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation log file.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if deleted successfully, False otherwise
        """
        log_file = self.log_dir / f"{conversation_id}.jsonl"
        try:
            if log_file.exists():
                log_file.unlink()
                return True
            return False
        except Exception:
            return False

    def log_tool_call(
        self,
        conversation_id: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Convenience method to log a tool call.
        
        Args:
            conversation_id: Unique identifier for the conversation
            tool_name: Name of the tool that was called
            tool_input: Input parameters passed to the tool
            tool_output: Output returned by the tool
            metadata: Additional metadata
            
        Returns:
            True if logged successfully, False otherwise
        """
        tool_call = {
            "tool_name": tool_name,
            "input": tool_input,
            "output": tool_output,
            "timestamp": datetime.now().isoformat()
        }

        return self.log_interaction(
            conversation_id=conversation_id,
            tool_calls=[tool_call],
            metadata=metadata
        ) 