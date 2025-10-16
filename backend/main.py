"""
FastAPI Main Application
KRX Stock Market - Authentication and Admin API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

# Import routers
from backend.api.routers import auth, admin

# Import database utilities
from backend.core.database import init_db, check_db_connection, close_db_connections, get_db_info


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown

    Startup:
        - Initialize database tables
        - Check database connection

    Shutdown:
        - Close database connections
    """
    # Startup
    print("🚀 Starting up application...")

    # Initialize database
    try:
        init_db()
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

    # Check database connection
    db_info = get_db_info()
    if db_info['connected']:
        print(f"✅ Database connected: {db_info['host']}:{db_info['port']}/{db_info['database']}")
    else:
        print(f"⚠️  Database connection failed")

    yield

    # Shutdown
    print("🛑 Shutting down application...")
    close_db_connections()
    print("✅ Database connections closed")


# Configuration
app = FastAPI(
    title="KRX Stock Market API",
    description="인증, 사용자 관리 및 주식 데이터 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
        "http://frontend:8501",  # Docker service name
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "KRX Stock Market API is running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "admin": "/api/admin",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    """상세 헬스 체크"""
    db_info = get_db_info()

    return {
        "status": "healthy" if db_info['connected'] else "degraded",
        "api": "running",
        "database": {
            "connected": db_info['connected'],
            "host": db_info.get('host'),
            "port": db_info.get('port'),
            "database": db_info.get('database')
        },
        "redis": "pending"  # TODO: Add Redis health check
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
