# KRX Stock Market Application 📈

한국 주식 시장 데이터를 제공하는 풀스택 웹 애플리케이션

## 🏗️ 프로젝트 구조

```
secondarymarket/
├── backend/                 # FastAPI 백엔드 API
│   ├── api/                # API 라우터
│   ├── core/               # 핵심 설정
│   ├── models/             # 데이터베이스 모델
│   ├── schemas/            # Pydantic 스키마
│   ├── services/           # 비즈니스 로직
│   └── main.py            # FastAPI 애플리케이션
│
├── frontend/               # Streamlit 프론트엔드
│   ├── pages/             # 멀티페이지 앱
│   ├── components/        # 재사용 컴포넌트
│   ├── utils/             # 유틸리티 함수
│   └── finance.py         # 메인 애플리케이션
│
└── database/              # 데이터베이스 설정
    ├── init/              # 초기화 스크립트
    └── backups/           # 백업 디렉토리
```

## 🚀 빠른 시작

### 필수 요구사항
- Docker & Docker Compose
- Git

### 1. 저장소 클론
```bash
git clone <repository-url>
cd secondarymarket
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 비밀번호 변경
```

### 3. 실행
```bash
docker-compose up -d
```

### 4. 접속
- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5051

## 📦 기술 스택

### Backend
- **FastAPI** - 고성능 Python 웹 프레임워크
- **PostgreSQL (TimescaleDB)** - 시계열 데이터베이스
- **Redis** - 캐싱 및 세션 관리
- **SQLAlchemy** - ORM
- **Python-Jose** - JWT 인증

### Frontend
- **Streamlit** - 인터랙티브 데이터 앱
- **FinanceDataReader** - 한국 주식 데이터
- **Pandas** - 데이터 분석

## 🔧 개발 가이드

### 로컬 개발 환경

#### Backend 개발
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend 개발
```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run finance.py
```

### Docker 명령어

```bash
# 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f [service-name]

# 컨테이너 상태
docker-compose ps

# 중지
docker-compose down

# 볼륨 삭제 (주의: 데이터 삭제됨)
docker-compose down -v
```

## 📚 추가 문서

- [인증 구현 가이드](AUTH_IMPLEMENTATION_GUIDE.md)
- [기술 부채 분석](TECHNICAL_DEBT_ANALYSIS.md)
- [코드 품질 개선 계획](CODE_QUALITY_IMPROVEMENT_PLAN.md)
- [프로젝트 재구조화 대안](PROJECT_RESTRUCTURING_ALTERNATIVES.md)
- [마이그레이션 완료 보고](MIGRATION_COMPLETE.md)

## 🔐 환경 변수

`.env.example` 파일을 참조하여 다음 변수들을 설정하세요:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - 데이터베이스
- `REDIS_PASSWORD` - Redis
- `SECRET_KEY` - JWT 암호화 키
- `PGADMIN_EMAIL`, `PGADMIN_PASSWORD` - PgAdmin

## 🧪 테스트

```bash
# Backend 테스트
cd backend
pytest

# 커버리지 리포트
pytest --cov=. --cov-report=html
```

## 📈 API 엔드포인트

### 인증 (예정)
- `POST /api/auth/signup` - 회원가입
- `POST /api/auth/login` - 로그인
- `POST /api/auth/refresh` - 토큰 갱신
- `POST /api/auth/logout` - 로그아웃

### 주식 데이터 (예정)
- `GET /api/stock/listings` - 상장 종목 목록
- `GET /api/stock/{ticker}` - 종목 상세
- `GET /api/stock/{ticker}/history` - 가격 히스토리

### Health Check
- `GET /` - 기본 상태 확인
- `GET /health` - 상세 헬스 체크

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 👥 팀

프로젝트 기여자 및 유지보수자 정보

## 📞 문의

이슈 발생 시 GitHub Issues를 통해 문의해 주세요.

---

**Last Updated**: 2025-10-15
