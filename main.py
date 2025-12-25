#!/usr/bin/env python3
"""
Main entry point for PII Detection System on Render
Serves both API and static frontend files
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the backend app
from backend.main import app as api_app

# Create main app
app = FastAPI(title="PII Detection System")

# Mount the API under /api
app.mount("/api", api_app)

# Mount static files
frontend_dir = current_dir / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Serve the main page
@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    frontend_file = frontend_dir / "index.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return {"message": "PII Detection System API", "frontend": "not found"}

# Health check for the main app
@app.get("/health")
async def main_health():
    """Main health check"""
    return {
        "status": "healthy",
        "service": "PII Detection System",
        "components": {
            "api": "running",
            "frontend": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )