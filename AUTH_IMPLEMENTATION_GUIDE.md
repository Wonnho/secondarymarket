# 인증 시스템 구현 가이드

**프로젝트:** KRX Stock Market Application
**작성일:** 2024-01-15
**목표:** JWT 기반 안전한 인증 시스템 구축

---

## 📋 목차

1. [아키텍처 개요](#아키텍처-개요)
2. [데이터베이스 설계](#데이터베이스-설계)
3. [인증 흐름](#인증-흐름)
4. [구현 상세](#구현-상세)
5. [보안 Best Practices](#보안-best-practices)
6. [배포 체크리스트](#배포-체크리스트)

---

## 🏗️ 아키텍처 개요

### 시스템 구성도

```
┌─────────────┐
│  Frontend   │
│ (Streamlit) │
└──────┬──────┘
       │ HTTPS
       │
┌──────▼──────┐      ┌──────────────┐
│   Auth API  │◄────►│  PostgreSQL  │
│  (FastAPI)  │      │   Database   │
└──────┬──────┘      └──────────────┘
       │
       │ JWT Token
       │
┌──────▼──────┐
│ Resource API│
│ (Protected) │
└─────────────┘
```

### 기술 스택

| 계층 | 기술 | 목적 |
|------|------|------|
| **Frontend** | Streamlit | UI 렌더링 |
| **Backend** | FastAPI | RESTful API |
| **Database** | PostgreSQL / SQLite | 사용자 데이터 저장 |
| **ORM** | SQLAlchemy | 데이터베이스 추상화 |
| **Auth** | JWT (PyJWT) | 토큰 기반 인증 |
| **Password** | bcrypt / passlib | 비밀번호 암호화 |
| **Validation** | Pydantic | 데이터 검증 |

---

## 💾 데이터베이스 설계

### ERD (Entity Relationship Diagram)

```
┌─────────────────────────┐
│        users            │
├─────────────────────────┤
│ id (PK)        SERIAL   │
│ user_id        VARCHAR  │ (UNIQUE)
│ email          VARCHAR  │ (UNIQUE)
│ password_hash  VARCHAR  │
│ name           VARCHAR  │
│ is_active      BOOLEAN  │
│ is_verified    BOOLEAN  │
│ created_at     TIMESTAMP│
│ updated_at     TIMESTAMP│
│ last_login_at  TIMESTAMP│
└─────────────────────────┘
           │
           │ 1:N
           │
┌──────────▼──────────────┐
│   refresh_tokens        │
├─────────────────────────┤
│ id (PK)        SERIAL   │
│ user_id (FK)   INTEGER  │
│ token          VARCHAR  │ (UNIQUE)
│ expires_at     TIMESTAMP│
│ created_at     TIMESTAMP│
│ revoked_at     TIMESTAMP│ (NULL if active)
│ device_info    VARCHAR  │
└─────────────────────────┘
           │
           │ 1:N
           │
┌──────────▼──────────────┐
│    login_history        │
├─────────────────────────┤
│ id (PK)        SERIAL   │
│ user_id (FK)   INTEGER  │
│ ip_address     VARCHAR  │
│ user_agent     VARCHAR  │
│ login_at       TIMESTAMP│
│ success        BOOLEAN  │
└─────────────────────────┘
```

### SQL Schema

```sql
-- users 테이블
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,

    CONSTRAINT chk_user_id_format CHECK (user_id ~ '^[a-zA-Z0-9_]{4,20}$'),
    CONSTRAINT chk_email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- refresh_tokens 테이블
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    device_info VARCHAR(255),

    CONSTRAINT chk_not_expired CHECK (expires_at > created_at)
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- login_history 테이블
CREATE TABLE login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL
);

CREATE INDEX idx_login_history_user_id ON login_history(user_id);
CREATE INDEX idx_login_history_login_at ON login_history(login_at);
```

### SQLAlchemy Models

```python
# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, email={self.email})>"


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    device_info = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"


class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    login_at = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, nullable=False)

    # Relationships
    user = relationship("User", back_populates="login_history")

    def __repr__(self):
        return f"<LoginHistory(id={self.id}, user_id={self.user_id}, success={self.success})>"
```

---

## 🔐 인증 흐름

### 1. 회원가입 플로우

```
사용자                  Frontend                Backend              Database
  │                       │                        │                     │
  ├──① 회원가입 정보 입력──►│                        │                     │
  │                       ├──② POST /auth/signup──►│                     │
  │                       │                        ├──③ 유효성 검증       │
  │                       │                        ├──④ 비밀번호 해싱     │
  │                       │                        ├──⑤ 사용자 생성──────►│
  │                       │                        │◄──⑥ 생성 완료───────┤
  │                       │◄──⑦ 성공 응답─────────┤                     │
  │◄──⑧ 성공 메시지 표시──┤                        │                     │
  │                       │                        │                     │
```

**상세 단계:**
1. 사용자가 회원가입 폼 작성
2. Frontend에서 Backend로 POST 요청
3. Backend에서 입력 데이터 검증
   - 아이디 중복 확인
   - 이메일 형식 검증
   - 비밀번호 강도 확인
4. 비밀번호를 bcrypt로 해싱
5. 데이터베이스에 사용자 생성
6. 성공 응답 반환
7. Frontend에서 성공 메시지 표시
8. 로그인 페이지로 리다이렉트

### 2. 로그인 플로우

```
사용자                  Frontend                Backend              Database
  │                       │                        │                     │
  ├──① 로그인 정보 입력───►│                        │                     │
  │                       ├──② POST /auth/login───►│                     │
  │                       │                        ├──③ 사용자 조회──────►│
  │                       │                        │◄──④ 사용자 정보─────┤
  │                       │                        ├──⑤ 비밀번호 검증     │
  │                       │                        ├──⑥ JWT 생성         │
  │                       │                        ├──⑦ Refresh Token───►│
  │                       │                        │    저장              │
  │                       │                        ├──⑧ 로그인 이력──────►│
  │                       │◄──⑨ Tokens 반환───────┤                     │
  │                       ├──⑩ Tokens 저장        │                     │
  │◄──⑪ 메인 페이지로─────┤    (session_state)     │                     │
  │     리다이렉트         │                        │                     │
```

**JWT Payload 구조:**
```json
{
  "sub": "johndoe",           // user_id
  "email": "john@example.com",
  "name": "홍길동",
  "user_db_id": 123,          // DB primary key
  "exp": 1705334400,          // 만료 시간 (Unix timestamp)
  "iat": 1705330800,          // 발급 시간
  "type": "access"            // 토큰 타입
}
```

### 3. 인증된 요청 플로우

```
사용자                  Frontend                Backend              Database
  │                       │                        │                     │
  ├──① 보호된 리소스 요청──►│                        │                     │
  │                       ├──② GET /api/stocks────►│                     │
  │                       │   Authorization:       │                     │
  │                       │   Bearer <token>       │                     │
  │                       │                        ├──③ JWT 검증         │
  │                       │                        ├──④ 토큰 만료 확인   │
  │                       │                        ├──⑤ 사용자 권한 확인─►│
  │                       │                        │◄──⑥ 권한 정보───────┤
  │                       │◄──⑦ 리소스 반환───────┤                     │
  │◄──⑧ 데이터 표시───────┤                        │                     │
  │                       │                        │                     │
```

### 4. 토큰 갱신 플로우

```
사용자                  Frontend                Backend              Database
  │                       │                        │                     │
  │                       │  (Access Token 만료)   │                     │
  │                       ├──① POST /auth/refresh─►│                     │
  │                       │   refresh_token        │                     │
  │                       │                        ├──② Refresh Token───►│
  │                       │                        │    검증              │
  │                       │                        │◄──③ 토큰 유효성─────┤
  │                       │                        ├──④ 새 Access Token  │
  │                       │                        │    생성              │
  │                       │◄──⑤ 새 Token 반환─────┤                     │
  │                       ├──⑥ Token 업데이트      │                     │
  │◄──⑦ 계속 사용─────────┤                        │                     │
  │                       │                        │                     │
```

### 5. 로그아웃 플로우

```
사용자                  Frontend                Backend              Database
  │                       │                        │                     │
  ├──① 로그아웃 버튼 클릭──►│                        │                     │
  │                       ├──② POST /auth/logout──►│                     │
  │                       │   refresh_token        │                     │
  │                       │                        ├──③ Refresh Token───►│
  │                       │                        │    무효화 (revoke)   │
  │                       │                        │◄──④ 완료────────────┤
  │                       │◄──⑤ 성공 응답─────────┤                     │
  │                       ├──⑥ Tokens 삭제        │                     │
  │◄──⑦ 로그인 페이지로────┤                        │                     │
  │     리다이렉트         │                        │                     │
```

---

## 💻 구현 상세

### 디렉토리 구조

```
secondarymarket/
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 엔트리포인트
│   ├── dependencies.py         # 의존성 주입
│   └── routers/
│       ├── __init__.py
│       ├── auth.py             # 인증 라우터
│       └── stocks.py           # 주식 API (보호됨)
├── core/
│   ├── __init__.py
│   ├── config.py               # 설정
│   ├── security.py             # 보안 유틸리티
│   └── database.py             # DB 연결
├── models/
│   ├── __init__.py
│   └── user.py                 # 데이터 모델
├── schemas/
│   ├── __init__.py
│   ├── user.py                 # Pydantic 스키마
│   └── token.py                # 토큰 스키마
├── services/
│   ├── __init__.py
│   ├── auth_service.py         # 인증 비즈니스 로직
│   └── user_service.py         # 사용자 관리
├── pages/
│   ├── login.py                # 로그인 페이지 (수정)
│   └── signup.py               # 회원가입 페이지 (수정)
└── utils/
    ├── __init__.py
    └── auth_middleware.py      # 인증 미들웨어
```

### 1. 설정 파일 (`core/config.py`)

```python
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # 애플리케이션
    APP_NAME: str = "KRX Stock Market API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 데이터베이스
    DATABASE_URL: str = "postgresql://user:password@localhost/krx_db"
    # 또는 SQLite: "sqlite:///./krx.db"

    # JWT 설정
    JWT_SECRET_KEY: str  # 필수! 환경변수에서 읽어야 함
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1시간
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30     # 30일

    # 비밀번호 정책
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:8501"]  # Streamlit 기본 포트

    # 보안
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_TIMEOUT_MINUTES: int = 15

    # 이메일 (선택사항 - 이메일 인증용)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        env_file = Path(__file__).parent.parent / '.env'
        case_sensitive = True

# 싱글톤 인스턴스
settings = Settings()
```

**`.env` 파일 예시:**
```bash
# .env
# 데이터베이스
DATABASE_URL=postgresql://krx_user:secure_password@localhost:5432/krx_db

# JWT (⚠️  절대 공유하지 말 것!)
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars

# 디버그
DEBUG=True

# OpenAI (기존)
OPENAI_API_KEY=sk-...
```

**안전한 SECRET_KEY 생성:**
```bash
# Python으로 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 또는 OpenSSL로 생성
openssl rand -hex 32
```

### 2. 보안 유틸리티 (`core/security.py`)

```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.pwd import genword
from core.config import settings
import re

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)


class PasswordValidator:
    """비밀번호 강도 검증"""

    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        """
        비밀번호 강도 검증

        Returns:
            (is_valid, error_message)
        """
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return False, f"비밀번호는 최소 {settings.PASSWORD_MIN_LENGTH}자 이상이어야 합니다."

        if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "비밀번호는 최소 1개의 대문자를 포함해야 합니다."

        if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "비밀번호는 최소 1개의 소문자를 포함해야 합니다."

        if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "비밀번호는 최소 1개의 숫자를 포함해야 합니다."

        if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "비밀번호는 최소 1개의 특수문자를 포함해야 합니다."

        return True, ""

    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """강력한 랜덤 비밀번호 생성"""
        return genword(length=length, charset="ascii_62")


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """JWT Access Token 생성"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """JWT Refresh Token 생성"""
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """JWT 토큰 디코딩 및 검증"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def is_token_expired(token: str) -> bool:
    """토큰 만료 여부 확인"""
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            return datetime.utcfromtimestamp(exp) < datetime.utcnow()
        return True
    except ValueError:
        return True
```

### 3. Pydantic 스키마 (`schemas/`)

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
import re

class UserBase(BaseModel):
    user_id: str = Field(..., min_length=4, max_length=20)
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)

    @validator('user_id')
    def validate_user_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('아이디는 영문, 숫자, 언더스코어만 사용 가능합니다.')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str
    agree: bool = Field(..., description="이용약관 동의")

    @validator('agree')
    def validate_agreement(cls, v):
        if not v:
            raise ValueError('이용약관에 동의해야 합니다.')
        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('비밀번호가 일치하지 않습니다.')
        return v


class UserLogin(BaseModel):
    user_id: str
    password: str
    remember_me: bool = False


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


# schemas/token.py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    sub: str  # user_id
    email: str
    name: str
    user_db_id: int
    exp: int
    iat: int
    type: str


class TokenRefresh(BaseModel):
    refresh_token: str
```

### 4. 인증 서비스 (`services/auth_service.py`)

```python
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Tuple
from models.user import User, RefreshToken, LoginHistory
from schemas.user import UserCreate, UserLogin
from schemas.token import Token
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    PasswordValidator
)
from core.config import settings
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserCreate) -> User:
        """
        사용자 회원가입

        Raises:
            HTTPException: 중복 아이디/이메일, 비밀번호 정책 위반
        """
        # 1. 중복 확인
        if self.db.query(User).filter(User.user_id == user_data.user_id).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 아이디입니다."
            )

        if self.db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 이메일입니다."
            )

        # 2. 비밀번호 검증
        is_valid, error_msg = PasswordValidator.validate(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # 3. 비밀번호 해싱
        hashed_password = hash_password(user_data.password)

        # 4. 사용자 생성
        new_user = User(
            user_id=user_data.user_id,
            email=user_data.email,
            name=user_data.name,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False  # 이메일 인증 필요 시
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    def authenticate_user(
        self,
        credentials: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[User, Token]:
        """
        사용자 인증 및 토큰 발급

        Returns:
            (User, Token)

        Raises:
            HTTPException: 인증 실패
        """
        # 1. 사용자 조회
        user = self.db.query(User).filter(User.user_id == credentials.user_id).first()

        # 2. 사용자 존재 여부 및 비밀번호 확인
        if not user or not verify_password(credentials.password, user.password_hash):
            # 로그인 실패 기록
            self._record_login_attempt(
                user_id=user.id if user else None,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. 계정 활성화 확인
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비활성화된 계정입니다. 관리자에게 문의하세요."
            )

        # 4. JWT 생성
        access_token = create_access_token(
            data={
                "sub": user.user_id,
                "email": user.email,
                "name": user.name,
                "user_db_id": user.id
            }
        )

        refresh_token_str = create_refresh_token(
            data={
                "sub": user.user_id,
                "user_db_id": user.id
            }
        )

        # 5. Refresh Token DB에 저장
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            device_info=user_agent[:255] if user_agent else None
        )
        self.db.add(refresh_token_record)

        # 6. 로그인 시간 업데이트
        user.last_login_at = datetime.utcnow()

        # 7. 로그인 성공 기록
        self._record_login_attempt(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )

        self.db.commit()

        # 8. Token 객체 생성
        token = Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        return user, token

    def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Access Token 갱신

        Raises:
            HTTPException: 유효하지 않은 Refresh Token
        """
        # 1. Refresh Token 검증
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 refresh token입니다."
            )

        # 2. Token 타입 확인
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 token 타입입니다."
            )

        # 3. DB에서 Refresh Token 확인
        token_record = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked_at.is_(None)
        ).first()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token이 만료되었거나 무효화되었습니다."
            )

        # 4. 만료 시간 확인
        if token_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token이 만료되었습니다."
            )

        # 5. 사용자 조회
        user = self.db.query(User).filter(User.id == token_record.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없거나 비활성화되었습니다."
            )

        # 6. 새로운 Access Token 생성
        access_token = create_access_token(
            data={
                "sub": user.user_id,
                "email": user.email,
                "name": user.name,
                "user_db_id": user.id
            }
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,  # 기존 Refresh Token 재사용
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def logout(self, refresh_token: str) -> bool:
        """
        로그아웃 (Refresh Token 무효화)

        Returns:
            성공 여부
        """
        token_record = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked_at.is_(None)
        ).first()

        if token_record:
            token_record.revoked_at = datetime.utcnow()
            self.db.commit()
            return True

        return False

    def _record_login_attempt(
        self,
        user_id: Optional[int],
        ip_address: Optional[str],
        user_agent: Optional[str],
        success: bool
    ):
        """로그인 시도 기록"""
        if user_id:
            login_record = LoginHistory(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success
            )
            self.db.add(login_record)
```

### 5. FastAPI 라우터 (`api/routers/auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from core.database import get_db
from services.auth_service import AuthService
from schemas.user import UserCreate, UserLogin, UserResponse
from schemas.token import Token, TokenRefresh

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    회원가입

    - **user_id**: 아이디 (4-20자, 영문/숫자/언더스코어)
    - **email**: 이메일 주소
    - **password**: 비밀번호 (8자 이상, 대소문자/숫자/특수문자 포함)
    - **password_confirm**: 비밀번호 확인
    - **name**: 이름
    - **agree**: 이용약관 동의
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return user


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    로그인

    - **user_id**: 아이디
    - **password**: 비밀번호
    - **remember_me**: 로그인 상태 유지 (선택)

    Returns:
        JWT Access Token 및 Refresh Token
    """
    auth_service = AuthService(db)

    # 클라이언트 정보 수집
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    user, token = auth_service.authenticate_user(
        credentials=credentials,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return token


@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Access Token 갱신

    - **refresh_token**: 유효한 Refresh Token

    Returns:
        새로운 Access Token
    """
    auth_service = AuthService(db)
    new_token = auth_service.refresh_access_token(token_data.refresh_token)
    return new_token


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    로그아웃

    - **refresh_token**: 무효화할 Refresh Token

    Returns:
        성공 메시지
    """
    auth_service = AuthService(db)
    success = auth_service.logout(token_data.refresh_token)

    if success:
        return {"message": "로그아웃되었습니다."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 refresh token입니다."
        )
```

### 6. 인증 의존성 (`api/dependencies.py`)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import decode_token
from models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 반환

    Raises:
        HTTPException: 유효하지 않은 토큰
    """
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token 타입 확인
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 사용자 조회
    user_id = payload.get("user_db_id")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다."
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    활성화된 현재 사용자 반환 (별도 검증 필요 시)
    """
    return current_user
```

### 7. 보호된 API 예시 (`api/routers/stocks.py`)

```python
from fastapi import APIRouter, Depends
from models.user import User
from api.dependencies import get_current_user

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/listings")
def get_stock_listings(
    market: str = "KRX",
    current_user: User = Depends(get_current_user)  # ← 인증 필수
):
    """
    상장 종목 목록 조회 (인증 필요)

    - **market**: 시장 구분 (KRX, KOSPI, KOSDAQ)
    """
    # 실제 로직...
    return {
        "user": current_user.user_id,
        "market": market,
        "stocks": []
    }
```

### 8. Streamlit 통합 (`pages/login.py`)

```python
# pages/login.py
import streamlit as st
import requests
from header import render_header

# 페이지 설정
st.set_page_config(page_title="로그인", layout="wide")
render_header()

# API 베이스 URL
API_BASE_URL = "http://localhost:8000"  # FastAPI 서버 주소

st.markdown("<h1 style='text-align: center; margin-top: 2rem;'>🔐 로그인</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("")
    st.write("")

    with st.form("login_form"):
        st.markdown("### 로그인 정보 입력")

        user_id = st.text_input("아이디", placeholder="아이디를 입력하세요")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        remember_me = st.checkbox("로그인 상태 유지")

        st.write("")

        submit_button = st.form_submit_button("로그인", use_container_width=True, type="primary")

        if submit_button:
            if user_id and password:
                try:
                    # API 호출
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={
                            "user_id": user_id,
                            "password": password,
                            "remember_me": remember_me
                        },
                        timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # 세션에 토큰 저장
                        st.session_state.access_token = data["access_token"]
                        st.session_state.refresh_token = data["refresh_token"]
                        st.session_state.user_id = user_id
                        st.session_state.authenticated = True

                        st.success(f"환영합니다, {user_id}님!")
                        st.balloons()

                        # 메인 페이지로 리다이렉트
                        st.switch_page("finance.py")

                    else:
                        error_detail = response.json().get("detail", "로그인 실패")
                        st.error(error_detail)

                except requests.exceptions.ConnectionError:
                    st.error("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
                except requests.exceptions.Timeout:
                    st.error("요청 시간이 초과되었습니다. 다시 시도해주세요.")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")
            else:
                st.error("아이디와 비밀번호를 모두 입력해주세요.")

    st.markdown("---")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("##### 계정이 없으신가요?")
    with col_b:
        if st.button("회원가입", use_container_width=True):
            st.switch_page("pages/signup.py")
```

### 9. 인증된 요청 헬퍼 (`utils/api_client.py`)

```python
# utils/api_client.py
import requests
import streamlit as st
from typing import Optional, Dict, Any

API_BASE_URL = "http://localhost:8000"


def get_auth_headers() -> Dict[str, str]:
    """인증 헤더 생성"""
    access_token = st.session_state.get("access_token")
    if not access_token:
        raise ValueError("로그인이 필요합니다.")

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


def api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    require_auth: bool = True
) -> requests.Response:
    """
    API 요청 헬퍼

    Args:
        method: HTTP 메서드 (GET, POST, PUT, DELETE)
        endpoint: API 엔드포인트 (/stocks/listings)
        data: 요청 body
        params: 쿼리 파라미터
        require_auth: 인증 필요 여부

    Returns:
        Response 객체

    Raises:
        ValueError: 인증 실패
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}

    if require_auth:
        try:
            headers = get_auth_headers()
        except ValueError:
            st.error("로그인이 필요합니다.")
            st.switch_page("pages/login.py")
            st.stop()

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=data,
            params=params,
            headers=headers,
            timeout=10
        )

        # 토큰 만료 시 갱신 시도
        if response.status_code == 401 and require_auth:
            if refresh_access_token():
                # 재시도
                headers = get_auth_headers()
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=10
                )

        return response

    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 실패: {str(e)}")
        raise


def refresh_access_token() -> bool:
    """Access Token 갱신"""
    refresh_token = st.session_state.get("refresh_token")
    if not refresh_token:
        return False

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            return True

    except Exception:
        pass

    # 갱신 실패 시 로그아웃
    st.session_state.clear()
    return False


# 사용 예시
def get_stock_listings(market: str = "KRX"):
    """상장 종목 조회 (인증 필요)"""
    response = api_request(
        method="GET",
        endpoint="/stocks/listings",
        params={"market": market},
        require_auth=True
    )

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"오류: {response.status_code}")
        return None
```

---

## 🔒 보안 Best Practices

### 1. 비밀번호 보안

#### ✅ DO (해야 할 것)
```python
# 1. 강력한 해싱 알고리즘 사용 (bcrypt, Argon2)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# 2. 비밀번호 정책 강제
- 최소 8자 이상
- 대소문자 혼용
- 숫자 포함
- 특수문자 포함

# 3. 평문 비밀번호 절대 저장/로깅 금지
# BAD
logger.info(f"User {user_id} password: {password}")  # ❌

# GOOD
logger.info(f"User {user_id} authenticated successfully")  # ✅
```

#### ❌ DON'T (하지 말아야 할 것)
```python
# ❌ MD5/SHA1 사용 금지 (취약)
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()  # NEVER DO THIS!

# ❌ 평문 저장 금지
user.password = password  # NEVER DO THIS!

# ❌ 비밀번호를 이메일로 전송 금지
send_email(user.email, f"Your password: {password}")  # NEVER DO THIS!
```

### 2. JWT 보안

#### ✅ DO
```python
# 1. 안전한 SECRET_KEY (최소 32자)
JWT_SECRET_KEY = secrets.token_urlsafe(32)

# 2. 짧은 만료 시간 (Access Token: 15-60분)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 3. HTTPS만 사용
# 4. HttpOnly 쿠키 사용 (XSS 방지)
# 5. 민감한 정보 Payload에 넣지 않기
```

#### ❌ DON'T
```python
# ❌ SECRET_KEY를 코드에 하드코딩
JWT_SECRET_KEY = "my-secret-key"  # NEVER DO THIS!

# ❌ 긴 만료 시간
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 1주일 - TOO LONG!

# ❌ 민감한 정보를 Payload에 포함
payload = {
    "sub": user_id,
    "password": password,  # ❌ NEVER!
    "ssn": "123-45-6789"   # ❌ NEVER!
}
```

### 3. SQL Injection 방어

#### ✅ DO (ORM 사용)
```python
# SQLAlchemy ORM - 자동 이스케이핑
user = db.query(User).filter(User.user_id == user_input).first()  # ✅ SAFE
```

#### ❌ DON'T (Raw SQL)
```python
# ❌ String concatenation - SQL Injection 취약!
query = f"SELECT * FROM users WHERE user_id = '{user_input}'"
db.execute(query)  # NEVER DO THIS!
```

### 4. CORS 설정

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit 주소만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ❌ 프로덕션에서 절대 사용 금지
# allow_origins=["*"]  # NEVER IN PRODUCTION!
```

### 5. Rate Limiting

```python
# pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 라우터에 적용
@router.post("/login")
@limiter.limit("5/minute")  # 1분에 5번까지만 시도 가능
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    # ...
```

### 6. 환경변수 관리

```bash
# .env (절대 Git에 커밋하지 말 것!)
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET_KEY=your-super-secret-key-here

# .gitignore에 추가
.env
.env.local
*.env
```

```python
# .env.example (템플릿 - Git에 커밋 가능)
DATABASE_URL=postgresql://user:password@localhost:5432/krx_db
JWT_SECRET_KEY=change-this-to-a-secure-random-value
OPENAI_API_KEY=sk-your-key-here
```

### 7. HTTPS 강제

```python
# 프로덕션 배포 시 HTTPS 리다이렉트 미들웨어
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

## ✅ 배포 체크리스트

### 배포 전 필수 확인사항

- [ ] **환경변수 설정**
  - [ ] `JWT_SECRET_KEY` 안전한 랜덤 값으로 변경
  - [ ] `DATABASE_URL` 프로덕션 DB로 설정
  - [ ] `.env` 파일이 `.gitignore`에 포함됨
  - [ ] 모든 API 키가 환경변수로 관리됨

- [ ] **데이터베이스**
  - [ ] 마이그레이션 스크립트 준비
  - [ ] 인덱스 생성 확인
  - [ ] 백업 전략 수립
  - [ ] 연결 풀 설정

- [ ] **보안**
  - [ ] HTTPS 설정 (SSL/TLS 인증서)
  - [ ] CORS 설정 검증
  - [ ] Rate Limiting 활성화
  - [ ] SQL Injection 테스트
  - [ ] XSS 방어 확인

- [ ] **인증 시스템**
  - [ ] 비밀번호 정책 검증
  - [ ] JWT 만료 시간 적절히 설정
  - [ ] Refresh Token 로테이션 구현
  - [ ] 로그아웃 동작 테스트

- [ ] **모니터링**
  - [ ] 로깅 시스템 구축
  - [ ] 에러 추적 (Sentry 등)
  - [ ] 성능 모니터링
  - [ ] 보안 감사 로그

- [ ] **테스트**
  - [ ] 단위 테스트 작성
  - [ ] 통합 테스트
  - [ ] 보안 테스트 (OWASP Top 10)
  - [ ] 부하 테스트

---

## 🚀 배포 가이드

### 1. Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: krx_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: krx_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U krx_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  api:
    build: ./api
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    environment:
      - DATABASE_URL=postgresql://krx_user:${DB_PASSWORD}@postgres:5432/krx_db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  # Streamlit Frontend
  streamlit:
    build: .
    command: streamlit run finance.py
    environment:
      - API_BASE_URL=http://api:8000
    ports:
      - "8501:8501"
    depends_on:
      - api

volumes:
  postgres_data:
```

### 2. 실행 명령

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 실제 값 입력

# 2. Docker Compose 실행
docker-compose up -d

# 3. 데이터베이스 마이그레이션
docker-compose exec api alembic upgrade head

# 4. 서비스 확인
curl http://localhost:8000/docs  # API 문서
open http://localhost:8501        # Streamlit 앱
```

---

## 📚 추가 학습 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/)
- [Pydantic Validation](https://pydantic-docs.helpmanual.io/)

---

**이전 문서:** [기술 부채 분석 보고서](./TECHNICAL_DEBT_ANALYSIS.md)
