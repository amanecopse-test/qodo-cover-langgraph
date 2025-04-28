# Qodo Cover LangGraph

LangGraph를 활용한 테스트 커버리지 개선 도구 프로젝트입니다.

## 1. 설치 및 설정

### 1.1. uv 설치
먼저 [uv](https://github.com/astral-sh/uv)를 설치해야 합니다.

### 1.2. 가상환경 설정

```bash
# Python 3.12 기반 가상환경 생성
uv venv --python 3.12

# 가상환경 활성화
source .venv/bin/activate  # Linux/macOS
# 또는
.venv\Scripts\activate  # Windows
```

### 1.3. 의존성 관리

#### 1.3.1. 기존 의존성 설치
```bash
# 모든 의존성 설치 (개발 의존성 포함)
uv sync

# 또는 개발 의존성 제외하고 설치
uv sync --no-dev
```

#### 1.3.2. 새로운 의존성 추가
```bash
# 일반 의존성 추가
uv add <패키지명>

# 개발 전용 의존성 추가
uv add --dev <패키지명>
```

## 2. 프로젝트 구조

- `src/`: 소스 코드 디렉토리
- `tests/`: 테스트 코드 디렉토리
- `pyproject.toml`: 프로젝트 설정 및 의존성 정보
- `uv.lock`: 의존성 버전 잠금 파일 