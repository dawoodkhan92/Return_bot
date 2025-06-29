# shopify_returns_chat_agent

---

- **Purpose:** Provide a conversational AI agent (CLI-first, later web widget) that guides customers through returns/exchanges by connecting to Shopify. It can look up orders, check return policy, and process refunds, lowering support load for apparel stores.

- **Communication Flows:**
    - **User ⇄ ReturnsChatAgent:**
        - User types messages in CLI (or HTTP JSON). Agent replies conversationally.
    - **Agent → Tools:**
        - Calls OrderLookup, PolicyChecker, RefundProcessor, ConversationLogger.
    - **Agent → Shopify:**
        - Uses Admin API token to fetch orders & create refunds.

---

## ReturnsChatAgent

### Role within the Agency
Conversational assistant that handles the end-to-end return process: collects order info, validates policy, and processes refunds, while logging each step.

### Tools

- **OrderLookup**
    - **Description:** Fetch order details from Shopify Admin API.
    - **Inputs:** `order_id` (str), `email` (str)
    - **Validation:** At least one identifier; verify order exists.
    - **Core Functions:** GraphQL query to retrieve order JSON.
    - **APIs:** Shopify Admin API (GraphQL).
    - **Output:** Order JSON or `{"error": "not_found"}`.

- **PolicyChecker** (reuse existing logic)
    - **Description:** Determine if the return meets store policy.
    - **Inputs:** `order_date`, `item_id`, `return_reason`
    - **Output:** `{ decision: approve/deny/flag, reason: str }`

- **RefundProcessor** (reuse, add API call)
    - **Description:** Initiate refund for approved items.
    - **Inputs:** `order_id`, `amount`, `item_id`
    - **Core:** Shopify Admin API mutation `refundCreate`.
    - **Output:** Confirmation JSON or error.

- **ConversationLogger**
    - **Description:** Persist each message/action/decision for audit.
    - **Inputs:** conversation_id, user_msg, agent_msg, tool_calls
    - **Core:** Append JSON lines to log file.

---

## MVP Build Steps
1. Implement OrderLookup tool.
2. Refactor PolicyChecker & RefundProcessor into unified tool interface.
3. Create ConversationLogger.
4. Build ReturnsChatAgent (rule-based first; later OpenAI function-calling).
5. CLI driver `chat.py` for local testing.
6. Add unit tests with Shopify API mocks.

---

## Environment Variables
- `SHOPIFY_ADMIN_TOKEN`
- `SHOPIFY_STORE_DOMAIN`
- `OPENAI_API_KEY` (optional for LLM phase)

---

## Future Extensions
- Plug into web chat widget.
- Return-label creation.
- Email/SMS notifications.
- Enhanced analytics dashboard. 