# 코드 품질 개선 계획

**프로젝트:** KRX Stock Market Application
**분석 날짜:** 2025-10-15
**현재 상태:** MVP (Minimum Viable Product)

---

## 📊 프로젝트 현황 분석

### 디렉토리 구조

```
secondarymarket/
├── app/                          # FastAPI 백엔드 (새로 추가)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── api/                  # API 라우터
│       │   └── routers/
│       ├── core/                 # 핵심 설정 및 보안
│       ├── models/               # 데이터베이스 모델
│       ├── schemas/              # Pydantic 스키마
│       ├── services/             # 비즈니스 로직
│       ├── utils/                # 유틸리티
│       └── main.py              # 메인 애플리케이션
│
├── pages/                        # Streamlit 페이지
│   ├── listed_stock_retrieval.py (170 lines)
│   ├── login.py                 (64 lines)
│   ├── signup.py                (86 lines)
│   ├── disclosure_today.py      (0 lines - 미구현)
│   └── news_today.py            (0 lines - 미구현)
│
├── database/                     # 데이터베이스 관련
│   ├── init/                    # 초기화 스크립트
│   └── backups/                 # 백업
│
├── docker-compose.yml            # Docker 설정
├── finance.py                    # 메인 Streamlit 앱
├── header.py                     # 공통 헤더
├── langchain_streamlit_tool.py   # LangChain 통합
└── [기타 유틸리티 파일들]
```

### 코드 메트릭

| 항목 | 현재 상태 | 목표 |
|------|-----------|------|
| **총 Python 파일** | 20개 | - |
| **총 코드 라인** | 714 라인 | - |
| **최대 파일 크기** | 170 라인 | < 200 라인 ✅ |
| **테스트 커버리지** | 0% | > 80% ❌ |
| **문서화** | 부분적 | 완전 ❌ |
| **타입 힌팅** | 없음 | 100% ❌ |
| **린팅** | 미설정 | 설정됨 ❌ |

---

## 🎯 코드 품질 지표

### 1. 가독성 (Readability)

**현재 상태:**
- ✅ 파일이 적절한 크기 (최대 170줄)
- ⚠️ 일부 함수가 너무 김 (listed_stock_retrieval.py의 버튼 핸들러)
- ❌ 타입 힌팅 부재
- ⚠️ 문서화 부족

**개선 필요:**
```python
# Before (타입 힌팅 없음)
def color_change(val):
    if val > 0:
        color = 'red'
    return f'color: {color}'

# After (타입 힌팅 추가)
def color_change(val: float) -> str:
    """
    값에 따라 CSS 색상을 반환합니다.

    Args:
        val: 변동률 값

    Returns:
        CSS 색상 문자열 (예: 'color: red')
    """
    if val > 0:
        color = 'red'
    return f'color: {color}'
```

### 2. 유지보수성 (Maintainability)

**현재 상태:**
- ✅ 모듈화된 구조
- ⚠️ 코드 중복 (render_header 호출 반복)
- ❌ 설정 관리 미흡
- ❌ 에러 핸들링 불충분

**개선 필요:**
```python
# Before (하드코딩된 설정)
st.dataframe(df, height=400, width=780)

# After (설정 파일로 관리)
from config import UIConfig
st.dataframe(df, height=UIConfig.DATAFRAME_HEIGHT, width=UIConfig.DATAFRAME_WIDTH)
```

### 3. 테스트 가능성 (Testability)

**현재 상태:**
- ❌ 단위 테스트 없음
- ❌ 통합 테스트 없음
- ❌ 테스트 구조 없음

**필요 사항:**
- `tests/` 디렉토리 생성
- pytest 설정
- 테스트 커버리지 목표 설정

### 4. 보안 (Security)

**현재 상태:**
- ❌ 인증 시스템 미구현
- ⚠️ 환경변수 관리 기본적
- ❌ 입력 검증 부족
- ❌ SQL Injection 방어 미흡

**Critical Issues:**
```python
# login.py - 현재 어떤 입력도 통과
if user_id and password:
    st.success(f"환영합니다, {user_id}님!")  # ❌ 실제 검증 없음
```

### 5. 성능 (Performance)

**현재 상태:**
- ⚠️ 캐싱 부분적 사용
- ❌ 데이터베이스 인덱스 미설정
- ⚠️ API 호출 최적화 필요

**개선 기회:**
```python
# Before (매번 API 호출)
df_krx = fdr.StockListing('KRX')

# After (캐싱 적용)
@st.cache_data(ttl=3600)  # 1시간 캐시
def get_krx_listings():
    return fdr.StockListing('KRX')
```

---

## 🚀 개선 계획 로드맵

### Phase 1: 기반 인프라 (1-2주) - **HIGH PRIORITY**

#### 1.1 개발 환경 설정
```bash
# requirements-dev.txt 생성
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
mypy==1.7.0
pylint==3.0.2
isort==5.12.0
pre-commit==3.5.0
```

**작업 항목:**
- [ ] `requirements-dev.txt` 생성
- [ ] `.pre-commit-config.yaml` 설정
- [ ] `pyproject.toml` 또는 `setup.cfg` 설정
- [ ] CI/CD 파이프라인 기본 설정

#### 1.2 코드 포맷팅 표준화
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--extend-ignore=E203,W503']
```

**실행:**
```bash
# 설치
pip install pre-commit
pre-commit install

# 모든 파일에 적용
pre-commit run --all-files
```

#### 1.3 설정 관리 중앙화

**파일 구조:**
```python
# config/settings.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # 애플리케이션
    APP_NAME: str = "KRX Stock Market"
    DEBUG: bool = False

    # UI 설정
    DATAFRAME_HEIGHT: int = 400
    DATAFRAME_WIDTH: int = 780

    # API
    API_BASE_URL: str = "http://localhost:8000"

    # 데이터베이스
    DATABASE_URL: str

    # 캐싱
    CACHE_TTL: int = 3600

    class Config:
        env_file = Path(__file__).parent.parent / '.env'
        case_sensitive = True

settings = Settings()
```

### Phase 2: 인증 시스템 구현 (2-3주) - **CRITICAL**

#### 2.1 데이터베이스 스키마
```sql
-- database/init/01_create_tables.sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    device_info VARCHAR(255)
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
```

#### 2.2 FastAPI 인증 구현 체크리스트
- [ ] `app/src/core/config.py` - 설정 관리
- [ ] `app/src/core/security.py` - JWT & 비밀번호 해싱
- [ ] `app/src/models/user.py` - SQLAlchemy 모델
- [ ] `app/src/schemas/user.py` - Pydantic 스키마
- [ ] `app/src/services/auth_service.py` - 인증 로직
- [ ] `app/src/api/routers/auth.py` - 인증 API
- [ ] `app/src/api/dependencies.py` - 인증 의존성

#### 2.3 Streamlit 통합
```python
# utils/api_client.py
import requests
import streamlit as st
from typing import Optional, Dict, Any

def api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    require_auth: bool = True
) -> requests.Response:
    """인증된 API 요청"""
    url = f"{settings.API_BASE_URL}{endpoint}"
    headers = {}

    if require_auth:
        token = st.session_state.get("access_token")
        if not token:
            st.error("로그인이 필요합니다.")
            st.switch_page("pages/login.py")
            st.stop()
        headers["Authorization"] = f"Bearer {token}"

    return requests.request(method, url, json=data, headers=headers)
```

### Phase 3: 테스트 커버리지 (3-4주)

#### 3.1 테스트 구조
```
tests/
├── __init__.py
├── conftest.py              # pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_auth_service.py
│   ├── test_stock_service.py
│   └── test_security.py
├── integration/
│   ├── __init__.py
│   ├── test_api_auth.py
│   └── test_api_stocks.py
└── e2e/
    ├── __init__.py
    └── test_user_flow.py
```

#### 3.2 예시 테스트
```python
# tests/unit/test_auth_service.py
import pytest
from app.src.services.auth_service import AuthService
from app.src.schemas.user import UserCreate

@pytest.fixture
def auth_service(db_session):
    return AuthService(db_session)

def test_register_user_success(auth_service):
    """회원가입 성공 테스트"""
    user_data = UserCreate(
        user_id="testuser",
        email="test@example.com",
        password="SecurePass123!",
        password_confirm="SecurePass123!",
        name="테스트 사용자",
        agree=True
    )

    user = auth_service.register_user(user_data)

    assert user.user_id == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash != "SecurePass123!"  # 해싱됨
    assert user.is_active is True

def test_register_user_duplicate(auth_service):
    """중복 아이디 회원가입 실패 테스트"""
    user_data = UserCreate(...)

    auth_service.register_user(user_data)

    with pytest.raises(HTTPException) as exc:
        auth_service.register_user(user_data)

    assert exc.value.status_code == 409
    assert "이미 존재하는 아이디" in exc.value.detail
```

#### 3.3 커버리지 목표
```bash
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=app/src
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

# 실행
pytest --cov=app/src --cov-report=html
```

### Phase 4: 코드 리팩토링 (4-6주)

#### 4.1 listed_stock_retrieval.py 리팩토링

**현재 문제:**
- 170줄 중 123줄이 하나의 버튼 핸들러 안에 있음
- 데이터 조회, 처리, 표시 로직이 혼재

**개선 후:**
```python
# services/stock_service.py
from typing import Optional, Dict, Any
import pandas as pd
import FinanceDataReader as fdr

class StockService:
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_krx_listings() -> pd.DataFrame:
        """KRX 상장 종목 전체 조회 (캐싱)"""
        return fdr.StockListing('KRX')

    @staticmethod
    def search_by_name(stock_name: str) -> Optional[pd.DataFrame]:
        """종목명으로 검색"""
        df_krx = StockService.get_krx_listings()
        matched = df_krx[df_krx['Name'] == stock_name]
        return matched if not matched.empty else None

    @staticmethod
    def get_price_history(ticker: str, start_year: str) -> pd.DataFrame:
        """종목 가격 이력 조회"""
        try:
            return fdr.DataReader(ticker, start_year)
        except ConnectionError:
            raise StockServiceError("네트워크 연결을 확인해주세요.")
        except ValueError:
            raise StockServiceError("잘못된 종목 코드입니다.")

    @staticmethod
    def calculate_52week_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """52주 통계 계산"""
        today = datetime.now()
        one_year_ago = today - timedelta(weeks=52)
        df_52weeks = df[df.index >= one_year_ago]

        if len(df_52weeks) == 0:
            return None

        return {
            'high': df_52weeks['Close'].max(),
            'low': df_52weeks['Close'].min(),
            'avg': df_52weeks['Close'].mean(),
            'current': df_52weeks['Close'].iloc[0],
            'high_date': df_52weeks['Close'].idxmax(),
            'low_date': df_52weeks['Close'].idxmin(),
        }

# pages/listed_stock_retrieval.py (간결해짐)
if st.button("조회"):
    stock_service = StockService()

    # 1. 검색
    matched = stock_service.search_by_name(stock_name)
    if not matched:
        st.error(f"'{stock_name}' 종목을 찾을 수 없습니다.")
        return

    # 2. 데이터 조회
    ticker = matched.iloc[0]['Code']
    df = stock_service.get_price_history(ticker, start_year)

    # 3. 표시
    display_stock_data(df, ticker, stock_name)
    display_charts(df)

    # 4. 통계
    stats = stock_service.calculate_52week_stats(df)
    if stats:
        display_statistics(stats)
```

#### 4.2 공통 컴포넌트 추출
```python
# components/base_page.py
import streamlit as st
from header import render_header
from abc import ABC, abstractmethod

class BasePage(ABC):
    def __init__(self, title: str, icon: str = "📊"):
        st.set_page_config(page_title=title, page_icon=icon, layout="wide")
        render_header()
        self.title = title
        self.icon = icon

    @abstractmethod
    def render(self):
        """페이지 렌더링 (서브클래스에서 구현)"""
        pass

    def run(self):
        """페이지 실행"""
        st.title(f"{self.icon} {self.title}")
        self.render()

# 사용
class StockRetrievalPage(BasePage):
    def __init__(self):
        super().__init__("상장종목조회", "📊")

    def render(self):
        # 실제 페이지 로직
        ...
```

#### 4.3 에러 핸들링 표준화
```python
# utils/exceptions.py
class AppException(Exception):
    """기본 애플리케이션 예외"""
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class StockServiceError(AppException):
    """주식 서비스 관련 에러"""
    pass

class AuthenticationError(AppException):
    """인증 관련 에러"""
    pass

# utils/error_handler.py
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def handle_error(func):
    """에러 핸들링 데코레이터"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StockServiceError as e:
            st.error(f"주식 데이터 오류: {e.message}")
            logger.error(f"StockServiceError: {e.code} - {e.message}")
        except AuthenticationError as e:
            st.error(f"인증 오류: {e.message}")
            st.switch_page("pages/login.py")
        except Exception as e:
            st.error("일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
            logger.exception("Unexpected error occurred")
    return wrapper
```

### Phase 5: 문서화 (병행 작업)

#### 5.1 코드 문서화
```python
# Google Style Docstring 사용
def calculate_52week_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """52주 통계를 계산합니다.

    Args:
        df: 주식 가격 데이터프레임. 인덱스는 날짜여야 합니다.

    Returns:
        다음 키를 포함하는 딕셔너리:
        - high: 52주 최고가
        - low: 52주 최저가
        - avg: 52주 평균가
        - current: 현재가
        - high_date: 최고가 달성일
        - low_date: 최저가 달성일

    Raises:
        ValueError: 데이터프레임이 비어있거나 52주 데이터가 부족한 경우

    Example:
        >>> df = fdr.DataReader('005930', '2023')
        >>> stats = calculate_52week_stats(df)
        >>> print(f"최고가: {stats['high']}")
    """
    ...
```

#### 5.2 API 문서
- ✅ OpenAPI 3.0 명세 (이미 생성됨)
- [ ] Swagger UI 활성화
- [ ] Redoc 활성화
- [ ] API 사용 가이드 작성

#### 5.3 사용자 문서
```
docs/
├── README.md              # 프로젝트 소개
├── INSTALLATION.md        # 설치 가이드
├── USAGE.md               # 사용 가이드
├── API.md                 # API 레퍼런스
├── DEVELOPMENT.md         # 개발 가이드
└── DEPLOYMENT.md          # 배포 가이드
```

### Phase 6: 성능 최적화 (5-6주)

#### 6.1 데이터베이스 최적화
```sql
-- 인덱스 추가
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_login_history_user_id_login_at ON login_history(user_id, login_at DESC);

-- 파티셔닝 (로그인 이력)
CREATE TABLE login_history (
    id SERIAL,
    user_id INTEGER,
    login_at TIMESTAMP,
    ...
) PARTITION BY RANGE (login_at);

CREATE TABLE login_history_2024 PARTITION OF login_history
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

#### 6.2 캐싱 전략
```python
# Redis 캐싱
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_result(ttl: int = 3600):
    """Redis 캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # 캐시 확인
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 실제 함수 실행
            result = func(*args, **kwargs)

            # 캐시 저장
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

@cache_result(ttl=1800)  # 30분 캐시
def get_stock_data(ticker: str):
    return fdr.DataReader(ticker)
```

#### 6.3 API 호출 최적화
```python
# 비동기 처리
import asyncio
import httpx

async def fetch_multiple_stocks(tickers: list[str]) -> dict:
    """여러 종목 데이터를 병렬로 조회"""
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(f"/api/stocks/{ticker}")
            for ticker in tickers
        ]
        responses = await asyncio.gather(*tasks)
        return {
            ticker: response.json()
            for ticker, response in zip(tickers, responses)
        }
```

---

## 📏 품질 지표 목표

### 단계별 목표

| 단계 | 기간 | 테스트 커버리지 | 타입 힌팅 | 문서화 | 린팅 통과율 |
|------|------|----------------|----------|--------|------------|
| **Phase 1** | 1-2주 | 0% | 0% | 20% | 50% |
| **Phase 2** | 3주 | 20% | 30% | 40% | 70% |
| **Phase 3** | 4주 | 60% | 60% | 60% | 90% |
| **Phase 4** | 5주 | 75% | 80% | 80% | 95% |
| **Phase 5** | 6주 | 85% | 100% | 100% | 100% |

### 최종 목표 (6주 후)
- ✅ 테스트 커버리지: 85%+
- ✅ 타입 힌팅: 100%
- ✅ 문서화: 모든 public API 문서화
- ✅ 린팅: 0 errors, 0 warnings
- ✅ 보안: OWASP Top 10 대응
- ✅ 성능: API 응답 < 200ms (p95)

---

## 🛠️ 도구 및 자동화

### 개발 도구 스택
```bash
# 코드 품질
black                # 코드 포맷팅
isort                # import 정렬
flake8               # 린팅
pylint               # 정적 분석
mypy                 # 타입 체킹

# 테스팅
pytest               # 테스트 프레임워크
pytest-cov           # 커버리지
pytest-asyncio       # 비동기 테스트
pytest-mock          # 모킹

# 보안
bandit               # 보안 취약점 검사
safety               # 의존성 보안 검사

# 문서화
sphinx               # 문서 생성
pdoc                 # API 문서 자동 생성
```

### CI/CD 파이프라인
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with flake8
        run: flake8 .

      - name: Type check with mypy
        run: mypy app/src

      - name: Test with pytest
        run: pytest --cov=app/src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

      - name: Security check
        run: |
          bandit -r app/src
          safety check
```

---

## 📊 진행 상황 추적

### KPI (Key Performance Indicators)

| KPI | 현재 | 목표 | 측정 방법 |
|-----|------|------|----------|
| 테스트 커버리지 | 0% | 85% | `pytest --cov` |
| 코드 중복률 | 미측정 | < 3% | `pylint --duplicate-code` |
| 순환복잡도 | 양호 | < 10 | `radon cc` |
| 유지보수성 지수 | 미측정 | A등급 | `radon mi` |
| 타입 커버리지 | 0% | 100% | `mypy --strict` |
| 보안 취약점 | 미검사 | 0 | `bandit` |
| API 응답시간 (p95) | 미측정 | < 200ms | Prometheus |
| 에러율 | 미측정 | < 0.1% | Sentry |

### 주간 리뷰 체크리스트
- [ ] 코드 리뷰 완료
- [ ] 테스트 추가 및 통과
- [ ] 문서 업데이트
- [ ] 성능 테스트
- [ ] 보안 검사
- [ ] 기술 부채 로그 업데이트

---

## 🎯 우선순위별 실행 계획

### 🔴 Critical (즉시 시작)
1. ✅ Docker + PostgreSQL 설치 완료
2. ⏭️ 인증 시스템 구현
3. ⏭️ 기본 테스트 구조 설정

### 🟠 High (1-2주 내)
4. 개발 환경 표준화 (linting, formatting)
5. 설정 관리 중앙화
6. 에러 핸들링 표준화

### 🟡 Medium (2-4주 내)
7. 테스트 커버리지 80% 달성
8. 타입 힌팅 추가
9. 코드 리팩토링

### 🟢 Low (4-6주 내)
10. 성능 최적화
11. 문서화 완성
12. CI/CD 파이프라인 구축

---

## 📚 참고 자료

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/best-practices/)
- [pytest Documentation](https://docs.pytest.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**다음 단계:** 인증 시스템 구현 시작
**연관 문서:** [AUTH_IMPLEMENTATION_GUIDE.md](./AUTH_IMPLEMENTATION_GUIDE.md)
