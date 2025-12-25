#!/usr/bin/env python3
"""
Main entry point for PII Detection API on Render
"""

import os
import sys
from pathlib import Path

# Add pii_system to Python path
current_dir = Path(__file__).parent
pii_system_dir = current_dir / "pii_system"
sys.path.insert(0, str(pii_system_dir))

# Import and run the backend
from backend.main import app
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )