## BE 빠른 실행

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/Past-Life-Card-with-Stat.git
cd Past-Life-Card-with-Stat/backend
```

### 2. uv 설치

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 의존성 설치

```bash
# 가상환경 생성 및 패키지 설치
uv sync

# PyTorch CUDA 버전 설치 (CUDA 12.6 기준)
uv pip install torch==2.7.1+cu126 torchvision==0.22.1+cu126 --index-url https://download.pytorch.org/whl/cu126
```

### 4. 환경 변수 설정

`.env` 파일을 backend 폴더에 생성:

```bash
# .env
HF_TOKEN=hf_your_token_here
```

> **HF_TOKEN 발급**: https://huggingface.co/settings/tokens

### 5. 모델 파일 다운로드

YOLOv8-Pose 모델이 자동으로 다운로드됩니다. 만약 수동으로 다운로드하려면:

```bash
# yolov8n-pose.pt는 첫 실행 시 자동 다운로드됨
# 또는 수동 다운로드: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-pose.pt
```

### 6. 서버 실행

```bash
# 방법 1: 직접 실행
uv run --no-sync python main.py

# 방법 2: uvicorn 사용
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. API 테스트

브라우저에서 접속:
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

또는 curl로 테스트:

```bash
curl -X POST "http://localhost:8000/images/transform" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_photo.jpg"
```

## FE 빠른 실행

### 사전 준비
- Node.js 18+ (LTS 권장)

### 실행 방법
```sh
# 1) 저장소 클론
git clone <YOUR_GIT_URL>

# 2) 프로젝트 폴더로 이동
cd <YOUR_PROJECT_NAME>/frontend

# 3) 의존성 설치
npm install

# 4) 개발 서버 실행
npm run dev
```

브라우저에서 Vite가 출력하는 로컬 주소로 접속하면 됩니다.

## 기술 스택
- Vite
- React + TypeScript
- Tailwind CSS
- shadcn/ui
