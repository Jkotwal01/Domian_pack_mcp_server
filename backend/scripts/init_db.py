"""
Database initialization script
Creates all tables and initial data for the new schema
"""

import argparse
import asyncio
import logging
import os
import sys
from uuid import UUID
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure app/ is on the import path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sqlalchemy import select
from app.db.session import init_db, AsyncSessionLocal, async_engine
from app.db.models import UserRole, Base, DomainPack, Version
from app.services.auth_service import AuthService
from app.schemas import UserCreate, DomainPackCreate
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def ensure_database_exists() -> None:
    """Connect to default 'postgres' database and create target database if missing"""
    db_name = settings.DB_NAME
    
    # Connection string for the default 'postgres' database
    postgres_uri = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres"
    
    # Use sync engine for database creation as it doesn't need to be async
    engine = create_engine(postgres_uri, isolation_level="AUTOCOMMIT")
    
    with engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        exists = result.scalar() is not None
        
        if not exists:
            logger.info(f"Database '{db_name}' does not exist. Creating...")
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
    
    engine.dispose()


async def reset_database() -> None:
    """Drop and recreate everything in the public schema"""
    logger.info("Starting aggressive database reset...")
    
    async with async_engine.begin() as conn:
        logger.info("Clearing public schema...")
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        logger.info("Public schema cleared successfully")


async def create_tables() -> None:
    """Create all database tables"""
    logger.info("Creating database tables...")
    await init_db()
    logger.info("Database tables created successfully")


async def create_admin_user() -> None:
    """Create default admin user if it does not exist"""
    async with AsyncSessionLocal() as db:
        auth_service = AuthService(db)

        admin_email = "admin@example.com"

        admin = await auth_service.get_user_by_email(admin_email)
        if admin:
            logger.info("Admin user already exists")
            return

        admin_data = UserCreate(
            email=admin_email,
            name="Admin User",
            password="admin123",  # ⚠️ change in production
            role=UserRole.ADMIN,
        )

        user = await auth_service.create_user(admin_data)
        await db.commit()

        logger.info("Admin user created: admin@example.com / admin123")
        return user.id


async def create_default_domain_pack(admin_id: UUID) -> None:
    """Create a default domain pack if none exist"""
    async with AsyncSessionLocal() as db:
        # Check if any domain pack exists
        result = await db.execute(select(DomainPack).limit(1))
        if result.scalar():
            logger.info("Domain packs already exist")
            return

        from uuid import UUID as PyUUID
        # Using the specific UUID the frontend seems to be sending as default
        DEFAULT_ID = PyUUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
        
        logger.info(f"Creating default domain pack with ID: {DEFAULT_ID}")
        
        # Create domain pack
        domain_pack = DomainPack(
            id=DEFAULT_ID,
            name="Sample Healthcare Domain Pack",
            description="A comprehensive healthcare data model for patient and clinical data.",
            created_by=admin_id,
            base_template={
                "version": "1.0.0",
                "entities": {},
                "relationships": []
            },
            domain_schema={
                "type": "object",
                "properties": {
                    "entities": {"type": "object"},
                    "relationships": {"type": "array"}
                }
            }
        )
        db.add(domain_pack)
        await db.flush()

        # Create initial version
        version = Version(
            domain_pack_id=domain_pack.id,
            version_number=1,
            snapshot=domain_pack.base_template,
            committed_by=admin_id,
            commit_message="Initial baseline",
            is_rollback=False
        )
        db.add(version)
        await db.flush()

        # Link version to pack
        domain_pack.current_version_id = version.id
        await db.commit()
        
        logger.info("Default domain pack created successfully")


async def main() -> None:
    """Main initialization entrypoint"""
    parser = argparse.ArgumentParser(description="Initialize or reset the database")
    parser.add_argument("--reset", action="store_true", help="Reset the database before initializing")
    args = parser.parse_args()

    logger.info("Starting database setup...")

    try:
        # 1. Ensure DB exists
        await ensure_database_exists()
        
        # 2. Reset if requested
        if args.reset:
            await reset_database()
            
        # 3. Create tables
        await create_tables()
        
        # 4. Create admin
        admin_id = await create_admin_user()
        
        # 5. Create default data
        if admin_id:
            await create_default_domain_pack(admin_id)
            
        logger.info("✅ Database initialization complete!")
    except Exception as exc:
        logger.exception("❌ Database initialization failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
