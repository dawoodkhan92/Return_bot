# 💬 CLI Usage Guide

This guide covers everything you need to know about using the Shopify Returns Chat Agent from the command line. Perfect for store managers, customer service teams, and developers.

## 🚀 **Getting Started**

### Quick Start
```bash
# Navigate to the chat agent directory
cd shopify_returns_chat_agent

# Start the chat agent
python llm_chat.py

# You'll see:
🤖 Initializing LLM-powered Returns Chat Agent...
✅ Agent initialized successfully!
====================================
🛍️ SHOPIFY RETURNS CHAT AGENT 🛍️
====================================
Type 'help' for commands or 'exit' to quit.

Agent: Hello! I'm here to help you with returns and exchanges. 
Please provide your order number, email, or tell me what you'd like to return.
```

## 🎯 **Core Usage Patterns**

### 1. **Standard Return Request** (Most Common)
```
You: Hi, I need to return order #1001

Agent: I'd be happy to help you with your return! Let me look up order #1001.

🔍 Found your order! Here are the details:
- Order #1001 (placed 2 days ago)
- Customer: john@example.com
- Items: Blue T-Shirt (Size M), Black Jeans (Size 32)
- Total: $85.00

Which item(s) would you like to return?

You: The blue t-shirt doesn't fit

Agent: I understand you'd like to return the Blue T-Shirt due to fit issues. 

✅ Good news! This item is eligible for return:
- Within our 30-day return window (2 days old)
- Item condition: Eligible for return
- Return reason: Size/fit issue (approved)

I can process this return for you. The refund amount will be $35.00.
Would you like me to proceed with the return?

You: Yes please

Agent: Perfect! I've processed your return:

🎉 Return Processed Successfully!
- Order: #1001
- Item: Blue T-Shirt (Size M)
- Refund Amount: $35.00
- Refund Method: Original payment method
- Processing Time: 3-5 business days

You should receive a return confirmation email shortly. Is there anything else I can help you with?
```

### 2. **Email-Based Order Lookup**
```
You: I want to return something but don't have my order number. My email is jane@example.com

Agent: No problem! Let me look up orders associated with jane@example.com.

🔍 I found these recent orders for your email:
1. Order #1002 - $120.00 (5 days ago) - Red Dress, Black Shoes
2. Order #1003 - $65.00 (12 days ago) - White Hoodie

Which order contains the item you'd like to return?

You: Order 1002, the dress

Agent: Great! I found Order #1002. Let me check the return eligibility for the Red Dress...

[Continues with standard return flow]
```

### 3. **Policy Questions**
```
You: What's your return policy?

Agent: Here's our return policy summary:

📋 RETURN POLICY OVERVIEW:
• Return Window: 30 days from purchase date
• Condition: Items must be unworn, with tags attached
• Refund Method: Original payment method
• Processing Time: 3-5 business days
• Shipping: Customer responsible for return shipping

❌ NON-RETURNABLE ITEMS:
• Final sale items
• Personalized/custom items  
• Intimate apparel
• Items without tags

Would you like help with a specific return, or do you have questions about returning a particular type of item?
```

## 🛠️ **Built-in Commands**

### Help Commands
```
You: help
# Shows all available commands and features

You: commands  
# Alternative to 'help'

You: ?
# Quick help shortcut
```

### Utility Commands
```
You: exit
# Gracefully exit the chat agent

You: quit
# Alternative to 'exit'

You: clear
# Clear the conversation history (starts fresh)

You: restart
# Restart the agent (useful if something goes wrong)
```

### Diagnostic Commands
```
You: status
# Check agent status and configuration

You: test
# Run basic connectivity tests (Shopify + OpenAI)

You: debug
# Enable detailed logging (for troubleshooting)
```

## 🔧 **Advanced Features**

### 1. **Batch Processing**
```
You: I need to return multiple items from order #1001

Agent: I'll help you return multiple items! Let me pull up order #1001...

Found order #1001 with items:
1. Blue T-Shirt - $35.00
2. Black Jeans - $50.00
3. Red Hat - $25.00

Which items would you like to return? You can say:
- "Items 1 and 3" 
- "The t-shirt and hat"
- "Everything except the jeans"

You: Items 1 and 3

Agent: Perfect! I'll process returns for:
- Blue T-Shirt ($35.00) 
- Red Hat ($25.00)
Total refund: $60.00

[Continues with confirmation and processing]
```

### 2. **Complex Return Scenarios**
```
You: I want to return something but it's been 45 days

Agent: I understand you'd like to process a return for an item that's 45 days old. 
Our standard policy is 30 days, but let me check if there are any exceptions...

⚠️ POLICY EXCEPTION DETECTED:
- Item is 15 days past our standard 30-day window
- However, I can make a note for manual review by our customer service team

Would you like me to:
1. Submit for manual review (may take 24-48 hours)
2. Check if you're eligible for store credit instead
3. Explore other options

You: Submit for review please

Agent: I've submitted your return request for manual review:

📤 SUBMITTED FOR REVIEW:
- Case #: RET-2024-001234
- Reason: Outside standard return window
- Expected Response: 24-48 hours
- Contact: You'll receive an email update

Is there anything else I can help you with today?
```

## 🎭 **Conversation Style Guide**

### What Works Well
✅ **Natural language**: "I want to return the blue shirt from last week"
✅ **Order numbers**: "Return order #1001" or "#1001"
✅ **Email addresses**: "Look up orders for john@example.com"
✅ **Specific items**: "Return the t-shirt" or "the jeans don't fit"
✅ **Clear reasons**: "Wrong size", "defective", "changed my mind"

### Common Patterns
```
# Starting a return
"I need to return something"
"Return order #1001"
"I want to return the shirt I bought"

# Providing order info
"Order number is 1001"
"My email is user@example.com"
"I bought it last Tuesday"

# Describing items
"The blue t-shirt"
"Item #2 from my order"
"The shoes are too small"

# Confirming actions
"Yes, process the return"
"That's correct"
"No, cancel that"
```

## 🚨 **Error Handling & Troubleshooting**

### Common Issues

#### ❌ **"Order not found"**
```
Agent: I'm sorry, I couldn't find order #1001. This could be because:
- The order number might be incorrect
- The order might be from a different store
- There might be a typing error

Could you double-check the order number, or provide your email address 
so I can search for recent orders?
```

#### ❌ **"Item not eligible for return"**
```
Agent: I'm sorry, but this item isn't eligible for return because:
- It's past our 30-day return window (purchased 45 days ago)
- It's marked as final sale
- It's a personalized item

However, I can check if there are other options available, such as:
- Store credit
- Exchange for different size
- Escalation to customer service

Would you like me to explore these alternatives?
```

#### ❌ **"API connection issues"**
```
Agent: I'm experiencing some connectivity issues right now. Let me try again...

🔄 Retrying connection to Shopify...

If this continues, you can:
1. Try again in a few minutes
2. Contact our customer service directly at support@yourstore.com
3. Use the web interface (if available)

I apologize for the inconvenience!
```

### Debug Mode
```bash
# Run with debug logging
python llm_chat.py --debug

# Shows detailed information:
[DEBUG] Loading environment variables...
[DEBUG] Connecting to Shopify API...
[DEBUG] OpenAI API initialized...
[DEBUG] User input: "Return order #1001"
[DEBUG] Calling OrderLookup tool with order_id: 1001
[DEBUG] Order lookup successful, found order data
[DEBUG] Generating AI response...
```

## 🎯 **Best Practices**

### For Customer Service Teams
1. **Start with order number** when available (fastest lookup)
2. **Use email search** when customers don't have order numbers
3. **Be specific about items** to avoid confusion with multi-item orders
4. **Confirm details** before processing refunds
5. **Explain policies clearly** using the agent's built-in explanations

### For Store Managers
1. **Use the test command** regularly to verify connectivity
2. **Monitor conversation logs** in the logs/ directory
3. **Train staff** on common conversation patterns
4. **Review edge cases** and escalate to development team
5. **Update return policies** as needed in the configuration

### For Developers
1. **Use debug mode** when troubleshooting
2. **Check logs** in the logs/ directory for issues
3. **Test API credentials** regularly
4. **Monitor response times** and error rates
5. **Implement graceful degradation** for API failures

## 📊 **Performance Tips**

### Optimize Response Time
- Provide **order numbers** when possible (faster than email search)
- Be **specific about items** to avoid back-and-forth clarification
- Use **clear return reasons** to speed up policy checking

### Reduce API Calls
- The agent **caches order data** during conversations
- Multiple returns from the **same order** are processed efficiently
- **Batch operations** when returning multiple items

## 🔮 **Coming Soon (Web Interface)**

The CLI interface is the foundation for upcoming web features:

🚀 **Phase 1 (Tasks 21-25):**
- **Web-based chat interface** (same conversation style)
- **Customer self-service portal** 
- **Admin dashboard** for tracking returns
- **Email notifications** for return confirmations

🚀 **Phase 2 (Future):**
- **Mobile app integration**
- **Shopify store widget**
- **Multi-language support**
- **Advanced analytics dashboard**

---

## 📞 **Getting Help**

### If you encounter issues:
1. **Try the help command**: Type `help` in the chat
2. **Check the troubleshooting section** above
3. **Review the [Installation Guide](INSTALLATION.md)** for setup issues
4. **Check [GitHub Issues](https://github.com/your-username/shopify-returns-chat-agent/issues)**
5. **Open a new issue** with conversation logs (remove sensitive data)

### For feature requests:
- Check the [Roadmap](../README.md#roadmap) first
- Open a [GitHub Discussion](https://github.com/your-username/shopify-returns-chat-agent/discussions)
- Tag issues with `enhancement` label

---

**Ready to start chatting?** 
```bash
python llm_chat.py
```

The agent is designed to be intuitive - just talk to it naturally about returns! 🎉 