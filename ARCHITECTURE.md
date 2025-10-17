# 📐 SecondaryMarket 프로젝트 아키텍처 분석

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                │
│                         http://localhost:8501                            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTP
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                       FRONTEND (Streamlit)                               │
│                    Container: secondarymarket_frontend                   │
│                              Port: 8501                                  │
├──────────────────────────────────────────────────────────────────────────┤
│  Components:                                                             │
│  ├── app.py (Main Page - KOSPI/KOSDAQ 시장 현황)                        │
│  ├── pages/                                                              │
│  │   ├── login.py (로그인)                                              │
│  │   ├── signup.py (회원가입)                                           │
│  │   ├── stocks.py (종목 상세 조회)                                     │
│  │   ├── news.py (뉴스)                                                 │
│  │   ├── disclosure.py (공시)                                           │
│  │   ├── admin_test_setup.py (관리자 테스트)                            │
│  │   └── admin/ (관리자 페이지)                                         │
│  │       ├── dashboard.py                                               │
│  │       ├── users.py                                                   │
│  │       └── analytics.py                                               │
│  ├── components/                                                         │
│  │   └── header.py (공통 헤더 - 네비게이션, 로그인 상태)                │
│  └── utils/                                                              │
│      ├── auth.py (인증 헬퍼)                                             │
│      ├── session_manager.py (세션 관리)                                 │
│      ├── admin_auth.py (관리자 권한 체크)                               │
│      └── [기타 유틸리티]                                                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ REST API
                                 │ http://backend:8000/api
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                        BACKEND (FastAPI)                                 │
│                    Container: secondarymarket_backend                    │
│                              Port: 8000                                  │
├──────────────────────────────────────────────────────────────────────────┤
│  Routes:                                                                 │
│  ├── main.py (FastAPI 앱 초기화, CORS 설정)                             │
│  ├── routes_auth.py                                                      │
│  │   ├── POST /api/auth/login                                           │
│  │   ├── POST /api/auth/register                                        │
│  │   ├── GET  /api/auth/me                                              │
│  │   └── POST /api/auth/logout                                          │
│  ├── routes_admin.py                                                     │
│  │   ├── GET  /api/admin/users (사용자 목록)                            │
│  │   ├── GET  /api/admin/users/{user_id} (사용자 상세)                  │
│  │   ├── PUT  /api/admin/users/{user_id} (사용자 수정)                  │
│  │   ├── DELETE /api/admin/users/{user_id} (사용자 삭제)                │
│  │   └── GET  /api/admin/audit-logs (감사 로그)                         │
│  │                                                                        │
│  Core Modules:                                                           │
│  ├── auth.py (JWT 토큰, 비밀번호 해싱 - bcrypt)                         │
│  ├── models.py (SQLAlchemy ORM 모델)                                    │
│  │   ├── User (사용자 테이블)                                           │
│  │   └── AuditLog (감사 로그 테이블)                                    │
│  ├── schemas.py (Pydantic 스키마 - 요청/응답 검증)                      │
│  ├── database.py (DB 연결 관리, 세션)                                   │
│  └── seed_data.py (초기 데이터 생성 스크립트)                           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
    ┌───────────────────────────┐  ┌──────────────────────────┐
    │   TimescaleDB/PostgreSQL  │  │      Redis (예정)        │
    │  Container: timescaledb   │  │   Container: redis       │
    │      Port: 5432 (5433)    │  │      Port: 6379          │
    ├───────────────────────────┤  ├──────────────────────────┤
    │  Tables:                  │  │  Sessions (향후 구현)    │
    │  ├── users                │  │  Cache (향후 구현)       │
    │  └── audit_logs           │  └──────────────────────────┘
    └───────────────────────────┘
                    │
                    │ (Optional)
                    ▼
    ┌───────────────────────────┐
    │        pgAdmin 4          │
    │  Container: pgadmin       │
    │      Port: 5051           │
    │  (DB 관리 도구)           │
    └───────────────────────────┘
```

---

## 🔄 데이터 흐름 분석

### 1️⃣ **회원가입 프로세스**

```
User Browser
    │
    │ 1. 회원가입 정보 입력 (user_id, password, email, name)
    ▼
pages/signup.py
    │
    │ 2. utils.auth.register_user() 호출
    ▼
utils/auth.py
    │
    │ 3. POST http://backend:8000/api/auth/register
    │    Body: {user_id, password, email, name, role: "user"}
    ▼
Backend: routes_auth.py
    │
    │ 4. 스키마 검증 (UserCreate)
    │ 5. 중복 체크 (user_id, email)
    ▼
Backend: auth.py
    │
    │ 6. get_password_hash() - bcrypt 해싱
    ▼
Backend: models.py
    │
    │ 7. User 모델 생성
    ▼
TimescaleDB
    │
    │ 8. INSERT INTO users
    │ 9. 201 Created 응답
    ▼
Frontend: signup.py
    │
    │ 10. 성공 메시지 표시
    │ 11. 로그인 페이지로 리다이렉트
    ▼
User Browser
```

---

### 2️⃣ **로그인 프로세스**

```
User Browser
    │
    │ 1. 로그인 정보 입력 (user_id, password)
    ▼
pages/login.py
    │
    │ 2. utils.auth.authenticate_with_backend() 호출
    ▼
utils/auth.py
    │
    │ 3. POST http://backend:8000/api/auth/login
    │    Body: {user_id, password}
    ▼
Backend: routes_auth.py
    │
    │ 4. DB에서 사용자 조회 (user_id or email)
    │ 5. verify_password() - bcrypt 검증
    ▼
Backend: auth.py
    │
    │ 6. create_access_token() - JWT 생성
    │    Payload: {sub: user_id, role: user.role, exp: 1시간}
    ▼
Backend: routes_auth.py
    │
    │ 7. last_login 업데이트
    │ 8. 200 OK 응답
    │    Body: {user_id, user_name, email, role, access_token}
    ▼
Frontend: utils/auth.py
    │
    │ 9. login_user() 호출
    ▼
Frontend: session_manager.py
    │
    │ 10. st.session_state에 세션 저장
    │     - logged_in = True
    │     - user_id, user_name, role, access_token
    │     - login_time, last_activity
    ▼
Frontend: app.py
    │
    │ 11. 메인 페이지 렌더링
    │ 12. render_header() - 로그인 상태 표시
    ▼
User Browser
```

---

### 3️⃣ **세션 관리 프로세스**

```
매 페이지 로드 시:

app.py / pages/*.py
    │
    │ 1. init_session_state() 호출
    ▼
session_manager.py
    │
    │ 2. 세션 존재 확인
    │ 3. check_session_timeout() 호출
    │    - last_activity 체크
    │    - 1시간 이상 경과 시 clear_session()
    │ 4. update_last_activity()
    ▼
app.py
    │
    │ 5. 타임아웃 시 경고 메시지
    │ 6. 정상 시 페이지 렌더링
    ▼
User Browser
```

---

### 4️⃣ **관리자 기능 프로세스**

```
Admin User Browser
    │
    │ 1. 관리자 페이지 접근 (pages/admin/users.py)
    ▼
admin_auth.py
    │
    │ 2. require_admin() 체크
    │    - is_logged_in()
    │    - user.role in ['admin', 'super_admin']
    ▼
pages/admin/users.py
    │
    │ 3. GET http://backend:8000/api/admin/users
    │    Headers: {Authorization: Bearer {access_token}}
    ▼
Backend: routes_admin.py
    │
    │ 4. require_admin() dependency
    │    - JWT 검증
    │    - 역할 확인
    ▼
Backend: models.py
    │
    │ 5. DB에서 사용자 목록 조회
    │ 6. 페이지네이션 처리
    ▼
Frontend: pages/admin/users.py
    │
    │ 7. 사용자 목록 표시
    │ 8. 관리 기능 (수정/삭제)
    ▼
Admin User Browser
```

---

### 5️⃣ **주식 데이터 조회 프로세스**

```
User Browser
    │
    │ 1. 메인 페이지 접속 (app.py)
    ▼
app.py
    │
    │ 2. load_market_data() 호출
    ▼
FinanceDataReader (fdr)
    │
    │ 3. 시간 체크
    │    - 9시 이전: fdr.StockListing('KOSPI') + 'KOSDAQ'
    │    - 9시 이후: fdr.StockListing('KRX')
    ▼
app.py
    │
    │ 4. 데이터 처리
    │    - 시가총액 정렬
    │    - 상위/하위 20개 필터링
    │    - 등락률 색상 적용
    ▼
Streamlit
    │
    │ 5. st.dataframe()으로 렌더링
    ▼
User Browser
```

---

## 🔐 보안 아키텍처

### **인증 흐름**

1. **비밀번호 해싱**: bcrypt (salt + hash)
2. **JWT 토큰**:
   - Algorithm: HS256
   - Expiry: 1시간
   - Payload: {sub: user_id, role, exp}
3. **세션 관리**: Streamlit session_state (서버 측)
4. **세션 타임아웃**: 1시간 비활동 시 자동 로그아웃

### **권한 관리 (RBAC)**

```
Roles:
├── user (일반 사용자)
│   └── 주식 데이터 조회
├── admin (관리자)
│   ├── user 관리 가능
│   └── 감사 로그 조회
└── super_admin (슈퍼 관리자)
    ├── 모든 사용자 관리
    └── 관리자 승격/강등
```

---

## 📊 데이터베이스 스키마

### **users 테이블**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT valid_role CHECK (role IN ('user', 'admin', 'super_admin'))
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### **audit_logs 테이블**

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    admin_id VARCHAR(100) REFERENCES users(user_id) ON DELETE CASCADE,
    admin_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    target VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_admin_id ON audit_logs(admin_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
```

---

## 🚀 개선 방향 및 대안

### ✅ **현재 잘 구현된 부분**

1. ✅ **마이크로서비스 분리**: Frontend/Backend 명확히 분리
2. ✅ **Docker 컨테이너화**: 일관된 개발/배포 환경
3. ✅ **REST API 설계**: 표준 HTTP 메서드 사용
4. ✅ **ORM 사용**: SQLAlchemy로 DB 추상화
5. ✅ **JWT 인증**: 표준 토큰 기반 인증
6. ✅ **RBAC 구현**: 역할 기반 접근 제어

---

### 🔧 **개선이 필요한 부분**

#### 1️⃣ **Redis 세션 관리 미구현**

**현재 문제**:
- Streamlit session_state는 **서버 메모리**에만 저장
- 서버 재시작 시 모든 세션 손실
- 멀티 인스턴스 환경에서 세션 공유 불가

**개선 방안**:
```python
# backend/utils/redis_session.py (신규)
import redis
from typing import Optional

redis_client = redis.Redis(
    host='redis',
    port=6379,
    password='redis123',
    decode_responses=True
)

def save_session(token: str, user_data: dict, expire: int = 3600):
    """JWT 토큰을 키로 세션 저장"""
    redis_client.setex(
        f"session:{token}",
        expire,
        json.dumps(user_data)
    )

def get_session(token: str) -> Optional[dict]:
    """JWT 토큰으로 세션 조회"""
    data = redis_client.get(f"session:{token}")
    return json.loads(data) if data else None

def invalidate_session(token: str):
    """세션 무효화 (로그아웃)"""
    redis_client.delete(f"session:{token}")
```

---

#### 2️⃣ **환경 변수 관리 부족**

**현재 문제**:
- `.env` 파일 없음
- 하드코딩된 시크릿 키: `"your-secret-key-change-in-production"`

**개선 방안**:
```bash
# .env 파일 생성
POSTGRES_DB=secondarymarket
POSTGRES_USER=admin
POSTGRES_PASSWORD=strong_password_here
REDIS_PASSWORD=redis_strong_password
SECRET_KEY=generated_secret_key_256bits
PGADMIN_EMAIL=admin@secondarymarket.com
PGADMIN_PASSWORD=pgadmin_password
```

```python
# backend/config.py (신규)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

---

#### 3️⃣ **API 에러 처리 개선**

**현재 문제**:
- 프론트엔드에서 단순히 "서버 연결 오류" 표시
- 상세한 에러 정보 부족

**개선 방안**:
```python
# frontend/utils/auth.py
def authenticate_with_backend(user_id: str, password: str):
    try:
        response = requests.post(...)

        if response.status_code == 200:
            return True, response.json(), None
        elif response.status_code == 401:
            return False, None, "아이디 또는 비밀번호가 올바르지 않습니다."
        elif response.status_code == 403:
            return False, None, "계정이 비활성화되었습니다. 관리자에게 문의하세요."
        elif response.status_code == 500:
            return False, None, "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        else:
            error_detail = response.json().get('detail', '알 수 없는 오류')
            return False, None, f"오류: {error_detail}"
    except requests.Timeout:
        return False, None, "서버 응답 시간이 초과되었습니다."
    except requests.ConnectionError:
        return False, None, "서버에 연결할 수 없습니다."
    except Exception as e:
        return False, None, f"예상치 못한 오류: {str(e)}"
```

---

#### 4️⃣ **로깅 시스템 부재**

**현재 문제**:
- 에러 추적 어려움
- 사용자 활동 모니터링 불가

**개선 방안**:
```python
# backend/logger.py (신규)
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("secondarymarket")
    logger.setLevel(logging.INFO)

    # 파일 핸들러 (최대 10MB, 5개 백업)
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10_000_000,
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

# 사용 예시
logger.info(f"User {user_id} logged in")
logger.error(f"Failed login attempt for {user_id}")
```

---

#### 5️⃣ **API Rate Limiting 부재**

**현재 문제**:
- 무제한 API 호출 가능
- DDoS 공격에 취약

**개선 방안**:
```python
# backend/middleware/rate_limit.py (신규)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# main.py에 추가
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# routes_auth.py에 적용
@router.post("/login")
@limiter.limit("5/minute")  # 1분에 5번만 허용
def login(request: Request, credentials: LoginRequest, ...):
    ...
```

---

#### 6️⃣ **DB 마이그레이션 도구 부재**

**현재 문제**:
- 스키마 변경 시 수동 SQL 실행 필요
- 버전 관리 어려움

**개선 방안**:
```bash
# Alembic 사용
pip install alembic

# 초기화
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Add new column to users"

# 마이그레이션 적용
alembic upgrade head
```

---

#### 7️⃣ **캐싱 전략 개선**

**현재 문제**:
- FinanceDataReader API 반복 호출
- 5분 캐시는 Streamlit 서버 메모리에만 저장

**개선 방안**:
```python
# backend/cache.py (신규)
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=1)

def cache_result(expire: int = 300):
    """Redis 캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # 캐시 확인
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 함수 실행
            result = func(*args, **kwargs)

            # 캐시 저장
            redis_client.setex(cache_key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

# 사용 예시
@cache_result(expire=300)  # 5분 캐시
def get_market_data():
    return fdr.StockListing('KRX').to_dict()
```

---

#### 8️⃣ **테스트 코드 부재**

**개선 방안**:
```python
# backend/tests/test_auth.py (신규)
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/api/auth/register", json={
        "user_id": "testuser",
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["user_id"] == "testuser"

def test_login_success():
    response = client.post("/api/auth/login", json={
        "user_id": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

#### 9️⃣ **CI/CD 파이프라인 구축**

**개선 방안**:
```yaml
# .github/workflows/ci.yml (신규)
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose exec backend pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # 배포 스크립트
```

---

## 📈 성능 최적화 제안

### 1️⃣ **DB 쿼리 최적화**
```python
# 현재: N+1 쿼리 문제 가능성
users = db.query(User).all()
for user in users:
    print(user.audit_logs)  # 각 사용자마다 쿼리 실행

# 개선: Eager Loading
users = db.query(User).options(joinedload(User.audit_logs)).all()
```

### 2️⃣ **DB Connection Pooling**
```python
# database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # 현재 5 → 10
    max_overflow=20,     # 현재 10 → 20
    pool_pre_ping=True
)
```

### 3️⃣ **비동기 처리**
```python
# FastAPI async 사용
@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

---

## 🔒 보안 강화 제안

1. **HTTPS 적용** (프로덕션 필수)
2. **SQL Injection 방어** (ORM 사용으로 이미 구현)
3. **XSS 방어** (Streamlit 자동 처리)
4. **CSRF 토큰** (Streamlit 자동 처리)
5. **비밀번호 정책 강화**:
   ```python
   - 최소 8자 이상
   - 대문자, 소문자, 숫자, 특수문자 포함
   - 비밀번호 재사용 방지
   ```

---

## 📊 모니터링 도구 추가

```yaml
# docker-compose.yml에 추가
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  depends_on:
    - prometheus
```

---

## 🎯 우선순위별 개선 로드맵

### **Phase 1: 긴급 (1주)**
1. ✅ 환경 변수 관리 (.env 파일)
2. ✅ SECRET_KEY 강화
3. ✅ 로깅 시스템 구축

### **Phase 2: 중요 (2-4주)**
4. ✅ Redis 세션 관리 구현
5. ✅ API Rate Limiting
6. ✅ 에러 처리 개선
7. ✅ 테스트 코드 작성

### **Phase 3: 개선 (1-2개월)**
8. ✅ DB 마이그레이션 (Alembic)
9. ✅ CI/CD 파이프라인
10. ✅ 캐싱 전략 개선
11. ✅ 모니터링 도구

### **Phase 4: 최적화 (3개월+)**
12. ✅ 비동기 처리
13. ✅ 성능 최적화
14. ✅ 고가용성 구성

---

## 📌 결론

**강점**:
- 깔끔한 아키텍처 설계
- Docker 기반 인프라
- REST API 표준 준수
- RBAC 구현

**개선 필요**:
- Redis 세션 관리
- 로깅 및 모니터링
- 테스트 자동화
- 보안 강화

현재 프로젝트는 **MVP(Minimum Viable Product)** 단계로 잘 구성되어 있으며, 위의 개선 사항들을 단계적으로 적용하면 **프로덕션 레벨**의 시스템으로 발전할 수 있습니다.
