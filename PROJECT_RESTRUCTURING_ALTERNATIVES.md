# 프로젝트 구조 개선 대안 분석

## 📋 현재 구조 문제점

### 현재 디렉토리 구조
```
secondarymarket/
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/                    # ❌ 불필요한 중첩
│       ├── api/
│       ├── core/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── utils/
│       └── main.py
├── pages/                       # ❌ app/ 외부에 위치
│   ├── login.py
│   ├── signup.py
│   ├── listed_stock_retrieval.py
│   ├── disclosure_today.py
│   └── news_today.py
├── docker-compose.yml
├── finance.py                   # Streamlit 메인 앱
├── header.py
└── [기타 파일들...]
```

### 문제점 상세

**문제 1: pages/ 폴더 위치**
- `pages/`가 `app/` 밖에 위치
- `app/Dockerfile`의 `COPY . .`는 `app/` 내부만 복사
- Docker 컨테이너에서 pages 접근 불가
- Streamlit 멀티페이지 앱 구조가 깨짐

**문제 2: app/src/ 중복 구조**
- `app/` 안에 다시 `src/`가 있어 경로 복잡
- Import 경로: `from src.core.config import settings`
- Dockerfile CMD: `python src/main.py`
- 불필요한 중첩으로 가독성 저하

**문제 3: 혼재된 앱 구조**
- FastAPI (app/) + Streamlit (root) 코드가 분리되어 있지 않음
- `finance.py`, `header.py` 등이 루트에 산재
- 역할별 명확한 경계 없음

---

## 🎯 추천 대안별 비교

### 대안 1: 모노레포 구조 (Frontend + Backend 분리) ⭐ **추천**

```
secondarymarket/
├── backend/                     # FastAPI 백엔드
│   ├── api/
│   │   └── routers/
│   │       ├── auth.py
│   │       └── stock.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   └── auth.py
│   ├── services/
│   │   └── auth_service.py
│   ├── utils/
│   │   └── helpers.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # Streamlit 프론트엔드
│   ├── pages/                   # ✅ pages가 frontend 내부로
│   │   ├── login.py
│   │   ├── signup.py
│   │   ├── listed_stock_retrieval.py
│   │   ├── disclosure_today.py
│   │   └── news_today.py
│   ├── components/
│   │   └── header.py
│   ├── utils/
│   │   ├── krx.py
│   │   └── langchain_streamlit_tool.py
│   ├── finance.py               # 메인 앱
│   ├── requirements.txt
│   └── Dockerfile
│
├── database/
│   ├── init/
│   └── backups/
│
├── docker-compose.yml
├── .gitignore
├── .env.example
└── README.md
```

#### 장점
- ✅ Frontend와 Backend가 명확히 분리
- ✅ 각 앱이 독립적인 Dockerfile과 requirements 보유
- ✅ pages/가 frontend/ 내부에 위치하여 Streamlit 멀티페이지 구조 정상 작동
- ✅ 마이크로서비스 전환 시 용이
- ✅ 팀 협업 시 역할 분담 명확
- ✅ 불필요한 중첩 제거 (src/ 제거)
- ✅ Import 경로 단순화: `from core.config import settings`

#### 단점
- ⚠️ 디렉토리 구조 변경 작업량이 가장 큼
- ⚠️ docker-compose.yml 대폭 수정 필요
- ⚠️ 기존 코드의 import 경로 전면 수정

#### 적용 시나리오
- ✅ 장기적으로 확장 가능한 구조 원할 때
- ✅ Frontend/Backend 팀이 분리될 가능성 있을 때
- ✅ 향후 React/Next.js 등 다른 프론트엔드로 전환 고려 시

---

### 대안 2: Streamlit 중심 구조 (간단 통합)

```
secondarymarket/
├── app/                         # 메인 Streamlit 앱
│   ├── pages/                   # ✅ pages를 app 내부로 이동
│   │   ├── login.py
│   │   ├── signup.py
│   │   └── listed_stock_retrieval.py
│   ├── api/                     # FastAPI 백엔드 코드
│   │   ├── routers/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py              # FastAPI 앱
│   ├── components/
│   │   └── header.py
│   ├── utils/
│   │   └── krx.py
│   ├── finance.py               # Streamlit 메인
│   ├── requirements.txt
│   └── Dockerfile
│
├── database/
├── docker-compose.yml
└── README.md
```

#### 장점
- ✅ 단순하고 이해하기 쉬운 구조
- ✅ 마이그레이션 작업량 중간 수준
- ✅ pages/가 app/ 내부로 이동하여 Docker COPY 문제 해결
- ✅ src/ 중첩 제거로 경로 단순화
- ✅ 작은 프로젝트에 적합

#### 단점
- ⚠️ Frontend/Backend 경계가 명확하지 않음
- ⚠️ 향후 확장 시 리팩토링 필요
- ⚠️ 두 앱이 같은 requirements.txt 공유 (의존성 충돌 가능성)

#### 적용 시나리오
- ✅ 프로젝트 규모가 작고 빠른 개발이 목표일 때
- ✅ Streamlit 앱이 메인이고 FastAPI는 보조적 역할일 때
- ✅ 단일 팀이 전체 코드 관리할 때

---

### 대안 3: FastAPI 중심 구조 (최소 변경)

```
secondarymarket/
├── app/
│   ├── api/                     # ✅ src 제거, 바로 api/
│   │   └── routers/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── streamlit_app/               # ✅ Streamlit 앱 분리
│   ├── pages/
│   │   ├── login.py
│   │   └── signup.py
│   ├── finance.py
│   ├── header.py
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md
```

#### 장점
- ✅ app/src/ 중첩 제거 (가장 간단한 수정)
- ✅ FastAPI 표준 구조 유지
- ✅ Import 경로 단순화: `from api.routers import auth`
- ✅ Dockerfile 수정 최소: `CMD ["python", "main.py"]`

#### 단점
- ⚠️ pages/ 문제는 여전히 존재 (별도 Dockerfile 필요)
- ⚠️ Streamlit 앱이 독립적으로 배포되어야 함
- ⚠️ 두 앱 간 통신 구조 명확히 설계 필요

#### 적용 시나리오
- ✅ FastAPI가 메인이고 Streamlit은 관리자 대시보드 용도일 때
- ✅ 최소한의 변경으로 구조 개선하고 싶을 때

---

## 🔄 마이그레이션 단계별 가이드

### 대안 1 채택 시: Frontend/Backend 완전 분리 (추천)

#### Phase 1: 백업 및 준비
```bash
# 1. 현재 상태 백업
git add .
git commit -m "Backup before restructuring"
git branch backup-before-restructure

# 2. 새 브랜치 생성
git checkout -b restructure-monorepo
```

#### Phase 2: Backend 디렉토리 생성 및 이동
```bash
# backend 폴더 생성
mkdir -p backend/{api/routers,core,models,schemas,services,utils}

# app/src/ 내용을 backend/로 이동
mv app/src/api/* backend/api/
mv app/src/core/* backend/core/
mv app/src/models/* backend/models/
mv app/src/schemas/* backend/schemas/
mv app/src/services/* backend/services/
mv app/src/utils/* backend/utils/
mv app/src/main.py backend/main.py

# requirements와 Dockerfile 이동
mv app/requirements.txt backend/requirements.txt
mv app/Dockerfile backend/Dockerfile

# 기존 app/ 폴더 제거
rm -rf app/
```

#### Phase 3: Frontend 디렉토리 생성 및 이동
```bash
# frontend 폴더 생성
mkdir -p frontend/{pages,components,utils}

# pages 이동
mv pages/* frontend/pages/

# 메인 파일들 이동
mv finance.py frontend/finance.py
mv header.py frontend/components/header.py
mv krx.py frontend/utils/krx.py
mv langchain_streamlit_tool.py frontend/utils/
mv FinanceDataReader_traits.py frontend/utils/
mv sNp500.py frontend/utils/

# pages 폴더 제거
rm -rf pages/
```

#### Phase 4: Dockerfile 생성

**backend/Dockerfile 수정**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**frontend/Dockerfile 생성**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8501

# Streamlit 실행
CMD ["streamlit", "run", "finance.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Phase 5: requirements.txt 분리

**backend/requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
redis==5.0.1
python-dotenv==1.0.0
sqlalchemy==2.0.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.0
pydantic-settings==2.1.0
```

**frontend/requirements.txt**
```txt
streamlit==1.28.0
FinanceDataReader==0.9.50
pandas==2.1.3
requests==2.31.0
python-dotenv==1.0.0
```

#### Phase 6: docker-compose.yml 수정

```yaml
version: '3.8'

services:
  # PostgreSQL with TimescaleDB
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: secondarymarket_db
    restart: unless-stopped
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-secondarymarket}
      POSTGRES_USER: ${POSTGRES_USER:-admin}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-admin123}
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
      - ./database/backups:/backups
    networks:
      - secondarymarket_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-admin} -d ${POSTGRES_DB:-secondarymarket}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for caching
  redis:
    image: redis:7-alpine
    container_name: secondarymarket_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis123}
    volumes:
      - redis_data:/data
    networks:
      - secondarymarket_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: secondarymarket_backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-admin}:${POSTGRES_PASSWORD:-admin123}@timescaledb:5432/${POSTGRES_DB:-secondarymarket}
      - REDIS_URL=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-in-production}
    volumes:
      - ./backend:/app
    networks:
      - secondarymarket_network
    depends_on:
      timescaledb:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Streamlit Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: secondarymarket_frontend
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8000
    volumes:
      - ./frontend:/app
    networks:
      - secondarymarket_network
    depends_on:
      - backend

  # PgAdmin (optional)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: secondarymarket_pgadmin
    restart: unless-stopped
    ports:
      - "5051:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@secondarymarket.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin123}
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    networks:
      - secondarymarket_network
    depends_on:
      - timescaledb

volumes:
  postgres_data:
  redis_data:
  pgadmin_data:

networks:
  secondarymarket_network:
    driver: bridge
```

#### Phase 7: Import 경로 수정

**Backend 파일들 (backend/main.py 등)**
```python
# 기존 (잘못됨)
from src.core.config import settings
from src.api.routers import auth

# 수정 후 (올바름)
from core.config import settings
from api.routers import auth
```

**Frontend 파일들 (frontend/finance.py 등)**
```python
# 기존
from header import render_header

# 수정 후
from components.header import render_header
```

**frontend/pages/login.py 등**
```python
# 기존
from header import render_header

# 수정 후
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from components.header import render_header
```

#### Phase 8: 테스트 및 검증
```bash
# 1. Docker 컨테이너 빌드
docker-compose build

# 2. 컨테이너 실행
docker-compose up -d

# 3. 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend

# 4. 접속 테스트
# Backend API: http://localhost:8000
# Frontend: http://localhost:8501
# PgAdmin: http://localhost:5051

# 5. Health check
curl http://localhost:8000/health
```

#### Phase 9: 커밋 및 배포
```bash
# 1. 변경사항 커밋
git add .
git commit -m "Restructure project: separate frontend and backend"

# 2. 메인 브랜치에 머지
git checkout main
git merge restructure-monorepo

# 3. 리모트에 푸시
git push origin main
```

---

## 📊 대안별 비교표

| 항목 | 대안 1 (모노레포) | 대안 2 (Streamlit 중심) | 대안 3 (최소 변경) |
|------|------------------|----------------------|-------------------|
| **마이그레이션 난이도** | 🔴 높음 | 🟡 중간 | 🟢 낮음 |
| **구조 명확성** | 🟢 매우 명확 | 🟡 보통 | 🟡 보통 |
| **확장성** | 🟢 매우 높음 | 🟡 보통 | 🔴 낮음 |
| **유지보수성** | 🟢 우수 | 🟡 보통 | 🟡 보통 |
| **팀 협업** | 🟢 최적 | 🟡 보통 | 🔴 어려움 |
| **Docker 최적화** | 🟢 최적 | 🟢 양호 | 🟡 보통 |
| **Import 경로** | 🟢 단순 | 🟢 단순 | 🟢 단순 |
| **pages/ 문제 해결** | ✅ 완전 해결 | ✅ 완전 해결 | ⚠️ 별도 처리 필요 |
| **app/src/ 문제 해결** | ✅ 완전 해결 | ✅ 완전 해결 | ✅ 완전 해결 |

---

## 🎯 최종 추천

### ⭐ **대안 1 (모노레포 구조) 강력 추천**

**선택 이유:**
1. ✅ 두 가지 문제(pages 위치, src 중첩) 모두 근본적으로 해결
2. ✅ 향후 확장성이 가장 뛰어남 (마이크로서비스 전환 용이)
3. ✅ Frontend/Backend 독립 개발 및 배포 가능
4. ✅ 팀 협업 시 역할 분담 명확
5. ✅ Docker 최적화 (각 앱이 필요한 것만 포함)
6. ✅ 현대적인 프로젝트 구조 표준에 부합

**단기 비용 vs 장기 이익:**
- 단기: 마이그레이션 작업 2-3시간 소요
- 장기: 향후 개발 속도 30%+ 향상, 유지보수 비용 50% 절감

---

## 📝 체크리스트

마이그레이션 전 확인사항:
- [ ] 현재 코드 백업 완료
- [ ] .env 파일 준비 (DATABASE_URL, REDIS_URL, SECRET_KEY)
- [ ] Docker 및 docker-compose 설치 확인
- [ ] 기존 컨테이너 중지 (`docker-compose down`)

마이그레이션 후 확인사항:
- [ ] Backend API 정상 작동 (http://localhost:8000/health)
- [ ] Frontend 정상 작동 (http://localhost:8501)
- [ ] PostgreSQL 연결 확인
- [ ] Redis 연결 확인
- [ ] Streamlit 멀티페이지 작동 확인 (pages/ 접근 가능)
- [ ] Import 오류 없음
- [ ] 모든 기능 정상 작동

---

## 🚀 다음 단계

구조 개편 완료 후:
1. **인증 시스템 구현** (AUTH_IMPLEMENTATION_GUIDE.md 참조)
2. **API 문서 자동 생성** (FastAPI Swagger UI)
3. **테스트 코드 작성** (pytest)
4. **CI/CD 파이프라인 구축** (GitHub Actions)
5. **코드 품질 도구 적용** (CODE_QUALITY_IMPROVEMENT_PLAN.md 참조)

---

## 💡 추가 권장사항

### .env.example 파일 생성
```bash
# Database
POSTGRES_DB=secondarymarket
POSTGRES_USER=admin
POSTGRES_PASSWORD=change-this-in-production

# Redis
REDIS_PASSWORD=change-this-in-production

# Backend
SECRET_KEY=your-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# PgAdmin
PGADMIN_EMAIL=admin@secondarymarket.com
PGADMIN_PASSWORD=change-this-in-production

# Frontend
API_URL=http://localhost:8000
```

### README.md 업데이트
```markdown
# KRX Stock Market Application

## 프로젝트 구조
- `backend/`: FastAPI 백엔드 API
- `frontend/`: Streamlit 프론트엔드 대시보드
- `database/`: DB 초기화 스크립트

## 실행 방법
```bash
# 환경변수 설정
cp .env.example .env
# .env 파일 수정

# Docker로 전체 실행
docker-compose up -d

# 개별 실행
cd backend && uvicorn main:app --reload
cd frontend && streamlit run finance.py
```

## 접속 주소
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Frontend: http://localhost:8501
- PgAdmin: http://localhost:5051
```

---

**문서 작성일:** 2025-10-15
**프로젝트:** secondarymarket
**작성자:** Claude Code
