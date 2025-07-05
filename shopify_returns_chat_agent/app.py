from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import uuid
import logging
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Sentry for comprehensive monitoring
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),  # You'll add this to your .env file
    environment=os.getenv("ENVIRONMENT", "production"),  # Set to 'development' for local testing
    integrations=[
        FastApiIntegration(auto_enabling_integrations=True),
        StarletteIntegration(),
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
    traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
    profiles_sample_rate=1.0,  # Enable profiling for performance insights
    release=os.getenv("SENTRY_RELEASE", "v0.1.0"),
    before_send=lambda event, hint: event if os.getenv("SENTRY_DSN") else None,  # Only send if DSN is configured
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Shopify Returns Chat API",
    description="API for handling returns and exchanges through conversational AI",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = None  # For better tracking
    shop_domain: Optional[str] = None  # For multi-tenant tracking

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.middleware("http")
async def add_sentry_context(request: Request, call_next):
    """Add custom context to Sentry for better error tracking."""
    # Set custom tags for this request
    sentry_sdk.set_tag("endpoint", str(request.url.path))
    sentry_sdk.set_tag("method", request.method)
    sentry_sdk.set_tag("service", "shopify-returns-chat")
    
    # Add user context if available (will be populated during chat)
    sentry_sdk.set_context("request", {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
    })
    
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    """Root endpoint - simple response"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Shopify Returns Chat API is running!",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with Sentry tracking"""
    try:
        # Track health checks in Sentry
        sentry_sdk.add_breadcrumb(
            message="Health check called",
            category="health",
            level="info"
        )
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "shopify-returns-agent",
            "version": "1.0.0"
        }
        
        # Send success event to Sentry
        sentry_sdk.capture_message("Health check successful", level="info")
        
        return health_status
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for the returns agent."""
    # Set up Sentry context for this chat interaction
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Add customer context to Sentry
    sentry_sdk.set_user({
        "id": request.customer_id,
        "conversation_id": conversation_id,
        "shop_domain": request.shop_domain,
    })
    
    # Set custom tags for this chat
    sentry_sdk.set_tag("conversation_id", conversation_id)
    sentry_sdk.set_tag("shop_domain", request.shop_domain or "unknown")
    sentry_sdk.set_tag("has_customer_id", bool(request.customer_id))
    
    # Add extra context
    sentry_sdk.set_context("chat_request", {
        "message_length": len(request.message),
        "conversation_id": conversation_id,
        "customer_id": request.customer_id,
        "shop_domain": request.shop_domain,
    })
    
    try:
        # Start a Sentry transaction for performance monitoring
        with sentry_sdk.start_transaction(op="chat", name="process_return_request"):
            logger.info(f"Processing chat request for conversation: {conversation_id}")
            
            # For now, return a simple response to test deployment
            # TODO: Replace with actual LLM integration
            
            response_text = f"Thanks for your message: '{request.message}'. The full returns agent will be connected once deployment is working!"
            
            # Log successful interaction
            logger.info(f"Chat response generated for conversation: {conversation_id}")
            
            return ChatResponse(
                response=response_text,
                conversation_id=conversation_id
            )
        
    except Exception as e:
        # Log error with context
        logger.error(f"Chat error for conversation {conversation_id}: {str(e)}")
        
        # Add error context to Sentry
        sentry_sdk.set_context("error_context", {
            "conversation_id": conversation_id,
            "error_type": type(e).__name__,
            "user_message": request.message,
        })
        
        # Capture exception in Sentry
        sentry_sdk.capture_exception(e)
        
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/sentry-debug")
async def trigger_error():
    """Debug endpoint to test Sentry integration (remove in production)."""
    logger.warning("Debug endpoint accessed - this will trigger a test error")
    sentry_sdk.set_tag("debug", "test_error")
    raise Exception("This is a test error for Sentry integration!")

# Add Railway deployment debugging endpoints
@app.get("/debug/railway")
async def railway_debug():
    """Debug endpoint specifically for Railway deployment issues"""
    try:
        # Send custom event to Sentry for Railway debugging
        sentry_sdk.add_breadcrumb(
            message="Railway debug endpoint called",
            category="railway",
            level="info"
        )
        
        debug_info = {
            "status": "Railway routing is working",
            "timestamp": datetime.utcnow().isoformat(),
            "port": os.getenv("PORT", "unknown"),
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "railway_service": os.getenv("RAILWAY_SERVICE_NAME", "unknown"),
            "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
        }
        
        # Track this as a custom Sentry event
        sentry_sdk.capture_message("Railway debug endpoint successfully accessed", level="info")
        
        return debug_info
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

# Add startup event tracking
@app.on_event("startup")
async def startup_event():
    """Track application startup in Sentry"""
    sentry_sdk.capture_message("FastAPI application starting up", level="info")
    sentry_sdk.set_tag("railway.startup", "success")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port) 