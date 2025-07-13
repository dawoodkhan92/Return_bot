# AI-Powered E-commerce Returns Agent

This project is a sophisticated, AI-powered chatbot designed to fully automate the customer returns process for e-commerce platforms like Shopify. It functions as an autonomous agent that handles customer return requests from start to finish through an embeddable web chat widget.

## ✨ Features

- **Conversational AI:** Customers use natural language to initiate and process returns.
- **Automated Order Verification:** Connects to the Shopify API to look up and verify order details.
- **Dynamic Policy Enforcement:** Checks return eligibility against configurable store policies (e.g., 30-day return window).
- **End-to-End Processing:** Capable of processing refunds directly through the Shopify API.
- **Web Integration:** Includes a self-contained frontend widget that can be embedded into any online store.

## 🚀 Getting Started

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

- Python 3.8+
- Git
- A Shopify store with Admin API access
- An OpenAI API key

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/shopify-returns-chat-agent.git
    cd shopify-returns-chat-agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt

    # For development, install the testing dependencies as well:
    pip install -r requirements-dev.txt
    ```

### 3. Configuration

1.  **Create an environment file** by copying the example:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** with your credentials:
    ```env
    # Required: Shopify Admin API credentials
    SHOPIFY_ADMIN_TOKEN="shpat_your_actual_token_here"
    SHOPIFY_STORE_DOMAIN="your-store.myshopify.com"

    # Required: OpenAI API credentials
    OPENAI_API_KEY="sk-your_actual_openai_key_here"

    # Optional: Sentry for error monitoring
    SENTRY_DSN=""
    ```

### 4. Running the Application

The application can be run in two ways:

1.  **As a CLI Chatbot (for testing):**
    ```bash
    python scripts/llm_chat.py
    ```

2.  **As a Web Service (for web widget integration):**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    You can then access the API at `http://localhost:8000`.

## Project Structure

Here is an overview of the key files and directories:

-   `main.py`: The main entry point for the FastAPI web application.
-   `shopify_returns_chat_agent/`: The core application package.
    -   `app.py`: Defines the FastAPI application and its endpoints.
    -   `llm_returns_chat_agent.py`: Contains the primary logic for the AI agent.
    -   `tools/`: Holds the tools the agent uses, such as `order_lookup.py` and `refund_processor.py`.
    -   `frontend/`: Contains the embeddable web chat widget.
-   `scripts/`: Contains supplementary scripts, like the CLI chat client.
-   `tests/`: Contains all the tests for the application.
-   `docs/`: Contains all project documentation.
-   `requirements.txt`: Core application dependencies.
-   `requirements-dev.txt`: Development and testing dependencies.
-   `Procfile` & `railway.json`: Configuration for Railway deployment.

## 🧪 Running Tests

To run the full test suite, use pytest:

```bash
python -m pytest
```

## 📚 Documentation

For more detailed information, please see the following documents:

- **[Architecture Guide](./docs/ARCHITECTURE.md):** A deep dive into the system architecture.
- **[Installation Guide](./docs/INSTALLATION.md):** Detailed setup instructions.
- **[API Reference](./docs/API_REFERENCE.md):** API endpoint documentation.
- **[Agent README](./docs/AGENT_README.md):** The original README for the agent.
- **[Deployment Guide](./docs/DEPLOYMENT.md):** Instructions for deploying the application.
- **[Integration Guide](./docs/INTEGRATION_GUIDE.md):** A guide for integrating the chat widget.
- **[Product Requirements](./docs/PRODUCT_REQUIREMENTS.md):** The product requirements document.
