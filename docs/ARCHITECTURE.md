# 🏗️ Architecture Guide

Deep technical overview of the Shopify Returns Chat Agent architecture, design decisions, and system interactions.

## 📋 **Table of Contents**

- [System Overview](#system-overview)
- [Core Architecture](#core-architecture)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Integration Patterns](#integration-patterns)
- [Scalability Design](#scalability-design)
- [Security Considerations](#security-considerations)
- [Performance Optimizations](#performance-optimizations)

## 🎯 **System Overview**

The Shopify Returns Chat Agent is a conversational AI system that bridges natural language interactions with e-commerce business logic. It combines OpenAI's function calling capabilities with specialized tools to automate the returns process.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                         │
│                    (Natural Language)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  CLI INTERFACE                             │
│  • Input validation     • Command processing              │
│  • Session management   • Error handling                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                LLM RETURNS CHAT AGENT                     │
│                    (Orchestrator)                          │
├─────────────────────────────────────────────────────────────┤
│  OpenAI GPT-4 + Function Calling                          │
│  • Conversation state management                           │
│  • Intent recognition and routing                          │
│  • Response generation and context                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   TOOL LAYER                              │
│              (Business Logic)                              │
├─────────────────────┬───────────────────────────────────────┤
│                     │                                       │
│  ┌─────────────┐   │   ┌─────────────┐   ┌─────────────┐   │
│  │OrderLookup  │   │   │PolicyChecker│   │RefundProc..│   │
│  │             │   │   │             │   │             │   │
│  │•GraphQL API │   │   │•Bus. Rules  │   │•Shopify API │   │
│  │•Validation  │   │   │•Eligibility │   │•Amount Calc │   │
│  └─────────────┘   │   └─────────────┘   └─────────────┘   │
│                     │                                       │
│  ┌─────────────┐   │                                       │
│  │Conversation │   │                                       │
│  │Logger       │   │                                       │
│  │             │   │                                       │
│  │•Audit Trail │   │                                       │
│  │•Analytics   │   │                                       │
│  └─────────────┘   │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                EXTERNAL APIS                               │
│                                                             │
│  ┌─────────────────┐        ┌─────────────────┐            │
│  │   Shopify       │        │    OpenAI       │            │
│  │   GraphQL       │        │   Functions     │            │
│  │                 │        │                 │            │
│  │• Orders API     │        │• GPT-4 Model    │            │
│  │• Customers API  │        │• Function Call  │            │
│  │• Refunds API    │        │• Context Mgmt   │            │
│  └─────────────────┘        └─────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## 🏛️ **Core Architecture**

### Design Principles

1. **Modular Design**: Each tool handles a specific business function
2. **Separation of Concerns**: Clear boundaries between AI logic and business rules
3. **Extensibility**: Easy to add new tools and integrations
4. **Testability**: Each component can be tested in isolation
5. **Configuration-Driven**: Behavior controlled through environment variables

### Core Components

#### 1. LLMReturnsChatAgent (Orchestrator)

```python
class LLMReturnsChatAgent:
    """
    Central orchestrator that manages:
    - OpenAI integration and function calling
    - Conversation state and context
    - Tool coordination and response generation
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.openai_client = self._initialize_openai()
        self.tools = self._initialize_tools()
        self.conversation_history = []
    
    def process_message(self, message: str) -> str:
        """
        Main processing pipeline:
        1. Add user message to context
        2. Generate OpenAI completion with function calling
        3. Execute any tool calls
        4. Generate final response
        5. Log conversation and actions
        """
```

**Key Responsibilities:**
- **Intent Recognition**: Understands user goals from natural language
- **Context Management**: Maintains conversation state across interactions
- **Tool Orchestration**: Determines which tools to call and in what order
- **Response Generation**: Creates natural language responses from tool outputs

#### 2. Tool Architecture

Each tool follows a consistent interface pattern:

```python
class BaseTool:
    """Base class for all tools with common interface."""
    
    def __init__(self, config: dict):
        self.config = config
        self.name = self._get_tool_name()
    
    def process(self, **kwargs) -> dict:
        """Main processing method - implemented by each tool."""
        raise NotImplementedError
    
    def get_function_schema(self) -> dict:
        """OpenAI function calling schema."""
        raise NotImplementedError
    
    def validate_input(self, **kwargs) -> bool:
        """Input validation - override if needed."""
        return True
```

## 🔧 **Component Design**

### OrderLookup Tool

**Purpose**: Handles all Shopify order-related queries

```python
class OrderLookup:
    """
    Responsibilities:
    - GraphQL query construction and execution
    - Order data validation and formatting
    - Customer access verification
    - Error handling for API failures
    """
    
    def lookup_order_by_id(self, order_id: str) -> dict:
        """
        Process:
        1. Sanitize order ID (remove #, validate format)
        2. Construct GraphQL query with required fields
        3. Execute API call with error handling
        4. Format response for downstream tools
        5. Cache result for session duration
        """
```

**GraphQL Query Pattern:**
```graphql
query GetOrder($orderId: ID!) {
  order(id: $orderId) {
    id
    name
    email
    createdAt
    totalPrice {
      amount
      currencyCode
    }
    lineItems(first: 50) {
      edges {
        node {
          id
          title
          quantity
          variant {
            title
            price {
              amount
              currencyCode
            }
          }
        }
      }
    }
  }
}
```

### PolicyChecker Tool

**Purpose**: Encapsulates all business rules for return eligibility

```python
class PolicyChecker:
    """
    Business Rules Engine:
    - Return window validation (configurable days)
    - Item condition requirements
    - Reason validation (size, defect, etc.)
    - Final sale and exception handling
    - Refund amount calculation
    """
    
    def check_return_eligibility(self, order_data: dict, item_id: str, reason: str) -> dict:
        """
        Evaluation Pipeline:
        1. Time-based eligibility (purchase date vs. current date)
        2. Item-specific rules (final sale, personalized items)
        3. Reason validation (acceptable return reasons)
        4. Customer history checks (abuse prevention)
        5. Amount calculation (partial refunds, restocking fees)
        """
```

**Rule Evaluation Engine:**
```python
def _evaluate_rules(self, context: dict) -> dict:
    """
    Rules are evaluated in priority order:
    1. Hard constraints (time limits, final sale)
    2. Soft constraints (reason validation)
    3. Business logic (amount calculations)
    4. Exceptions (VIP customers, special cases)
    """
    
    rules = [
        self._check_time_window,
        self._check_item_condition,
        self._check_return_reason,
        self._check_customer_status,
        self._calculate_refund_amount
    ]
    
    result = {"eligible": True, "checks": {}}
    
    for rule in rules:
        rule_result = rule(context)
        result["checks"][rule.__name__] = rule_result
        
        if not rule_result.get("passed", True):
            result["eligible"] = False
            result["reason"] = rule_result.get("reason")
            break
    
    return result
```

### RefundProcessor Tool

**Purpose**: Handles the actual refund processing through Shopify API

```python
class RefundProcessor:
    """
    Refund Processing Pipeline:
    - Amount validation and calculation
    - Shopify refund API integration
    - Transaction tracking and logging
    - Error handling and retry logic
    - Status monitoring and updates
    """
    
    def process_refund(self, order_id: str, line_item_id: str, amount: str, reason: str) -> dict:
        """
        Processing Steps:
        1. Pre-flight validation (amount, permissions)
        2. Construct refund request payload
        3. Execute Shopify refund API call
        4. Parse response and extract refund ID
        5. Log transaction for audit trail
        6. Return formatted result with tracking info
        """
```

**Shopify Refund API Integration:**
```python
def _execute_shopify_refund(self, payload: dict) -> dict:
    """
    API Call Structure:
    POST /admin/api/2023-10/orders/{order_id}/refunds.json
    
    Payload:
    {
        "refund": {
            "reason": "size",
            "notify": true,
            "note": "Customer service refund",
            "refund_line_items": [
                {
                    "line_item_id": "...",
                    "quantity": 1,
                    "reason": "size"
                }
            ],
            "transactions": [
                {
                    "parent_id": "...",
                    "amount": "19.99",
                    "kind": "refund",
                    "gateway": "manual"
                }
            ]
        }
    }
    """
```

### ConversationLogger Tool

**Purpose**: Comprehensive logging and analytics

```python
class ConversationLogger:
    """
    Logging Architecture:
    - Structured conversation logs (JSON format)
    - Action-specific logging (refunds, lookups)
    - Performance metrics (response times, success rates)
    - Error tracking and debugging information
    - Analytics data preparation
    """
    
    def log_conversation(self, session_id: str, user_message: str, agent_response: str, metadata: dict):
        """
        Log Structure:
        {
            "timestamp": "2024-03-15T10:30:00Z",
            "session_id": "sess_123",
            "message_id": "msg_456",
            "user_message": "I want to return order #1001",
            "agent_response": "I'll help you with that return...",
            "metadata": {
                "tools_called": ["order_lookup", "policy_checker"],
                "response_time_ms": 1250,
                "tokens_used": 150
            }
        }
        """
```

## 🔄 **Data Flow**

### Typical Return Request Flow

```
1. User Input: "I want to return the blue shirt from order #1001"
   │
   ▼
2. CLI Processing: Input validation, session management
   │
   ▼
3. LLM Agent: Intent recognition → "return_request"
   │
   ▼
4. OpenAI Function Calling:
   ├─ Function: "lookup_order"
   │  Parameters: {"order_id": "1001"}
   │
   ├─ Function: "check_policy"
   │  Parameters: {"order_data": {...}, "item": "blue shirt", "reason": "general"}
   │
   └─ Function: "process_refund" (if approved)
      Parameters: {"order_id": "1001", "line_item_id": "...", "amount": "35.00"}
   │
   ▼
5. Tool Execution (in sequence):
   │
   ├─ OrderLookup.lookup_order_by_id("1001")
   │  └─ GraphQL API call → Order data
   │
   ├─ PolicyChecker.check_return_eligibility(order_data, item_info, "general")
   │  └─ Business rules evaluation → Eligibility result
   │
   └─ RefundProcessor.process_refund("1001", "line_item_123", "35.00", "general")
      └─ Shopify Refund API → Refund confirmation
   │
   ▼
6. Response Generation:
   ├─ Aggregate tool results
   ├─ Generate natural language response
   └─ Include confirmation details and next steps
   │
   ▼
7. Logging:
   ├─ ConversationLogger.log_conversation(...)
   ├─ ConversationLogger.log_action("refund", {...})
   └─ Performance metrics collection
   │
   ▼
8. User Response: "Perfect! I've processed your return for $35.00..."
```

### Error Handling Flow

```
Error Detection (Any Stage)
│
├─ Network/API Errors
│  ├─ Retry logic (exponential backoff)
│  ├─ Fallback to cached data (if available)
│  └─ Graceful degradation message
│
├─ Business Rule Violations  
│  ├─ Policy explanation to user
│  ├─ Alternative options (store credit, exchanges)
│  └─ Escalation path (human agent)
│
├─ Data Validation Errors
│  ├─ Request clarification from user
│  ├─ Suggest correct format
│  └─ Provide examples
│
└─ System Errors
   ├─ Log detailed error information
   ├─ Generic user-friendly message
   └─ Automatic error reporting
```

## 🔌 **Integration Patterns**

### OpenAI Function Calling Integration

The system uses OpenAI's function calling feature to bridge natural language with structured tool calls:

```python
def _generate_openai_response(self, messages: List[dict]) -> dict:
    """
    Function calling configuration:
    - Tools are dynamically registered with schemas
    - GPT-4 determines which functions to call
    - Multiple function calls can be made in sequence
    - Responses are formatted for natural conversation
    """
    
    functions = [tool.get_function_schema() for tool in self.tools.values()]
    
    response = self.openai_client.chat.completions.create(
        model=self.config['OPENAI_MODEL'],
        messages=messages,
        functions=functions,
        function_call="auto",  # Let GPT-4 decide when to call functions
        temperature=float(self.config.get('OPENAI_TEMPERATURE', 0.7)),
        max_tokens=int(self.config.get('OPENAI_MAX_TOKENS', 1000))
    )
    
    return response
```

### Shopify API Integration Strategy

**GraphQL for Read Operations:**
- Single query for comprehensive order data
- Reduces API call count vs. REST
- Flexible field selection
- Built-in pagination support

**REST API for Write Operations:**
- Refund processing (no GraphQL mutation available)
- Webhook registration (future feature)
- Admin operations

**Authentication Pattern:**
```python
headers = {
    'X-Shopify-Access-Token': self.admin_token,
    'Content-Type': 'application/json'
}

# For GraphQL
url = f"https://{self.store_domain}/admin/api/2023-10/graphql.json"

# For REST API
url = f"https://{self.store_domain}/admin/api/2023-10/orders/{order_id}/refunds.json"
```

## 🚀 **Scalability Design**

### Current Architecture Scalability

The CLI-based architecture is designed to support the upcoming web deployment:

```python
# Current: Direct CLI instantiation
agent = LLMReturnsChatAgent(config)
response = agent.process_message(user_input)

# Future: Web service wrapper (Task 21)
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    agent = get_agent_instance()  # Singleton or pool
    response = await agent.process_message_async(request.message)
    return ChatResponse(response=response)
```

### Planned Scalability Improvements

**Phase 1: Web Service (Tasks 21-25)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│  FastAPI App    │────│ Agent Instances │
│   (Railway)     │    │   (Stateless)   │    │  (In-Memory)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  External APIs  │
                       │ (Shopify, OpenAI│
                       └─────────────────┘
```

**Phase 2: Distributed Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│  Chat Service   │────│  Agent Pool     │
└─────────────────┘    │   (FastAPI)     │    │  (Redis Queue)  │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Database      │    │  Tool Services  │
                       │ (Conversations) │    │ (Microservices) │
                       └─────────────────┘    └─────────────────┘
```

### Performance Optimizations

**Caching Strategy:**
```python
from functools import lru_cache
import redis

class CachingOrderLookup(OrderLookup):
    def __init__(self, config):
        super().__init__(config)
        self.redis_client = redis.Redis(url=config.get('REDIS_URL'))
    
    @lru_cache(maxsize=100)  # In-memory cache
    def lookup_order_by_id(self, order_id: str) -> dict:
        # Check Redis cache first
        cached = self.redis_client.get(f"order:{order_id}")
        if cached:
            return json.loads(cached)
        
        # Fetch from API if not cached
        result = super().lookup_order_by_id(order_id)
        
        # Cache for future requests (TTL: 1 hour)
        self.redis_client.setex(
            f"order:{order_id}", 
            3600, 
            json.dumps(result)
        )
        
        return result
```

**Connection Pooling:**
```python
import aiohttp

class AsyncShopifyClient:
    def __init__(self, config):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=10  # Per-host limit
            )
        )
    
    async def execute_graphql(self, query: str, variables: dict = None):
        async with self.session.post(
            f"https://{self.store_domain}/admin/api/2023-10/graphql.json",
            json={"query": query, "variables": variables},
            headers=self.headers
        ) as response:
            return await response.json()
```

## 🔒 **Security Considerations**

### API Key Management

```python
class SecureConfig:
    """Secure configuration management."""
    
    def __init__(self):
        self.required_vars = [
            'SHOPIFY_ADMIN_TOKEN',
            'SHOPIFY_STORE_DOMAIN', 
            'OPENAI_API_KEY'
        ]
    
    def validate_config(self, config: dict) -> dict:
        """Validate and sanitize configuration."""
        
        # Check required variables
        missing = [var for var in self.required_vars if not config.get(var)]
        if missing:
            raise ConfigurationError(f"Missing required vars: {missing}")
        
        # Validate token formats
        if not config['SHOPIFY_ADMIN_TOKEN'].startswith('shpat_'):
            raise ConfigurationError("Invalid Shopify token format")
        
        if not config['OPENAI_API_KEY'].startswith('sk-'):
            raise ConfigurationError("Invalid OpenAI API key format")
        
        # Sanitize domain
        domain = config['SHOPIFY_STORE_DOMAIN']
        if not domain.endswith('.myshopify.com'):
            config['SHOPIFY_STORE_DOMAIN'] = f"{domain}.myshopify.com"
        
        return config
```

### Input Validation and Sanitization

```python
class InputValidator:
    """Comprehensive input validation."""
    
    @staticmethod
    def validate_order_id(order_id: str) -> str:
        """Validate and sanitize order ID."""
        # Remove # prefix if present
        clean_id = order_id.lstrip('#')
        
        # Check format (numbers only)
        if not clean_id.isdigit():
            raise ValidationError("Order ID must be numeric")
        
        # Check reasonable length
        if len(clean_id) < 1 or len(clean_id) > 20:
            raise ValidationError("Invalid order ID length")
        
        return clean_id
    
    @staticmethod  
    def validate_email(email: str) -> str:
        """Validate email format."""
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
        
        return email.lower()
```

### Rate Limiting and Abuse Prevention

```python
from functools import wraps
import time

class RateLimiter:
    """API rate limiting to prevent abuse."""
    
    def __init__(self):
        self.requests = {}  # Track requests by session/IP
    
    def rate_limit(self, max_requests: int = 60, window_seconds: int = 60):
        """Decorator for rate limiting."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                session_id = kwargs.get('session_id', 'default')
                current_time = time.time()
                
                # Clean old entries
                self._cleanup_old_requests(current_time, window_seconds)
                
                # Check current rate
                session_requests = self.requests.get(session_id, [])
                recent_requests = [
                    req_time for req_time in session_requests 
                    if current_time - req_time < window_seconds
                ]
                
                if len(recent_requests) >= max_requests:
                    raise RateLimitError(
                        f"Rate limit exceeded: {max_requests} requests per {window_seconds} seconds"
                    )
                
                # Record this request
                recent_requests.append(current_time)
                self.requests[session_id] = recent_requests
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
```

### Data Privacy and Logging

```python
class PrivacyAwareLogger:
    """Logging with PII protection."""
    
    def __init__(self):
        self.pii_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
            (r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', '[CARD]'),
            (r'\b\d{3}-?\d{2}-?\d{4}\b', '[SSN]'),
        ]
    
    def sanitize_message(self, message: str) -> str:
        """Remove PII from log messages."""
        sanitized = message
        
        for pattern, replacement in self.pii_patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        return sanitized
    
    def log_conversation(self, user_message: str, agent_response: str, metadata: dict):
        """Log conversation with PII protection."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": self.sanitize_message(user_message),
            "agent_response": self.sanitize_message(agent_response),
            "metadata": metadata
        }
        
        # Write to secure log file
        with open('logs/conversations.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
```

## 📊 **Monitoring and Observability**

### Metrics Collection

```python
class MetricsCollector:
    """Application metrics for monitoring."""
    
    def __init__(self):
        self.metrics = {
            'conversation_count': 0,
            'successful_returns': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'tool_usage': {},
            'error_counts': {}
        }
    
    def record_conversation(self, duration_ms: float, tools_used: List[str], success: bool):
        """Record conversation metrics."""
        self.metrics['conversation_count'] += 1
        
        if success:
            self.metrics['successful_returns'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        # Update response time (rolling average)
        current_avg = self.metrics['average_response_time']
        count = self.metrics['conversation_count']
        new_avg = ((current_avg * (count - 1)) + duration_ms) / count
        self.metrics['average_response_time'] = new_avg
        
        # Track tool usage
        for tool in tools_used:
            self.metrics['tool_usage'][tool] = self.metrics['tool_usage'].get(tool, 0) + 1
    
    def record_error(self, error_type: str, error_details: str):
        """Record error for monitoring."""
        self.metrics['error_counts'][error_type] = self.metrics['error_counts'].get(error_type, 0) + 1
        
        # Log error details (sanitized)
        logger.error(f"Error [{error_type}]: {error_details}")
    
    def export_metrics(self) -> dict:
        """Export metrics for external monitoring."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.metrics,
            "health_status": self._get_health_status()
        }
    
    def _get_health_status(self) -> str:
        """Determine system health based on metrics."""
        error_rate = self.metrics['failed_requests'] / max(self.metrics['conversation_count'], 1)
        
        if error_rate > 0.1:  # >10% error rate
            return "unhealthy"
        elif error_rate > 0.05:  # >5% error rate
            return "degraded"
        else:
            return "healthy"
```

---

## 🔮 **Future Architecture Evolution**

### Phase 1: Web Service (Tasks 21-25)
- FastAPI wrapper around existing CLI architecture
- Stateless request/response model
- Session management via Redis or database
- Railway deployment with auto-scaling

### Phase 2: Microservices (Q2 2025)
- Individual services for each tool
- Event-driven architecture with message queues
- Database persistence layer
- Advanced monitoring and observability

### Phase 3: AI-Enhanced (Q3 2025)
- RAG system for dynamic policy understanding
- Vector database for conversation context
- Multi-model AI integration (text, image, voice)
- Real-time learning and adaptation

### Phase 4: Enterprise Platform (Q4 2025+)
- Multi-tenant architecture
- Plugin system for custom integrations
- Advanced analytics and business intelligence
- White-label and API marketplace capabilities

---

**This architecture provides a solid foundation for scaling from CLI to enterprise-grade platform while maintaining code quality, security, and performance.** 