# Shopify Returns Chat API

A FastAPI web service for handling Shopify returns and exchanges through conversational AI.

## Features

- RESTful API for interacting with an AI returns processing agent
- Stateless architecture for cloud deployment
- Conversation persistence through logs
- Railway-ready deployment configuration

## Setup

### Prerequisites

- Python 3.8+
- Shopify Admin API access
- OpenAI API key

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy `env.example` to `.env` and fill in your API keys):

```
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o
SHOPIFY_ADMIN_TOKEN=your-shopify-token
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
PORT=8080
```

## Running Locally

```bash
# Start the server
uvicorn app:app --host 0.0.0.0 --port 8080

# Run self-test
python app.py --test
```

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "environment_configured": true
}
```

### Chat

```
POST /chat
```

Request:
```json
{
  "message": "I want to return my order",
  "conversation_id": "optional-existing-conversation-id"
}
```

Response:
```json
{
  "conversation_id": "unique-conversation-id",
  "response": "I'd be happy to help you with your return. Could you please provide your order number?",
  "status": "success",
  "metadata": {
    "context": {}
  }
}
```

## Railway Deployment

This project includes configuration files for deployment on [Railway](https://railway.app/):

1. `railway.json` - Railway configuration
2. `Procfile` - Process management
3. `.dockerignore` - Files to exclude from deployment

To deploy to Railway:

1. Push this code to GitHub
2. Connect your GitHub repository to Railway
3. Set the required environment variables in Railway dashboard
4. Deploy! 