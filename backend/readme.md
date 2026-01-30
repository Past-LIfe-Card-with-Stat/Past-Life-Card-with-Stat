# Medieval Me - Backend

사용자의 전신 사진을 중세 판타지 스타일로 변환하고, RPG 스탯 카드를 생성하는 API 서버입니다.

## 주요 기능

- **이미지 변환**: SDXL-Turbo + ControlNet을 사용하여 중세 판타지 스타일로 변환
- **Face Swap**: 원본 얼굴을 생성된 이미지에 자연스럽게 합성
- **특징 추출**: CLIP + YOLOv8-Pose를 사용한 이미지 분석
- **캐릭터 카드 생성**: LLM 기반 스탯, 직업, flavor text 생성

## 시스템 요구사항

- **Python**: 3.10+
- **GPU**: NVIDIA CUDA GPU (14GB+ VRAM 권장)
- **OS**: Windows / Linux (CUDA 지원)

## 프로젝트 구조

```
backend/
├── main.py                 # FastAPI 서버 진입점
├── pyproject.toml          # 의존성 관리 (uv)
├── .env                    # 환경 변수 (HF_TOKEN)
└── backend/
    ├── pipelines/
    │   ├── medieval_pipeline.py      # 메인 파이프라인
    │   ├── extract_features_pipeline.py  # 특징 추출
    │   ├── infer_identity_flavor.py  # LLM 기반 직업/스탯 추론
    │   └── generate_description.py   # 프롬프트 생성
    └── app/
        ├── models/
        │   ├── model2.py             # SDXL-Turbo + ControlNet
        │   ├── face_detector.py      # RetinaFace 얼굴 감지
        │   ├── face_cropper.py       # 얼굴 크롭
        │   └── image_blender.py      # Face Swap 블렌딩
        └── services/
            ├── character_generator.py # 캐릭터 카드 생성
            ├── stat_calculator.py     # 스탯 계산
            └── input_adapter.py       # 입력 데이터 변환
```

## 설치 방법

### 1. uv 설치 (권장)

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 의존성 설치

```bash
cd backend

# 가상환경 생성 및 의존성 설치
uv sync
```

### 3. PyTorch CUDA 설치

uv로 설치 후 PyTorch CUDA 버전을 별도로 설치해야 합니다:

```bash
# CUDA 12.4 기준
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### 4. 환경 변수 설정

`.env` 파일을 생성하고 Hugging Face 토큰을 설정합니다:

```bash
# .env
HF_TOKEN=hf_your_token_here
```

Hugging Face 토큰은 https://huggingface.co/settings/tokens 에서 발급받을 수 있습니다.

### 5. (선택) xformers 설치

메모리 최적화를 위해 xformers를 설치합니다:

```bash
uv pip install xformers
```

## 실행 방법

### 개발 서버 실행

```bash
cd backend
uv run python main.py
```

또는

```bash
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면:

- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

## API 엔드포인트

### `GET /`

Health check 및 API 정보

### `GET /health`

서버 상태 체크

### `POST /images/transform`

이미지 변환 API

**Request:**

- `file`: 이미지 파일 (JPEG, PNG, WebP)

**Response:**

```json
{
  "status": "success",
  "card_data": {
    "identity": {
      "job_title": "기사",
      "role": "전장의 수호자"
    },
    "stats": {
      "STR": { "value": 25, "max": 50 },
      "AGI": { "value": 18, "max": 50 },
      "INT": { "value": 15, "max": 50 },
      "CHA": { "value": 22, "max": 50 },
      "LUK": { "value": 12, "max": 50 },
      "VIT": { "value": 28, "max": 50 }
    },
    "flavor_text": "전장의 함성 속에서도 흔들리지 않는 강철 의지의 소유자."
  },
  "medieval_image": "base64_encoded_image",
  "output_path": "uploads/result_filename.png",
  "metadata": {
    "original_filename": "photo.jpg",
    "image_size": "1024x768",
    "output_size": "768x768"
  }
}
```

## 파이프라인 흐름

```
[Input Image]
     │
     ▼
[Step 1] 특징 추출 (CLIP + YOLOv8-Pose)
     │
     ▼
[Step 2] 원본 얼굴 감지 & 추출 (RetinaFace)
     │
     ▼
[Step 3] 중세 이미지 생성 (SDXL-Turbo + ControlNet)
     │
     ▼
[Step 4] Face Swap (원본 얼굴 → 생성 이미지)
     │
     ▼
[Step 5] 생성 이미지 특징 추출
     │
     ▼
[Step 6] 스탯 & 캐릭터 카드 생성 (Qwen + Llama)
     │
     ▼
[Output: 변환 이미지 + 캐릭터 카드]
```

## 사용 모델

| 용도           | 모델                                   |
| -------------- | -------------------------------------- |
| 이미지 생성    | `stabilityai/sdxl-turbo`               |
| 포즈 제어      | `thibaud/controlnet-openpose-sdxl-1.0` |
| 태그 추출      | `openai/clip-vit-base-patch32`         |
| 포즈 추출      | `YOLOv8n-pose`                         |
| 얼굴 감지      | `RetinaFace`                           |
| 직업/역할 추론 | `Qwen/Qwen2.5-7B-Instruct`             |
| Flavor Text    | `meta-llama/Llama-3.1-8B-Instruct`     |

## 트러블슈팅

### CUDA Out of Memory

- `model2.py`에서 `height`, `width`를 줄여보세요 (768 → 512)
- xformers가 설치되어 있는지 확인하세요

### HuggingFace 모델 다운로드 실패

- `.env`에 `HF_TOKEN`이 올바르게 설정되어 있는지 확인
- 네트워크 연결 상태 확인

### ReadTimeout 오류

- `infer_identity_flavor.py`의 `timeout` 값을 늘려보세요
- HuggingFace 서버 상태 확인

## 라이선스

MIT License
