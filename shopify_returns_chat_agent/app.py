from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import uuid
from dotenv import load_dotenv
import threading
import time
import requests
import sys

# Import our chat agent
from llm_returns_chat_agent import LLMReturnsChatAgent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Shopify Returns Chat API",
    description="API for handling returns and exchanges through conversational AI",
    version="0.1.0"
)

# Configure CORS with environment variables
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    allowed_origins = ["*"]  # Default to allow all for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for frontend assets if needed)
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Dependency to get agent config
def get_agent_config():
    """Get configuration from environment variables"""
    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "SHOPIFY_ADMIN_TOKEN": os.getenv("SHOPIFY_ADMIN_TOKEN"),
        "SHOPIFY_STORE_DOMAIN": os.getenv("SHOPIFY_STORE_DOMAIN"),
        # Add other config parameters as needed
    }
    # Validate required environment variables
    missing_vars = []
    if not config["OPENAI_API_KEY"]:
        missing_vars.append("OPENAI_API_KEY")
    if not config["SHOPIFY_ADMIN_TOKEN"]:
        missing_vars.append("SHOPIFY_ADMIN_TOKEN")
    if not config["SHOPIFY_STORE_DOMAIN"]:
        missing_vars.append("SHOPIFY_STORE_DOMAIN")
    
    if missing_vars:
        raise HTTPException(status_code=500, detail=f"Missing required environment variables: {', '.join(missing_vars)}")
    return config

# Pydantic models for request/response
class MessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class MessageResponse(BaseModel):
    conversation_id: str
    response: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

@app.get("/", response_class=HTMLResponse)
async def serve_chat_page():
    """Serve the standalone chat interface"""
    try:
        # Read the HTML file
        html_path = os.path.join("frontend", "standalone-chat.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Chat Not Found</title></head>
                <body>
                    <h1>Chat Interface Not Found</h1>
                    <p>The chat interface file is missing. Please check your deployment.</p>
                    <p><a href="/health">Check API Health</a></p>
                </body>
            </html>
            """,
            status_code=404
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if environment variables exist
        config = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "SHOPIFY_ADMIN_TOKEN": os.getenv("SHOPIFY_ADMIN_TOKEN"),
            "SHOPIFY_STORE_DOMAIN": os.getenv("SHOPIFY_STORE_DOMAIN"),
        }
        
        # Only check if variables exist, don't require them for health check
        env_status = all(config.values())
        
        return {
            "status": "healthy",
            "environment_configured": env_status,
            "frontend_available": os.path.exists("frontend/standalone-chat.html")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest, config: dict = Depends(get_agent_config)):
    """Process a chat message through the returns agent"""
    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Restore or create agent
        if request.conversation_id:
            try:
                agent = LLMReturnsChatAgent.from_log(config, conversation_id)
            except FileNotFoundError:
                # If conversation not found, create a new one but keep the ID
                agent = LLMReturnsChatAgent(config)
                agent.conversation_id = conversation_id
                agent.start_conversation()
        else:
            agent = LLMReturnsChatAgent(config)
            agent.conversation_id = conversation_id
            agent.start_conversation()  # initializes messages array
            
        # Process message through chat agent
        response = agent.process_message(request.message)
        
        # Return response with conversation state
        return MessageResponse(
            conversation_id=conversation_id,
            response=response,
            status="success",
            metadata={"context": agent.context}  # Include relevant context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler to return formatted error responses"""
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)}
    )

def start_server_thread(port=8080):
    """Start the server in a background thread"""
    import uvicorn
    config = uvicorn.Config("app:app", port=port, log_level="info")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    return thread

def test_server(port=8080, max_retries=5):
    """Test that the server is running and endpoints are working"""
    print(f"Testing server on port {port}...")
    
    # Allow some time for server to start
    for i in range(max_retries):
        try:
            time.sleep(1)
            response = requests.get(f"http://localhost:{port}/health")
            if response.status_code == 200:
                print(f"✅ Server is running! Health endpoint returned: {response.json()}")
                return True
        except requests.RequestException:
            print(f"Waiting for server to start (attempt {i+1}/{max_retries})...")
    
    print("❌ Failed to connect to server after multiple attempts")
    return False

if __name__ == "__main__":
    import uvicorn
    
    # If --test flag is provided, run self-test
    if "--test" in sys.argv:
        port = 8088  # Use a different port for testing
        print("Starting server for self-test...")
        server_thread = start_server_thread(port)
        success = test_server(port)
        if success:
            print("Self-test completed successfully!")
        else:
            print("Self-test failed!")
            sys.exit(1)
    else:
        # Regular server start
        print("Starting server in normal mode...")
        port = int(os.getenv("PORT", 8080))
        uvicorn.run("app:app", host="0.0.0.0", port=port) 