"""
config_utils.py
Handles environment configuration for the surveillance system.
"""

import os
from dotenv import load_dotenv
from typing import Dict

def load_config() -> Dict[str, str]:
    """Load configuration from .env file."""
    load_dotenv()
    
    required_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'SAVE_DIR',
        'MOTION_THRESHOLD'
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
    return {
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT'),
        'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        'save_dir': os.getenv('SAVE_DIR'),
        'motion_threshold': int(os.getenv('MOTION_THRESHOLD', '500'))
    }