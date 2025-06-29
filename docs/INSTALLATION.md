# 🚀 Installation Guide

This guide will walk you through setting up the Shopify Returns Chat Agent on your system. Follow these steps to get up and running quickly.

## 📋 **Prerequisites**

Before you begin, ensure you have:

### System Requirements
- **Python 3.8 or higher** ([Download Python](https://python.org/downloads/))
- **Git** ([Download Git](https://git-scm.com/downloads))
- **A Shopify store** with Admin API access
- **OpenAI API account** ([Sign up](https://platform.openai.com/))

### Knowledge Requirements
- Basic familiarity with command-line interface
- Shopify store admin access
- Basic understanding of API keys (we'll guide you through setup)

## 🛠️ **Step 1: Clone the Repository**

```bash
# Clone the repository
git clone https://github.com/your-username/shopify-returns-chat-agent.git

# Navigate to the project directory
cd shopify-returns-chat-agent
```

## 🐍 **Step 2: Python Environment Setup**

### Option A: Using Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Navigate to the chat agent directory
cd shopify_returns_chat_agent

# Install required packages
pip install -r requirements.txt
```

### Option B: Using Conda

```bash
# Create a new conda environment
conda create --name returns-agent python=3.8

# Activate the environment
conda activate returns-agent

# Navigate to the chat agent directory
cd shopify_returns_chat_agent

# Install required packages
pip install -r requirements.txt
```

## 🔑 **Step 3: API Credentials Setup**

### 3.1 Shopify Admin API Setup

1. **Access your Shopify Admin Panel**
   - Go to your store's admin URL (e.g., `your-store.myshopify.com/admin`)

2. **Navigate to App Development**
   - Click **Settings** → **Apps and sales channels**
   - Click **Develop apps** (or **App and sales channel settings**)

3. **Create a Private App**
   - Click **Create an app**
   - Enter app name: "Returns Chat Agent"
   - Enter app URL: `https://localhost` (for development)

4. **Configure Admin API Access**
   - Click **Configure Admin API scopes**
   - Enable the following permissions:
     - ✅ `read_orders` - Read order information
     - ✅ `write_orders` - Process refunds
     - ✅ `read_customers` - Look up customer information
     - ✅ `read_products` - Validate product information

5. **Install the App**
   - Click **Install app**
   - Copy the **Admin API access token** (keep this secure!)

### 3.2 OpenAI API Setup

1. **Create OpenAI Account**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in to your account

2. **Generate API Key**
   - Go to [API Keys](https://platform.openai.com/api-keys)
   - Click **Create new secret key**
   - Give it a name: "Returns Chat Agent"
   - Copy the key (it won't be shown again!)

3. **Add Billing Information**
   - Go to [Billing](https://platform.openai.com/account/billing)
   - Add a payment method
   - OpenAI uses usage-based pricing (typically $0.01-0.03 per conversation)

## ⚙️ **Step 4: Environment Configuration**

1. **Copy the example environment file**
   ```bash
   cp env.example .env
   ```

2. **Edit the .env file**
   Open `.env` in your text editor and add your credentials:
   
   ```env
   # Required: Shopify Admin API credentials
   SHOPIFY_ADMIN_TOKEN="shpat_your_actual_token_here"
   SHOPIFY_STORE_DOMAIN="your-store.myshopify.com"
   
   # Required: OpenAI API credentials  
   OPENAI_API_KEY="sk-your_actual_openai_key_here"
   
   # Optional: Advanced configuration (use defaults)
   OPENAI_MODEL="gpt-4.1-mini-2025-04-14"
   OPENAI_MAX_TOKENS="1000"
   OPENAI_TEMPERATURE="0.7"
   ```

3. **Secure your .env file**
   ```bash
   # Make sure .env is in .gitignore (it should be by default)
   echo ".env" >> .gitignore
   ```

## ✅ **Step 5: Test Installation**

### 5.1 Verify Dependencies
```bash
# Check Python version
python --version
# Should show Python 3.8 or higher

# Verify packages are installed
pip list | grep -E "(requests|openai|pytest)"
```

### 5.2 Test Environment Configuration
```bash
# Run the environment validation
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('✅ SHOPIFY_ADMIN_TOKEN:', 'SET' if os.getenv('SHOPIFY_ADMIN_TOKEN') else '❌ MISSING')
print('✅ SHOPIFY_STORE_DOMAIN:', 'SET' if os.getenv('SHOPIFY_STORE_DOMAIN') else '❌ MISSING')
print('✅ OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else '❌ MISSING')
"
```

### 5.3 Run the Chat Agent
```bash
# Start the chat agent
python llm_chat.py

# You should see:
# 🤖 Initializing LLM-powered Returns Chat Agent...
# ✅ Agent initialized successfully!
```

### 5.4 Quick Test Conversation
```
Agent: Hello! I'm here to help you with returns and exchanges...

You: help
# Should show the help menu

You: exit
# Should exit gracefully
```

## 🧪 **Step 6: Run Tests (Optional but Recommended)**

```bash
# Run the test suite to verify everything works
python -m pytest tests/ -v

# Expected output:
# =================== test session starts ===================
# ... tests/test_order_lookup.py::test_successful_order_lookup PASSED
# ... tests/test_policy_checker.py::test_within_return_window PASSED
# ... [more tests]
# =================== X passed in Y.XXs ===================
```

## 🚨 **Troubleshooting**

### Common Issues and Solutions

#### ❌ **"Module not found" errors**
```bash
# Make sure you're in the right directory
cd shopify_returns_chat_agent

# Reinstall dependencies
pip install -r requirements.txt
```

#### ❌ **"Invalid API credentials" error**
- Double-check your `.env` file has the correct tokens
- Ensure no extra spaces around the `=` sign
- Verify your Shopify app has the correct permissions
- Test your OpenAI API key at [OpenAI Playground](https://platform.openai.com/playground)

#### ❌ **"Permission denied" errors on Shopify**
- Verify your private app has `read_orders`, `write_orders`, and `read_customers` permissions
- Make sure the app is installed and active

#### ❌ **Python version issues**
```bash
# Check your Python version
python --version

# If using multiple Python versions, try:
python3 llm_chat.py
# or
python3.8 llm_chat.py
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs** - Run with `--debug` flag: `python llm_chat.py --debug`
2. **Review the [CLI Usage Guide](CLI_USAGE.md)** for common commands
3. **Search [GitHub Issues](https://github.com/your-username/shopify-returns-chat-agent/issues)**
4. **Open a new issue** with:
   - Your operating system
   - Python version
   - Error messages (remove any API keys!)
   - Steps to reproduce

## 🎉 **Next Steps**

Congratulations! You've successfully installed the Shopify Returns Chat Agent. 

**What's next:**
- 📖 Read the **[CLI Usage Guide](CLI_USAGE.md)** to learn all available features
- 🏗️ Explore the **[Architecture Guide](ARCHITECTURE.md)** to understand how it works
- 🤝 Check out **[Contributing Guide](CONTRIBUTING.md)** if you want to help improve the project
- 🗺️ See the **Roadmap** in the main README for upcoming features

**Start chatting:**
```bash
python llm_chat.py
```

---

**Need help?** Join our community discussions or open an issue on GitHub! 