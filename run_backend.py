#!/usr/bin/env python3
"""
Run script for MediAssist AI Frontend
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])