from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.get("/")
async def root():
    """Root endpoint - simple response"""
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
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "shopify-returns-chat",
        "version": "0.1.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for the returns agent."""
    try:
        # For now, return a simple response to test deployment
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        return ChatResponse(
            response=f"Thanks for your message: '{request.message}'. The full returns agent will be connected once deployment is working!",
            conversation_id=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port) 