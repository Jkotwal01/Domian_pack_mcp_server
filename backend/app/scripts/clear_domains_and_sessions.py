"""Script to clear all domain configurations and chat sessions from database.

This script will:
1. Delete all chat messages (via cascade from chat sessions)
2. Delete all chat sessions (via cascade from domain configs)
3. Delete all domain configurations
4. Keep all user data intact

Run this script from the backend directory:
    python -m app.scripts.clear_domains_and_sessions
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal
from app.models.domain_config import DomainConfig
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage


def clear_all_domains_and_sessions():
    """Delete all domain configurations and chat sessions from the database."""
    db = SessionLocal()
    
    try:
        # Count records before deletion
        domain_count = db.query(DomainConfig).count()
        session_count = db.query(ChatSession).count()
        message_count = db.query(ChatMessage).count()
        
        print("\n" + "="*60)
        print("🗑️  Database Cleanup - Domains and Sessions")
        print("="*60)
        print(f"\n📊 Current counts:")
        print(f"   - Domain Configurations: {domain_count}")
        print(f"   - Chat Sessions: {session_count}")
        print(f"   - Chat Messages: {message_count}")
        print("\n" + "="*60)
        
        if domain_count == 0 and session_count == 0 and message_count == 0:
            print("\n✅ Database is already clean! No records to delete.")
            print("="*60 + "\n")
            return
        
        print("\n🔄 Deleting records...")
        
        # Delete all domain configurations
        # This will cascade delete all chat_sessions and chat_messages
        deleted_domains = db.query(DomainConfig).delete()
        
        db.commit()
        
        # Verify deletion
        remaining_domains = db.query(DomainConfig).count()
        remaining_sessions = db.query(ChatSession).count()
        remaining_messages = db.query(ChatMessage).count()
        
        print("\n✅ Deletion complete!")
        print("\n📊 Results:")
        print(f"   - Deleted {deleted_domains} domain configurations")
        print(f"   - Deleted {session_count} chat sessions (via cascade)")
        print(f"   - Deleted {message_count} chat messages (via cascade)")
        print(f"\n📊 Remaining counts:")
        print(f"   - Domain Configurations: {remaining_domains}")
        print(f"   - Chat Sessions: {remaining_sessions}")
        print(f"   - Chat Messages: {remaining_messages}")
        print("\n✅ User data remains intact!")
        print("="*60 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during deletion: {e}")
        print("="*60 + "\n")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clear_all_domains_and_sessions()
