#!/usr/bin/env python3
"""
Startup script for the AI Learning Engine Backend
Initializes database and starts the FastAPI server
"""

import uvicorn
from init_db import init_database
from config import settings

def startup():
    """Initialize database and start the server"""
    print("🚀 Starting AI Learning Engine Backend...")
    
    # Initialize database
    init_database()
    
    # Start FastAPI server
    print(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

if __name__ == "__main__":
    startup() 