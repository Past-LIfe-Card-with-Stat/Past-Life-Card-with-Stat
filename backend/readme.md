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

## 알려진 문제 및 개선 작업 (2026-02-02)

### 1. 이상한 합성 결과 (얼굴 어색함)

**원인:**
- 얼굴 합성이 단순 리사이즈+붙여넣기만 함 (정렬/색상 보정 없음)
- 얼굴 크롭이 margin 1.5로 크게 잘아 배경까지 섞임
- 생성 이미지의 얼굴 좌표가 부정확하면 강제 왜곡됨

**해결 방법 (우선순위):**
- [x] 1단계: 파이프라인 전역 캐싱 (main.py 수정) - 서버 시작 시 한 번만 로드
- [x] 2단계: OpenPose 옵션 축소 (model2.py 수정) - hand_and_face=False로 변경
- [x] 3단계: 추론 해상도/step 감소 (model2.py 수정) - 768→512, 6→4 스텝
- [x] 4단계: 얼굴 정렬 및 색상 보정 추가 (image_blender.py 수정) - 색상 톤 맞춤
- [x] 5단계: 얼굴 크롭 margin 축소 (face_cropper.py 수정) - 1.5→1.2
- [x] 6단계: 얼굴 감지 실패 시 Fallback (medieval_pipeline.py) - 중앙 배치

### 2. 매우 느린 처리 속도

**원인:**
- 요청마다 파이프라인 새로 생성 → SDXL/ControlNet/OpenPose 매번 로드
- 768x768 해상도 + 6 steps (불필요하게 높음)
- OpenPose hand_and_face=True로 처리 비용 증가
- CLIP, YOLO도 모두 풀 실행

**해결 방법 (우선순위):**
- [x] 1단계: 파이프라인 전역 캐싱 (main.py) - ✓ 완료
- [x] 2단계: OpenPose hand_and_face=False 변경 (model2.py) - ✓ 완료
- [x] 3단계: 768 → 512 해상도, 6 → 4 steps 감소 (model2.py) - ✓ 완료

### 3. 스탯 계산 문제

**원인:**
- "full-body portrait" 태그가 흔하게 나와서 CHA가 항상 높음 → LEADERSHIP만 나옴
- 기본값(10)이 너무 낮아서 전사도 STR/VIT이 15~20 수준

**해결 방법:**
- [x] CHA 계산 가중치 낮춤 (20 → 5)
- [x] Leadership 허용 기준 상향 (CHA >= 18 → 25)
- [x] 스탯 기본값 상향 (10 → 15)
- [x] Pose/장비/실루엣 가중치 20% 상향

### 4. 이미지 검증 누락

**원인:**
- Content-type만 체크하고 실제 이미지 유효성은 검증하지 않음
- 사람 없는 이미지, 손상된 이미지, 너무 작거나 큰 이미지 처리 불가

**해결 방법 (api/utils/image_validator.py):**
- [x] 이미지 크기 검증 (최소 256x256, 최대 4096x4096)
- [x] 사람 감지 여부 체크 (YOLO Pose)
- [x] 얼굴 감지 여부 체크 (RetinaFace) - 경고로 처리
- [x] 이미지 손상 체크 (PIL verify)

**예외 처리 시점:**
- **Step 1 (main.py)**: Content-Type 검증
- **Step 2 (main.py)**: 이미지 파일 로드 검증
- **Step 2.5 (main.py)**: 이미지 검증 (크기, 사람 감지, 얼굴 감지)
- **Step 3 (medieval_pipeline.py)**: 원본 얼굴 감지 실패 → 경고
- **Step 4 (medieval_pipeline.py)**: 생성 이미지 얼굴 감지 실패 → Fallback (중앙 배치)

## 진행 상황

### 완료된 개선사항
- ✓ PyTorch/torchvision CUDA 빌드 재설정
- ✓ xformers 제거 (빌드 실패로 인해 옵션)
- ✓ 파이프라인 전역 캐싱 (요청 시마다 모델 로드 방지)
- ✓ OpenPose 최적화 (hand_and_face=False)
- ✓ 생성 해상도/스텝 감소 (768→512, 6→4)
- ✓ 얼굴 색상 보정 추가 (타겟 톤에 맞춤)
- ✓ 얼굴 크롭 margin 축소 (1.5→1.2)
- ✓ 얼굴 감지 실패 시 Fallback 추가
- ✓ CHA 계산 로직 개선 (LEADERSHIP 편향 해결)
- ✓ 스탯 기본값/가중치 상향 (전사 STR/VIT 개선)
- ✓ 이미지 검증 로직 추가 (크기, 사람/얼굴 감지, 손상 체크)

### 다음 개선 예정사항
- [ ] 얼굴 랜드마크 기반 정렬 (회전/변형 보정)
- [ ] CLIP 모델 케싱 (extract_features_pipeline에서)
- [ ] Batch 처리 (여러 요청 동시 처리)

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
