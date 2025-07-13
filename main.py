#!/usr/bin/env python3
"""
Railway-compatible FastAPI app entry point
Based on successful Railway deployment patterns
"""

import os
import sys
from pathlib import Path

# Add the shopify_returns_chat_agent directory to the Python path
sys.path.append(str(Path(__file__).parent / "shopify_returns_chat_agent"))

# Import the FastAPI app from the subdirectory
from app import app

# Railway compatibility: Ensure the app is accessible at the module level
# This is crucial for gunicorn to find the app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Railway provides this)
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting FastAPI app on port {port}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path}")
    
    # Run with Railway-compatible settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 