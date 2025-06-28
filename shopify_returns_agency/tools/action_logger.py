import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Dict, Any, Optional

class ActionLogger:
    """
    Enhanced tool for comprehensive logging with rotating files and structured output.
    
    Features:
    - Rotating file handlers to prevent large log files
    - Structured JSON logging for actions
    - Separate log files for different types of events
    - Console and file logging with proper formatting
    """
    
    def __init__(self, log_file_path: Optional[str] = None, log_dir: Optional[str] = None):
        """Initialize ActionLogger with enhanced configuration"""
        
        # Set up log directory
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        self.log_dir = log_dir
        
        # Ensure log directory exists
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Set up main log file path
        if log_file_path is None:
            log_file_path = os.path.join(self.log_dir, 'returns_agent.log')
        self.log_file_path = log_file_path
        
        # Set up action log file path
        self.action_log_file = os.path.join(self.log_dir, 'actions.log')
        
        # Initialize loggers
        self._setup_main_logger()
        self._setup_action_logger()
    
    def _setup_main_logger(self):
        """Set up the main logger with rotating file handler"""
        self.logger = logging.getLogger('ReturnsAgent')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = RotatingFileHandler(
            self.log_file_path,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _setup_action_logger(self):
        """Set up the action logger for structured logging"""
        self.action_logger = logging.getLogger('ActionLogger')
        self.action_logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.action_logger.handlers[:]:
            self.action_logger.removeHandler(handler)
        
        # Rotating file handler for actions (5MB max, keep 10 backups)
        action_handler = RotatingFileHandler(
            self.action_log_file,
            maxBytes=5242880,  # 5MB
            backupCount=10
        )
        action_handler.setLevel(logging.INFO)
        
        # Simple formatter for structured logs
        action_formatter = logging.Formatter('%(asctime)s - %(message)s')
        action_handler.setFormatter(action_formatter)
        
        self.action_logger.addHandler(action_handler)
    
    def log_info(self, message: str):
        """Log an informational message"""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """Log an error message"""
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log a warning message"""
        self.logger.warning(message)
    
    def log_debug(self, message: str):
        """Log a debug message"""
        self.logger.debug(message)
    
    def log_action(self, event_id: str, decision: str, reason: str, 
                  additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an action/decision with structured data.
        
        Args:
            event_id (str): Unique identifier for the event
            decision (str): The decision made (approve/deny/flag)
            reason (str): Reason for the decision
            additional_data (dict, optional): Additional context data
            
        Returns:
            str: Confirmation message
        """
        try:
            # Validate inputs
            if not all([event_id, decision, reason]):
                error_msg = "Missing required fields for logging"
                self.log_error(error_msg)
                return f"ERROR: {error_msg}"
            
            # Create log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_id': event_id,
                'decision': decision.lower(),
                'reason': reason,
                'additional_data': additional_data or {}
            }
            
            # Log to structured action log
            action_message = f"ACTION_LOG: {json.dumps(log_entry)}"
            self.action_logger.info(action_message)
            
            # Also log to main logger for visibility
            main_message = f"Action logged - Event: {event_id}, Decision: {decision}, Reason: {reason}"
            self.log_info(main_message)
            
            return f"Successfully logged action for event {event_id}: {decision}"
            
        except Exception as e:
            error_msg = f"Error logging action: {str(e)}"
            self.log_error(error_msg)
            return f"ERROR: {error_msg}"
    
    def log_webhook_received(self, webhook_data: Dict[str, Any]) -> str:
        """
        Log webhook receipt with payload summary.
        
        Args:
            webhook_data (dict): The webhook payload
            
        Returns:
            str: Confirmation message
        """
        try:
            event_id = webhook_data.get('id', 'unknown')
            order_id = webhook_data.get('order_id', 'unknown')
            
            summary_data = {
                'webhook_type': 'shopify_return_request',
                'order_id': order_id,
                'payload_keys': list(webhook_data.keys()),
                'payload_size': len(json.dumps(webhook_data))
            }
            
            return self.log_action(
                event_id=f"webhook_{event_id}",
                decision="received",
                reason="Webhook payload received and validated",
                additional_data=summary_data
            )
            
        except Exception as e:
            error_msg = f"Error logging webhook: {str(e)}"
            self.log_error(error_msg)
            return f"ERROR: {error_msg}"
    
    def log_policy_check(self, event_id: str, policy_result: Dict[str, Any]) -> str:
        """
        Log policy check results.
        
        Args:
            event_id (str): Unique identifier for the event
            policy_result (dict): Result from PolicyChecker
            
        Returns:
            str: Confirmation message
        """
        try:
            decision = policy_result.get('decision', 'unknown')
            reason = policy_result.get('reason', 'No reason provided')
            details = policy_result.get('details', {})
            
            return self.log_action(
                event_id=f"policy_{event_id}",
                decision=decision,
                reason=f"Policy Check: {reason}",
                additional_data={
                    'policy_details': details,
                    'check_type': 'return_policy_validation'
                }
            )
            
        except Exception as e:
            error_msg = f"Error logging policy check: {str(e)}"
            self.log_error(error_msg)
            return f"ERROR: {error_msg}"
    
    def log_refund_action(self, event_id: str, refund_result: Dict[str, Any]) -> str:
        """
        Log refund processing results.
        
        Args:
            event_id (str): Unique identifier for the event
            refund_result (dict): Result from RefundProcessor
            
        Returns:
            str: Confirmation message
        """
        try:
            status = refund_result.get('status', 'unknown')
            message = refund_result.get('message', 'No message provided')
            details = refund_result.get('details', {})
            
            return self.log_action(
                event_id=f"refund_{event_id}",
                decision=status,
                reason=f"Refund Processing: {message}",
                additional_data={
                    'refund_details': details,
                    'action_type': 'refund_processing'
                }
            )
            
        except Exception as e:
            error_msg = f"Error logging refund action: {str(e)}"
            self.log_error(error_msg)
            return f"ERROR: {error_msg}"
    
    def get_recent_logs(self, limit: int = 10) -> list:
        """
        Get recent log entries from the action log.
        
        Args:
            limit (int): Number of recent entries to return
            
        Returns:
            list: Recent log entries
        """
        try:
            if not os.path.exists(self.action_log_file):
                return []
            
            with open(self.action_log_file, 'r') as f:
                lines = f.readlines()
            
            # Get the last 'limit' lines
            recent_lines = lines[-limit:] if len(lines) >= limit else lines
            
            # Parse JSON entries
            entries = []
            for line in recent_lines:
                try:
                    if 'ACTION_LOG:' in line:
                        # Extract JSON part
                        json_part = line.split('ACTION_LOG: ', 1)[1].strip()
                        entry = json.loads(json_part)
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue
            
            return entries
            
        except Exception as e:
            self.log_error(f"Error reading recent logs: {str(e)}")
            return []
    
    def get_action_summary(self, limit: int = 100) -> dict:
        """
        Get a summary of recent actions.
        
        Args:
            limit (int): Number of recent entries to analyze
            
        Returns:
            dict: Summary statistics
        """
        try:
            recent_logs = self.get_recent_logs(limit)
            
            if not recent_logs:
                return {
                    'total_actions': 0,
                    'decisions': {},
                    'recent_activity': 'No recent activity'
                }
            
            # Count decisions
            decisions = {}
            for entry in recent_logs:
                decision = entry.get('decision', 'unknown')
                decisions[decision] = decisions.get(decision, 0) + 1
            
            # Get most recent timestamp
            most_recent = recent_logs[-1].get('timestamp', 'Unknown') if recent_logs else 'Unknown'
            
            return {
                'total_actions': len(recent_logs),
                'decisions': decisions,
                'recent_activity': most_recent,
                'log_file_size': self._get_log_file_size()
            }
            
        except Exception as e:
            self.log_error(f"Error generating action summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_log_file_size(self) -> str:
        """Get formatted log file size"""
        try:
            if os.path.exists(self.action_log_file):
                size_bytes = os.path.getsize(self.action_log_file)
                if size_bytes < 1024:
                    return f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            return "0 bytes"
        except Exception:
            return "Unknown" 