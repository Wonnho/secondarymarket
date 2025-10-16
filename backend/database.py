"""
Database Configuration and Connection
SQLAlchemy setup for PostgreSQL/TimescaleDB
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# ==================== Configuration ====================

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin123@timescaledb:5432/secondarymarket"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,
    max_overflow=10,
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# ==================== Database Functions ====================

def get_db() -> Generator:
    """
    Database session dependency for FastAPI

    Yields:
        Session: SQLAlchemy database session

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        # Import models here to avoid circular imports
        from models import User, AuditLog

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def close_db_connections():
    """
    Close all database connections
    Should be called on application shutdown
    """
    try:
        engine.dispose()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"⚠️  Error closing database connections: {e}")


def get_db_info() -> dict:
    """
    Get database connection information

    Returns:
        dict: Database connection details
    """
    try:
        # Parse DATABASE_URL
        url_parts = DATABASE_URL.replace("postgresql://", "").split("@")

        if len(url_parts) == 2:
            host_port_db = url_parts[1].split("/")
            host_port = host_port_db[0].split(":")

            return {
                "connected": check_db_connection(),
                "host": host_port[0] if len(host_port) > 0 else "unknown",
                "port": host_port[1] if len(host_port) > 1 else "5432",
                "database": host_port_db[1] if len(host_port_db) > 1 else "unknown"
            }
    except Exception as e:
        print(f"⚠️  Error parsing database URL: {e}")

    return {
        "connected": False,
        "host": "unknown",
        "port": "unknown",
        "database": "unknown"
    }


# ==================== Database Health Check ====================

def health_check() -> dict:
    """
    Comprehensive database health check

    Returns:
        dict: Health check results
    """
    try:
        with engine.connect() as conn:
            # Check basic connectivity
            result = conn.execute(text("SELECT version()"))
            db_version = result.scalar()

            # Check if tables exist
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            table_count = result.scalar()

            return {
                "status": "healthy",
                "connected": True,
                "version": db_version,
                "tables": table_count,
                "message": "Database is healthy"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
            "message": "Database connection failed"
        }
