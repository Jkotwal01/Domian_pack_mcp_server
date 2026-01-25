"""
Database Initialization Script

Run this script to initialize the PostgreSQL database schema.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import db

def main():
    print("Initializing Domain Pack MCP Database...")
    print(f"Connection string: {db.get_connection_string()}")
    
    try:
        db.init_database()
        print("✅ Database initialized successfully!")
        print("\nTables created:")
        print("  - sessions")
        print("  - versions")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
