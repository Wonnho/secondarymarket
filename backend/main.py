"""
FastAPI Main Application
KRX Stock Market - Authentication API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configuration
app = FastAPI(
    title="KRX Stock Market API",
    description="인증 및 주식 데이터 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "KRX Stock Market API is running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """상세 헬스 체크"""
    return {
        "status": "healthy",
        "api": "running",
        "database": "pending",  # 나중에 DB 연결 상태 추가
        "redis": "pending"       # 나중에 Redis 연결 상태 추가
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
