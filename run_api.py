"""
Startup script for the Restaurant Reservation System API.
"""

import uvicorn
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print(" Starting Restaurant Reservation System API...")
    print(" API will be available at: http://localhost:8000")
    print(" API documentation at: http://localhost:8000/docs")
    print(" Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
