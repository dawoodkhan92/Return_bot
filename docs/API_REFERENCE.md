# 🔧 API Reference

Technical reference documentation for the Shopify Returns Chat Agent. This guide covers all classes, methods, tools, and configuration options for developers.

## 📋 **Table of Contents**

- [Core Classes](#core-classes)
- [Tools Reference](#tools-reference)
- [Configuration](#configuration)
- [Environment Variables](#environment-variables)
- [Error Handling](#error-handling)
- [Testing Reference](#testing-reference)
- [Integration Examples](#integration-examples)

## 🏗️ **Core Classes**

### `LLMReturnsChatAgent`

Main orchestrator class that integrates OpenAI with specialized tools.

```python
from llm_returns_chat_agent import LLMReturnsChatAgent

class LLMReturnsChatAgent:
    def __init__(self, config: dict)
    def start_conversation(self) -> str
    def process_message(self, message: str) -> str
    def get_conversation_history(self) -> List[str]
    def get_conversation_summary(self) -> str
```

#### Constructor Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `config` | `dict` | Configuration dictionary with API keys and settings | ✅ |

#### Methods

##### `start_conversation() -> str`
Initializes a new conversation and returns the greeting message.

**Returns:** Welcome message string

**Example:**
```python
agent = LLMReturnsChatAgent(config)
greeting = agent.start_conversation()
print(greeting)
# Output: "Hello! I'm here to help you with returns and exchanges..."
```

##### `process_message(message: str) -> str`
Processes user input using OpenAI function calling and specialized tools.

**Parameters:**
- `message` (str): User input message

**Returns:** Agent response string

**Example:**
```python
response = agent.process_message("I want to return order #1001")
print(response)
# Output: AI-generated response with tool interactions
```

##### `get_conversation_history() -> List[str]`
Returns the complete conversation history.

**Returns:** List of conversation entries

##### `get_conversation_summary() -> str`
Generates an AI summary of the conversation.

**Returns:** Summary string

---

## 🛠️ **Tools Reference**

### `OrderLookup`

Handles Shopify GraphQL queries for order information.

```python
from tools.order_lookup import OrderLookup

class OrderLookup:
    def __init__(self, admin_token: str, store_domain: str)
    def lookup_order_by_id(self, order_id: str) -> dict
    def lookup_orders_by_email(self, email: str) -> List[dict]
    def validate_order_access(self, order_id: str, customer_info: dict) -> bool
```

#### Methods

##### `lookup_order_by_id(order_id: str) -> dict`
Retrieves order details by order ID.

**Parameters:**
- `order_id` (str): Shopify order ID (with or without # prefix)

**Returns:** Order data dictionary

**Example:**
```python
lookup = OrderLookup(admin_token, store_domain)
order = lookup.lookup_order_by_id("1001")

# Response format:
{
    "id": "gid://shopify/Order/1001",
    "name": "#1001",
    "email": "customer@example.com",
    "totalPrice": {"amount": "85.00", "currencyCode": "USD"},
    "createdAt": "2024-03-15T10:30:00Z",
    "lineItems": [
        {
            "id": "gid://shopify/LineItem/1",
            "title": "Blue T-Shirt",
            "variant": {"title": "Size M"},
            "quantity": 1,
            "price": {"amount": "35.00", "currencyCode": "USD"}
        }
    ]
}
```

##### `lookup_orders_by_email(email: str) -> List[dict]`
Finds recent orders for a customer email.

**Parameters:**
- `email` (str): Customer email address

**Returns:** List of order dictionaries (last 10 orders)

##### `validate_order_access(order_id: str, customer_info: dict) -> bool`
Validates that a customer has access to an order.

**Parameters:**
- `order_id` (str): Order ID to validate
- `customer_info` (dict): Customer information for validation

**Returns:** Boolean indicating access permission

---

### `PolicyChecker`

Business rule engine for return eligibility validation.

```python
from tools.policy_checker import PolicyChecker

class PolicyChecker:
    def __init__(self, return_window_days: int = 30)
    def check_return_eligibility(self, order_data: dict, item_id: str, reason: str) -> dict
    def get_return_policy_summary(self) -> dict
    def validate_return_reason(self, reason: str) -> bool
```

#### Methods

##### `check_return_eligibility(order_data: dict, item_id: str, reason: str) -> dict`
Comprehensive return eligibility check.

**Parameters:**
- `order_data` (dict): Order information from OrderLookup
- `item_id` (str): Specific line item ID
- `reason` (str): Return reason provided by customer

**Returns:** Eligibility result dictionary

**Example:**
```python
checker = PolicyChecker(return_window_days=30)
result = checker.check_return_eligibility(order_data, item_id, "size issue")

# Response format:
{
    "eligible": True,
    "reason": "Item is within return window and meets policy requirements",
    "return_window": {
        "days_since_purchase": 5,
        "days_remaining": 25,
        "window_days": 30
    },
    "policy_checks": {
        "within_window": True,
        "valid_reason": True,
        "item_condition": "acceptable",
        "final_sale": False
    },
    "refund_amount": "35.00",
    "currency": "USD"
}
```

##### `get_return_policy_summary() -> dict`
Returns the complete return policy information.

**Returns:** Policy summary dictionary

##### `validate_return_reason(reason: str) -> bool`
Validates if a return reason is acceptable.

**Parameters:**
- `reason` (str): Customer-provided return reason

**Returns:** Boolean indicating if reason is valid

---

### `RefundProcessor`

Handles automated refund processing via Shopify Admin API.

```python
from tools.refund_processor import RefundProcessor

class RefundProcessor:
    def __init__(self, admin_token: str, store_domain: str)
    def process_refund(self, order_id: str, line_item_id: str, amount: str, reason: str) -> dict
    def calculate_refund_amount(self, order_data: dict, line_item_id: str) -> str
    def validate_refund_request(self, order_data: dict, refund_data: dict) -> bool
```

#### Methods

##### `process_refund(order_id: str, line_item_id: str, amount: str, reason: str) -> dict`
Processes a refund through Shopify API.

**Parameters:**
- `order_id` (str): Shopify order ID
- `line_item_id` (str): Line item ID to refund
- `amount` (str): Refund amount
- `reason` (str): Refund reason for records

**Returns:** Refund processing result

**Example:**
```python
processor = RefundProcessor(admin_token, store_domain)
result = processor.process_refund("1001", "line_item_1", "35.00", "size issue")

# Response format:
{
    "success": True,
    "refund_id": "gid://shopify/Refund/123",
    "amount": "35.00",
    "currency": "USD",
    "status": "pending",
    "estimated_processing_time": "3-5 business days",
    "refund_method": "original_payment_method"
}
```

##### `calculate_refund_amount(order_data: dict, line_item_id: str) -> str`
Calculates the eligible refund amount for a line item.

##### `validate_refund_request(order_data: dict, refund_data: dict) -> bool`
Validates refund request before processing.

---

### `ConversationLogger`

Audit trail and analytics logging system.

```python
from tools.conversation_logger import ConversationLogger

class ConversationLogger:
    def __init__(self, log_directory: str = "logs")
    def log_conversation(self, session_id: str, user_message: str, agent_response: str, metadata: dict = None)
    def log_action(self, action_type: str, details: dict, session_id: str = None)
    def get_session_logs(self, session_id: str) -> List[dict]
    def generate_analytics_summary(self, date_range: tuple = None) -> dict
```

#### Methods

##### `log_conversation(session_id: str, user_message: str, agent_response: str, metadata: dict = None)`
Logs a conversation exchange.

**Parameters:**
- `session_id` (str): Unique session identifier
- `user_message` (str): User input
- `agent_response` (str): Agent response
- `metadata` (dict, optional): Additional metadata

##### `log_action(action_type: str, details: dict, session_id: str = None)`
Logs specific actions (refunds, lookups, etc.).

**Parameters:**
- `action_type` (str): Type of action ("refund", "lookup", "policy_check")
- `details` (dict): Action-specific details
- `session_id` (str, optional): Associated session ID

**Example:**
```python
logger = ConversationLogger()
logger.log_action("refund", {
    "order_id": "1001",
    "amount": "35.00",
    "reason": "size issue",
    "success": True
}, session_id="sess_123")
```

---

## ⚙️ **Configuration**

### Configuration Dictionary Structure

```python
config = {
    # Required: Shopify API
    'SHOPIFY_ADMIN_TOKEN': 'shpat_your_token_here',
    'SHOPIFY_STORE_DOMAIN': 'your-store.myshopify.com',
    
    # Required: OpenAI API
    'OPENAI_API_KEY': 'sk-your_key_here',
    
    # Optional: OpenAI Configuration
    'OPENAI_MODEL': 'gpt-4.1-mini-2025-04-14',
    'OPENAI_MAX_TOKENS': '1000',
    'OPENAI_TEMPERATURE': '0.7',
    'OPENAI_PROJECT_ID': '',  # Optional
    'OPENAI_ORG_ID': '',      # Optional
    
    # Optional: Business Rules
    'RETURN_WINDOW_DAYS': '30',
    'ALLOW_FINAL_SALE_RETURNS': 'false',
    'REQUIRE_TAGS_FOR_RETURN': 'true',
    
    # Optional: Logging
    'LOG_LEVEL': 'INFO',
    'LOG_DIRECTORY': 'logs'
}
```

### Environment Variable Loading

```python
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Build config from environment
config = {
    'SHOPIFY_ADMIN_TOKEN': os.getenv('SHOPIFY_ADMIN_TOKEN'),
    'SHOPIFY_STORE_DOMAIN': os.getenv('SHOPIFY_STORE_DOMAIN'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    # ... other variables
}
```

---

## 🌍 **Environment Variables**

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SHOPIFY_ADMIN_TOKEN` | Shopify Admin API access token | `shpat_abc123...` |
| `SHOPIFY_STORE_DOMAIN` | Store domain with .myshopify.com | `store.myshopify.com` |
| `OPENAI_API_KEY` | OpenAI API key for LLM functionality | `sk-abc123...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_MODEL` | `gpt-4.1-mini-2025-04-14` | OpenAI model to use |
| `OPENAI_MAX_TOKENS` | `1000` | Maximum response tokens |
| `OPENAI_TEMPERATURE` | `0.7` | Model creativity (0.0-1.0) |
| `OPENAI_PROJECT_ID` | _(empty)_ | OpenAI project ID (optional) |
| `OPENAI_ORG_ID` | _(empty)_ | OpenAI organization ID (optional) |
| `RETURN_WINDOW_DAYS` | `30` | Return policy window in days |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_DIRECTORY` | `logs` | Directory for log files |

---

## ❌ **Error Handling**

### Exception Types

#### `ShopifyAPIError`
```python
class ShopifyAPIError(Exception):
    """Raised when Shopify API calls fail"""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
```

#### `PolicyViolationError`
```python
class PolicyViolationError(Exception):
    """Raised when return request violates business rules"""
    
    def __init__(self, message: str, policy_details: dict = None):
        super().__init__(message)
        self.policy_details = policy_details
```

#### `OpenAIError`
```python
class OpenAIError(Exception):
    """Raised when OpenAI API calls fail"""
    
    def __init__(self, message: str, error_type: str = None):
        super().__init__(message)
        self.error_type = error_type
```

### Error Handling Patterns

```python
try:
    agent = LLMReturnsChatAgent(config)
    response = agent.process_message("return order #1001")
    
except ShopifyAPIError as e:
    print(f"Shopify API error: {e}")
    if e.status_code == 429:
        # Handle rate limiting
        time.sleep(60)
    
except PolicyViolationError as e:
    print(f"Return policy violation: {e}")
    # Offer alternative solutions
    
except OpenAIError as e:
    print(f"OpenAI error: {e}")
    # Fallback to rule-based responses
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log error and graceful degradation
```

---

## 🧪 **Testing Reference**

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_order_lookup.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run tests with debug output
python -m pytest tests/ -v -s
```

### Test Structure

```
tests/
├── test_order_lookup.py       # OrderLookup tool tests
├── test_policy_checker.py     # PolicyChecker tool tests  
├── test_refund_processor.py   # RefundProcessor tool tests
├── test_conversation_logger.py # ConversationLogger tests
├── test_llm_agent.py          # Main agent tests
├── test_cli.py                # CLI interface tests
├── conftest.py                # Shared test fixtures
└── fixtures/                  # Test data files
    ├── orders.json
    ├── customers.json
    └── responses.json
```

### Mock Usage

```python
import pytest
from unittest.mock import Mock, patch
from tools.order_lookup import OrderLookup

@pytest.fixture
def mock_shopify_response():
    return {
        "data": {
            "order": {
                "id": "gid://shopify/Order/1001",
                "name": "#1001",
                # ... order data
            }
        }
    }

@patch('requests.post')
def test_order_lookup(mock_post, mock_shopify_response):
    mock_post.return_value.json.return_value = mock_shopify_response
    
    lookup = OrderLookup("test_token", "test_store.myshopify.com")
    result = lookup.lookup_order_by_id("1001")
    
    assert result['name'] == "#1001"
    mock_post.assert_called_once()
```

---

## 🔌 **Integration Examples**

### Custom Tool Integration

```python
from tools.base_tool import BaseTool

class CustomTool(BaseTool):
    """Example custom tool implementation"""
    
    def __init__(self, config):
        super().__init__(config)
        self.name = "custom_tool"
    
    def process(self, **kwargs):
        """Process custom business logic"""
        # Your custom implementation
        return {"result": "success"}

# Register with agent
agent = LLMReturnsChatAgent(config)
agent.register_tool(CustomTool(config))
```

### Webhook Integration

```python
from flask import Flask, request, jsonify
from llm_returns_chat_agent import LLMReturnsChatAgent

app = Flask(__name__)
agent = LLMReturnsChatAgent(config)

@app.route('/webhook/chat', methods=['POST'])
def chat_webhook():
    data = request.json
    message = data.get('message', '')
    
    try:
        response = agent.process_message(message)
        return jsonify({"response": response, "success": True})
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Batch Processing

```python
def process_return_batch(returns_data: List[dict]) -> List[dict]:
    """Process multiple returns in batch"""
    agent = LLMReturnsChatAgent(config)
    results = []
    
    for return_request in returns_data:
        try:
            order_id = return_request['order_id']
            item_id = return_request['item_id']
            reason = return_request['reason']
            
            # Process return
            message = f"Return item {item_id} from order {order_id} because {reason}"
            response = agent.process_message(message)
            
            results.append({
                "order_id": order_id,
                "success": True,
                "response": response
            })
            
        except Exception as e:
            results.append({
                "order_id": return_request.get('order_id'),
                "success": False,
                "error": str(e)
            })
    
    return results
```

---

## 📊 **Performance Considerations**

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second=2):
    """Decorator to rate limit API calls"""
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# Usage
@rate_limit(calls_per_second=2)
def shopify_api_call():
    # API call implementation
    pass
```

### Caching

```python
from functools import lru_cache

class OrderLookup:
    @lru_cache(maxsize=100)
    def lookup_order_by_id(self, order_id: str) -> dict:
        """Cached order lookup to reduce API calls"""
        # Implementation with caching
        pass
```

---

**For more examples and advanced usage, see the [Architecture Guide](ARCHITECTURE.md) and [Contributing Guide](CONTRIBUTING.md).** 