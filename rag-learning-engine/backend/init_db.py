#!/usr/bin/env python3
"""
Database initialization script
Run this to create the SQLite database and tables
"""

from .models import create_tables, engine
from .config import settings
import os

def init_database():
    """Initialize the database and create tables"""
    print("Initializing database...")
    
    # Ensure data directory exists
    data_dir = os.path.dirname(settings.database_url.replace("sqlite:///", ""))
    if data_dir and data_dir != ".":
        os.makedirs(data_dir, exist_ok=True)
    
    # Create tables
    create_tables()
    print(f"Database initialized at: {settings.database_url}")
    print("Tables created: documents, chunks")

if __name__ == "__main__":
    init_database() 