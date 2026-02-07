
import sys
import os

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.db.models import Base

def init_db():
    print("Initializing database...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Successfully created all tables.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
