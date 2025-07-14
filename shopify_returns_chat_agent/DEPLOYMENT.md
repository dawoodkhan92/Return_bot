# Railway Deployment Guide

This guide covers deploying the Shopify Returns Chat API to Railway.

## Prerequisites

1. Railway account at [railway.app](https://railway.app/)
2. GitHub repository with this code
3. Required API keys:
   - Shopify Admin API token
   - OpenAI API key

## Deployment Steps

### 1. Prepare Repository

Ensure your repository has these files:
- `railway.json` - Railway configuration
- `Procfile` - Process management
- `requirements.txt` - Python dependencies
- `.dockerignore` - Docker build optimization
- `.env.example` - Environment variable template

### 2. Create Railway Project

1. Go to [railway.app](https://railway.app/) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Select the `shopify_returns_chat_agent` directory as the root

### 3. Configure Environment Variables

In Railway dashboard, add these environment variables:

```bash
# Required
SHOPIFY_ADMIN_TOKEN=your_shopify_admin_token_here
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
OPENAI_API_KEY=your_openai_api_key_here

# Optional (with defaults)
OPENAI_MODEL=gpt-4o
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 4. Deploy

Railway will automatically:
1. Build using the configuration in `railway.json`
2. Install dependencies from `requirements.txt`
3. Start the service using the `Procfile`
4. Run health checks on `/health`

## Testing Deployment

### Local Testing

```bash
# Test the application locally
python app.py --test

# Run with Railway environment simulation
railway run python app.py --test
```

### Production Testing

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-app-name.railway.app/health

# Chat endpoint
curl -X POST https://your-app-name.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to return my order"}'
```

Expected responses:

**Health Check:**
```json
{
  "status": "healthy",
  "environment_configured": true
}
```

**Chat:**
```json
{
  "conversation_id": "unique-id",
  "response": "I'd be happy to help you with your return...",
  "status": "success",
  "metadata": {...}
}
```

## Monitoring

Railway provides:
- Application logs
- Metrics and monitoring
- Automatic restarts on failure
- Health check monitoring

Access these through the Railway dashboard.

## Troubleshooting

### Common Issues

1. **Environment Variables Missing**
   - Check Railway dashboard for all required vars
   - Verify variable names match exactly

2. **Health Check Failing**
   - Check application logs for startup errors
   - Verify dependencies are installed correctly

3. **CORS Issues**
   - Update `ALLOWED_ORIGINS` environment variable
   - Check that origins are comma-separated

4. **Port Issues**
   - Railway automatically sets `$PORT` - don't override
   - Application listens on `0.0.0.0:$PORT`

### Logs

View logs in Railway dashboard or using CLI:
```bash
railway logs
```

## Configuration Details

### railway.json
- Uses NIXPACKS builder for Python apps
- Health checks on `/health` endpoint
- Automatic restarts on failure
- 100-second health check timeout

### Procfile
- Defines web process command
- Uses uvicorn ASGI server
- Binds to Railway's dynamic port

### Dependencies
- FastAPI for web framework
- Uvicorn for ASGI server
- Gunicorn for production deployment
- All required application dependencies 