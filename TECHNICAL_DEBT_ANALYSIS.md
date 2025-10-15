# 기술 부채 분석 보고서

**프로젝트:** KRX Stock Market Application
**분석 날짜:** 2024-01-15
**분석 도구:** 수동 코드 리뷰 + 정적 분석

---

## 📊 Executive Summary

### 전체 프로젝트 현황
- **총 Python 파일 수:** 11개
- **총 코드 라인 수:** 664 라인
- **300+ 라인 파일:** 0개 ✅
- **순환복잡도 15+ 함수:** 0개 ✅

### 주요 발견사항
프로젝트는 전반적으로 **양호한 상태**이지만, 다음과 같은 개선이 필요합니다:

1. **인증 시스템 미구현** (Critical)
2. **데이터베이스 연동 부재** (High)
3. **코드 중복** (Medium)
4. **에러 핸들링 부족** (Medium)
5. **환경 설정 관리 미흡** (Low)

---

## 📈 파일별 코드 분석

### 라인 수 기준 분석

| 파일명 | 라인 수 | 복잡도 등급 | 우선순위 |
|--------|---------|-------------|----------|
| `pages/listed_stock_retrieval.py` | 170 | Medium | High |
| `header.py` | 110 | Low | Medium |
| `langchain_streamlit_tool.py` | 95 | Medium | High |
| `pages/signup.py` | 86 | Low | High |
| `finance.py` | 82 | Low | Low |
| `pages/login.py` | 64 | Low | High |
| `FinanceDataReader_traits.py` | 28 | Low | Low |
| `krx.py` | 24 | Low | Low |
| `sNp500.py` | 5 | Low | Low |
| `pages/disclosure_today.py` | 0 | N/A | High |
| `pages/news_today.py` | 0 | N/A | High |

---

## 🔍 세부 분석

### 1. `pages/listed_stock_retrieval.py` (170 lines)

**현재 상태:**
- 가장 긴 파일이지만 300라인 미만으로 양호
- 단일 기능(종목 조회)에 집중

**발견된 문제:**

#### 1.1 복잡한 함수 구조
```python
# 라인 47-170: 버튼 클릭 핸들러 내부 로직이 123라인
if st.button("조회", key="btn_by_name", type="primary"):
    # 123 lines of nested logic
```
**순환복잡도 추정:** ~8-10 (허용 범위)

**문제점:**
- 하나의 버튼 핸들러에 너무 많은 로직
- 데이터 처리, 표시, 통계 계산이 혼재

**권장사항:**
```python
# 함수로 분리
def fetch_stock_data(ticker, start_year):
    """주식 데이터 조회"""
    pass

def calculate_statistics(df, weeks=52):
    """통계 정보 계산"""
    pass

def display_stock_data(df, ticker, name):
    """데이터 표시"""
    pass
```

#### 1.2 에러 핸들링 부족
```python
try:
    df = fdr.DataReader(ticker, start_year)
    # ... 많은 로직
except Exception as e:
    st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")
```

**문제점:**
- 너무 광범위한 Exception 처리
- 특정 오류에 대한 구체적 처리 없음

**권장사항:**
```python
try:
    df = fdr.DataReader(ticker, start_year)
except ConnectionError:
    st.error("네트워크 연결을 확인해주세요.")
except ValueError:
    st.error("잘못된 종목 코드입니다.")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    st.error("일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
```

#### 1.3 스타일 적용 deprecated 메서드
```python
styled_df = df_sorted_renamed.style.applymap(
    color_change,
    subset=['전일대비']
)
```

**문제점:**
- `applymap`은 pandas 2.1.0부터 deprecated
- `map`으로 변경 필요

---

### 2. `langchain_streamlit_tool.py` (95 lines)

**현재 상태:**
- LangChain + OpenAI 통합
- 재귀 호출 패턴 사용

**발견된 문제:**

#### 2.1 무한 재귀 위험
```python
def get_ai_response(messages):
    # ...
    if gethered.tool_calls:
        # ...
        for chunk in get_ai_response(st.session_state["messages"]):  # ← 재귀
            yield chunk
```

**순환복잡도:** ~5-7 (양호)

**문제점:**
- 재귀 깊이 제한 없음
- 무한 루프 가능성

**권장사항:**
```python
def get_ai_response(messages, max_iterations=5):
    iteration = 0
    while iteration < max_iterations:
        response = llm_with_tools.stream(messages)
        # ... 로직
        if not gathered.tool_calls:
            break
        iteration += 1

    if iteration >= max_iterations:
        raise MaxIterationsExceeded("Tool call limit reached")
```

#### 2.2 API 키 하드코딩 위험
```python
load_dotenv('../.env')
api_key = os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.9, api_key=api_key)
```

**문제점:**
- 상대 경로 사용
- API 키 검증 없음

**권장사항:**
```python
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")
```

#### 2.3 불완전한 코드
```python
result=st.chat_message("assistant").write_stream(response)
st  # ← 미완성 라인
```

---

### 3. `header.py` (110 lines)

**현재 상태:**
- UI 컴포넌트
- 주로 CSS와 레이아웃

**발견된 문제:**

#### 3.1 CSS 인라인 정의
```python
st.markdown("""
    <style>
    /* 70+ lines of CSS */
    </style>
""", unsafe_allow_html=True)
```

**문제점:**
- CSS가 Python 코드에 혼재
- 유지보수 어려움
- 재사용 불가

**권장사항:**
```python
# static/styles.css 파일로 분리
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 사용
load_css('static/header.css')
```

---

### 4. 인증 관련 파일 (`login.py`, `signup.py`)

**현재 상태:**
- UI만 구현됨
- 실제 인증 로직 없음

**발견된 문제:**

#### 4.1 모의 인증 (Mock Authentication)
```python
# login.py
if submit_button:
    if user_id and password:
        # 여기에 실제 로그인 로직 추가
        st.success(f"환영합니다, {user_id}님!")
```

**문제점:**
- 어떤 입력도 통과 (보안 취약)
- 세션 관리 없음
- 데이터베이스 연동 없음

#### 4.2 비밀번호 검증 부재
```python
# signup.py
if password != password_confirm:
    st.error("비밀번호가 일치하지 않습니다.")
```

**문제점:**
- 비밀번호 강도 검증 없음
- 해싱 없음
- 평문 전송 위험

---

### 5. 빈 파일들

**파일:**
- `pages/disclosure_today.py` (0 lines)
- `pages/news_today.py` (0 lines)

**문제점:**
- 기능 미구현
- 헤더에서 링크되지만 작동하지 않음

---

## 🎯 기술 부채 우선순위 매트릭스

### 우선순위 매트릭스 (Impact vs Effort)

```
High Impact │
           │  ┌─────────────┐
           │  │ 1. 인증구현  │ (Critical)
           │  └─────────────┘
           │         ┌──────────────────┐
           │         │ 2. DB 연동       │
           │         └──────────────────┘
           │  ┌─────────────────────────┐
           │  │ 3. 빈 페이지 구현       │
           │  └─────────────────────────┘
           │                    ┌────────────────┐
           │                    │ 4. 에러핸들링  │
           │                    └────────────────┘
           │                              ┌──────────┐
           │                              │5.리팩토링│
Low Impact │                              └──────────┘
           └──────────────────────────────────────────
             Low Effort              High Effort
```

### 우선순위 테이블

| 순위 | 항목 | Impact | Effort | 복잡도 | 긴급도 |
|------|------|--------|--------|--------|--------|
| 🔴 **P0** | 인증 시스템 구현 | Critical | High | High | Immediate |
| 🟠 **P1** | 데이터베이스 연동 | High | High | Medium | 1주 |
| 🟡 **P2** | 빈 페이지 구현 (공시/뉴스) | High | Medium | Low | 2주 |
| 🟡 **P2** | 에러 핸들링 개선 | Medium | Medium | Low | 2주 |
| 🟢 **P3** | 코드 리팩토링 | Medium | Medium | Medium | 1개월 |
| 🟢 **P3** | CSS 분리 | Low | Low | Low | 2개월 |
| 🟢 **P3** | 로깅 시스템 추가 | Low | Low | Low | 2개월 |

---

## 🚨 Critical Issues (즉시 해결 필요)

### 1. 인증 시스템 부재 ⚠️

**위험도:** Critical
**영향 범위:** 전체 애플리케이션

**현재 상태:**
- 로그인/회원가입 UI만 존재
- 실제 인증 로직 없음
- 세션 관리 없음
- 누구나 접근 가능

**보안 위험:**
- 무단 접근 가능
- 데이터 유출 위험
- CSRF 공격 취약
- SQL Injection 위험 (DB 연동 시)

**해결 방안:** 다음 섹션 "인증 시스템 설계 가이드" 참조

---

### 2. 데이터베이스 연동 부재

**위험도:** High
**영향 범위:** 사용자 관리, 데이터 영속성

**현재 상태:**
- 모든 데이터가 세션에만 저장
- 사용자 정보 저장 불가
- 재시작 시 데이터 손실

**권장사항:**
```python
# PostgreSQL 또는 SQLite 사용
# SQLAlchemy ORM 권장

from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 📝 코드 품질 이슈

### 1. 코드 중복

**위치:**
- `finance.py`와 `pages/listed_stock_retrieval.py`에서 `fdr.StockListing()` 호출 중복
- 여러 파일에서 `render_header()` 호출 패턴 반복

**개선안:**
```python
# utils/data_loader.py
@st.cache_data(ttl=3600)  # 1시간 캐시
def get_krx_listings():
    """KRX 상장 종목 데이터 조회 (캐싱)"""
    return fdr.StockListing('KRX')

# base_page.py
class BasePage:
    def __init__(self):
        st.set_page_config(page_title=self.title, layout="wide")
        render_header()

    @property
    def title(self):
        raise NotImplementedError
```

### 2. 매직 넘버/문자열

**예시:**
```python
df_kospi_display = df_kospi[columns_to_show].rename(columns=columns_mapping)
st.dataframe(df_kospi_display, height=400, width=780, hide_index=True)
                                         # ^^^       ^^^
```

**개선안:**
```python
# config.py
class UIConfig:
    DATAFRAME_HEIGHT = 400
    DATAFRAME_WIDTH = 780
    CACHE_TTL = 3600
    MAX_DISPLAY_ROWS = 20

# 사용
st.dataframe(df, height=UIConfig.DATAFRAME_HEIGHT, width=UIConfig.DATAFRAME_WIDTH)
```

### 3. 타입 힌팅 부재

**현재:**
```python
def color_change(val):
    if val > 0:
        color = 'red'
    # ...
```

**개선:**
```python
def color_change(val: float) -> str:
    """
    값에 따라 색상을 반환합니다.

    Args:
        val: 변동률 값

    Returns:
        CSS 색상 문자열
    """
    if val > 0:
        return 'color: red'
    # ...
```

---

## 🔧 리팩토링 권장사항

### High Priority

#### 1. `pages/listed_stock_retrieval.py` 리팩토링

**Before (123 lines in one block):**
```python
if st.button("조회"):
    # ... 123 lines
```

**After (모듈화):**
```python
# services/stock_service.py
class StockService:
    @staticmethod
    def search_by_name(stock_name: str) -> Optional[pd.DataFrame]:
        """종목명으로 검색"""
        pass

    @staticmethod
    def get_price_history(ticker: str, start_year: str) -> pd.DataFrame:
        """가격 이력 조회"""
        pass

    @staticmethod
    def calculate_52week_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """52주 통계 계산"""
        pass

# pages/listed_stock_retrieval.py
if st.button("조회"):
    stock_service = StockService()
    matched = stock_service.search_by_name(stock_name)

    if matched.empty:
        st.error(f"'{stock_name}' 종목을 찾을 수 없습니다.")
        return

    ticker = matched.iloc[0]['Code']
    df = stock_service.get_price_history(ticker, start_year)

    display_stock_data(df, ticker, stock_name)
    display_charts(df)
    display_statistics(stock_service.calculate_52week_stats(df))
```

#### 2. 환경 설정 관리

**현재 문제:**
- `.env` 파일 상대 경로
- 환경변수 검증 없음

**개선안:**
```python
# config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str = "sqlite:///./krx.db"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    class Config:
        env_file = Path(__file__).parent.parent / '.env'
        case_sensitive = False

settings = Settings()
```

### Medium Priority

#### 1. 로깅 시스템 추가

```python
# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# 사용
logger = setup_logger(__name__)
logger.info("Stock data fetched successfully")
```

#### 2. 단위 테스트 추가

```python
# tests/test_stock_service.py
import pytest
from services.stock_service import StockService

def test_search_by_name():
    service = StockService()
    result = service.search_by_name("삼성전자")

    assert not result.empty
    assert result.iloc[0]['Code'] == '005930'

def test_search_invalid_name():
    service = StockService()
    result = service.search_by_name("존재하지않는종목")

    assert result.empty
```

---

## 📏 코드 메트릭 요약

### 현재 상태
```
✅ 순환복잡도 15+ 함수: 0개
✅ 300+ 라인 파일: 0개
⚠️  100+ 라인 함수: 1개 (listed_stock_retrieval.py:47-170)
⚠️  인증 시스템: 미구현
⚠️  데이터베이스: 미연동
⚠️  테스트 커버리지: 0%
```

### 목표
```
🎯 순환복잡도 < 10
🎯 파일 라인 수 < 200
🎯 함수 라인 수 < 50
🎯 테스트 커버리지 > 80%
🎯 인증 시스템 구현
🎯 DB 연동 완료
```

---

## 🎯 개선 로드맵

### Phase 1: Critical Issues (1-2주)
- [ ] 인증 시스템 구현
- [ ] 데이터베이스 연동
- [ ] 세션 관리 구현
- [ ] 비밀번호 암호화

### Phase 2: Core Features (2-3주)
- [ ] 공시 페이지 구현
- [ ] 뉴스 페이지 구현
- [ ] 에러 핸들링 개선
- [ ] 로깅 시스템 추가

### Phase 3: Code Quality (1개월)
- [ ] `listed_stock_retrieval.py` 리팩토링
- [ ] 코드 중복 제거
- [ ] 타입 힌팅 추가
- [ ] 단위 테스트 작성

### Phase 4: Performance & UX (2개월)
- [ ] 캐싱 전략 구현
- [ ] 페이지네이션 추가
- [ ] CSS 분리
- [ ] 반응형 디자인 개선

---

## 📚 참고 문서

### 추천 도구
- **코드 품질:** `pylint`, `flake8`, `black`
- **복잡도 분석:** `radon`, `mccabe`
- **타입 체킹:** `mypy`
- **테스팅:** `pytest`, `pytest-cov`
- **보안:** `bandit`, `safety`

### 설치 및 실행
```bash
# 개발 의존성 설치
pip install pylint flake8 black radon mypy pytest pytest-cov bandit

# 코드 분석
pylint **/*.py
flake8 .
radon cc . -s -a

# 테스트
pytest --cov=. --cov-report=html
```

---

**다음 문서:** [인증 시스템 설계 가이드](./AUTH_IMPLEMENTATION_GUIDE.md)
