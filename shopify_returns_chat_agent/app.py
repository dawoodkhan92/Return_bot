from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import uuid
import logging
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# Import the LLM Returns Chat Agent
from llm_returns_chat_agent import LLMReturnsChatAgent

# Load environment variables
load_dotenv()

# Try to import and initialize Sentry - make it completely optional
SENTRY_AVAILABLE = False
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    # Only initialize if DSN is provided
    if os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            environment=os.getenv("ENVIRONMENT", "production"),
            integrations=[
                FastApiIntegration(),
                StarletteIntegration(),
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            ],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            release=os.getenv("SENTRY_RELEASE", "v0.1.0"),
        )
        SENTRY_AVAILABLE = True
        print("✅ Sentry monitoring initialized")
    else:
        print("⚠️ Sentry DSN not found - monitoring disabled")
except ImportError:
    print("⚠️ Sentry SDK not available - monitoring disabled")
except Exception as e:
    print(f"⚠️ Sentry initialization failed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Shopify Returns Chat API",
    description="API for handling returns and exchanges through conversational AI",
    version="0.1.0"
)

# Configure CORS - more restrictive for production
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve widget.js at root path for Shopify integration
@app.get("/widget.js")
async def serve_widget():
    """Serve the widget.js file for Shopify integration"""
    widget_path = Path(__file__).parent / "frontend" / "widget.js"
    if widget_path.exists():
        return FileResponse(widget_path, media_type="application/javascript")
    else:
        raise HTTPException(status_code=404, detail="Widget file not found")

# Simple models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = None  # For better tracking
    shop_domain: Optional[str] = None  # For multi-tenant tracking

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

class ConversationStartRequest(BaseModel):
    customer_id: Optional[str] = None
    shop_domain: Optional[str] = None

# Store active conversations in memory (in production, use Redis or database)
active_conversations: Dict[str, LLMReturnsChatAgent] = {}

def get_agent_config():
    """Get configuration for the LLM agent from environment variables."""
    required_vars = ['OPENAI_API_KEY', 'SHOPIFY_ADMIN_TOKEN', 'SHOPIFY_STORE_DOMAIN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-4o'),
        'OPENAI_PROJECT_ID': os.getenv('OPENAI_PROJECT_ID'),
        'OPENAI_ORG_ID': os.getenv('OPENAI_ORG_ID'),
        'SHOPIFY_ADMIN_TOKEN': os.getenv('SHOPIFY_ADMIN_TOKEN'),
        'SHOPIFY_STORE_DOMAIN': os.getenv('SHOPIFY_STORE_DOMAIN'),
    }

def safe_sentry_call(func, *args, **kwargs):
    """Safely call Sentry functions only if Sentry is available"""
    if SENTRY_AVAILABLE:
        try:
            return func(*args, **kwargs)
        except:
            pass
    return None

@app.middleware("http")
async def add_sentry_context(request: Request, call_next):
    """Add custom context to Sentry for better error tracking."""
    # Set custom tags for this request
    safe_sentry_call(sentry_sdk.set_tag, "endpoint", str(request.url.path))
    safe_sentry_call(sentry_sdk.set_tag, "method", request.method)
    safe_sentry_call(sentry_sdk.set_tag, "service", "shopify-returns-chat")
    
    # Add user context if available (will be populated during chat)
    safe_sentry_call(sentry_sdk.set_context, "request", {
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
            "start": "/start",
            "docs": "/docs"
        },
        "monitoring": "Sentry enabled" if SENTRY_AVAILABLE else "Monitoring disabled",
        "llm_agent": "Integrated with LLMReturnsChatAgent"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with Sentry tracking"""
    try:
        # Track health checks in Sentry
        safe_sentry_call(sentry_sdk.add_breadcrumb,
            message="Health check called",
            category="health",
            level="info"
        )
        
        # Test agent configuration
        try:
            config = get_agent_config()
            config_status = "valid"
        except RuntimeError as e:
            config_status = f"invalid: {str(e)}"
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "shopify-returns-agent",
            "version": "1.0.0",
            "sentry_enabled": SENTRY_AVAILABLE,
            "active_conversations": len(active_conversations),
            "agent_config": config_status
        }
        
        # Send success event to Sentry
        safe_sentry_call(sentry_sdk.capture_message, "Health check successful", level="info")
        
        return health_status
    except Exception as e:
        safe_sentry_call(sentry_sdk.capture_exception, e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start", response_model=ChatResponse)
async def start_conversation(request: ConversationStartRequest):
    """Start a new conversation with the returns agent."""
    try:
        # Get agent configuration
        config = get_agent_config()
        
        # Create new agent instance
        agent = LLMReturnsChatAgent(config)
        
        # Start conversation and get greeting
        greeting = agent.start_conversation()
        conversation_id = agent.conversation_id
        
        # Store agent in active conversations
        active_conversations[conversation_id] = agent
        
        # Set up Sentry context
        safe_sentry_call(sentry_sdk.set_user, {
            "id": request.customer_id,
            "conversation_id": conversation_id,
            "shop_domain": request.shop_domain,
        })
        
        safe_sentry_call(sentry_sdk.set_tag, "conversation_id", conversation_id)
        safe_sentry_call(sentry_sdk.set_tag, "shop_domain", request.shop_domain or "unknown")
        
        logger.info(f"Started new conversation: {conversation_id}")
        
        return ChatResponse(
            response=greeting,
            conversation_id=conversation_id
        )
        
    except RuntimeError as e:
        logger.error(f"Configuration error: {str(e)}")
        safe_sentry_call(sentry_sdk.capture_exception, e)
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        safe_sentry_call(sentry_sdk.capture_exception, e)
        raise HTTPException(status_code=500, detail=f"Error starting conversation: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for the returns agent."""
    conversation_id = request.conversation_id
    
    if not conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required. Please start a conversation first using /start endpoint.")
    
    # Add customer context to Sentry
    safe_sentry_call(sentry_sdk.set_user, {
        "id": request.customer_id,
        "conversation_id": conversation_id,
        "shop_domain": request.shop_domain,
    })
    
    # Set custom tags for this chat
    safe_sentry_call(sentry_sdk.set_tag, "conversation_id", conversation_id)
    safe_sentry_call(sentry_sdk.set_tag, "shop_domain", request.shop_domain or "unknown")
    safe_sentry_call(sentry_sdk.set_tag, "has_customer_id", bool(request.customer_id))
    
    # Add extra context
    safe_sentry_call(sentry_sdk.set_context, "chat_request", {
        "message_length": len(request.message),
        "conversation_id": conversation_id,
        "customer_id": request.customer_id,
        "shop_domain": request.shop_domain,
    })
    
    try:
        # Get agent from active conversations
        agent = active_conversations.get(conversation_id)
        
        if not agent:
            # Try to restore from logs if possible, otherwise start new conversation
            try:
                config = get_agent_config()
                agent = LLMReturnsChatAgent.from_log(config, conversation_id)
                active_conversations[conversation_id] = agent
            except:
                raise HTTPException(
                    status_code=404, 
                    detail="Conversation not found. Please start a new conversation using /start endpoint."
                )
        
        # Start a Sentry transaction for performance monitoring
        if SENTRY_AVAILABLE:
            with sentry_sdk.start_transaction(op="chat", name="process_return_request"):
                logger.info(f"Processing chat request for conversation: {conversation_id}")
                
                # Process message with LLM agent
                response_text = agent.process_message(request.message)
        else:
            logger.info(f"Processing chat request for conversation: {conversation_id}")
            response_text = agent.process_message(request.message)
        
        # Log successful interaction
        logger.info(f"Chat response generated for conversation: {conversation_id}")
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error with context
        logger.error(f"Chat error for conversation {conversation_id}: {str(e)}")
        
        # Add error context to Sentry
        safe_sentry_call(sentry_sdk.set_context, "error_context", {
            "conversation_id": conversation_id,
            "error_type": type(e).__name__,
            "user_message": request.message,
        })
        
        # Capture exception in Sentry
        safe_sentry_call(sentry_sdk.capture_exception, e)
        
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/sentry-debug")
async def trigger_error():
    """Debug endpoint to test Sentry integration (remove in production)."""
    logger.warning("Debug endpoint accessed - this will trigger a test error")
    safe_sentry_call(sentry_sdk.set_tag, "debug", "test_error")
    raise Exception("This is a test error for Sentry integration!")

# Add Railway deployment debugging endpoints
@app.get("/debug/railway")
async def railway_debug():
    """Debug endpoint specifically for Railway deployment issues"""
    try:
        # Send custom event to Sentry for Railway debugging
        safe_sentry_call(sentry_sdk.add_breadcrumb,
            message="Railway debug endpoint called",
            category="railway",
            level="info"
        )
        
        debug_info = {
            "status": "Railway deployment successful!",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "sentry_enabled": SENTRY_AVAILABLE,
            "sentry_dsn_configured": bool(os.getenv("SENTRY_DSN")),
            "python_path": os.getcwd(),
            "port": os.getenv("PORT", "not_set"),
            "active_conversations": len(active_conversations),
            "agent_config_check": "valid" if get_agent_config() else "invalid"
        }
        
        # Track successful Railway deployment
        safe_sentry_call(sentry_sdk.set_tag, "railway.deployment", "success")
        safe_sentry_call(sentry_sdk.capture_message, "Railway deployment debug endpoint accessed", level="info")
        
        logger.info("Railway debug endpoint successful")
        return debug_info
        
    except Exception as e:
        safe_sentry_call(sentry_sdk.capture_exception, e)
        logger.error(f"Railway debug error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add startup event tracking
@app.on_event("startup")
async def startup_event():
    """Track application startup in Sentry"""
    safe_sentry_call(sentry_sdk.capture_message, "FastAPI application starting up", level="info")
    safe_sentry_call(sentry_sdk.set_tag, "railway.startup", "success")
    
    # Test agent configuration on startup
    try:
        config = get_agent_config()
        logger.info("✅ LLM agent configuration validated successfully")
    except RuntimeError as e:
        logger.error(f"❌ LLM agent configuration invalid: {str(e)}")
        logger.error("Please check your environment variables")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port) 