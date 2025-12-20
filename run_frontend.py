"""
Startup script for the Restaurant Reservation System Streamlit Frontend.
"""

import subprocess
import sys
import os

def run_streamlit():
    """Run the Streamlit frontend"""
    print(" Starting Restaurant Reservation System Frontend...")
    print(" Frontend will be available at: http://localhost:8501")
    print(" Press Ctrl+C to stop the server")
    print("  Make sure the API server is running on http://localhost:8000")
    
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "app.py", 
        "--server.port=8501",
        "--server.address=127.0.0.1"
    ], cwd=frontend_dir)

if __name__ == "__main__":
    run_streamlit()
