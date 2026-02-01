import base64
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from api.pipelines import medieval_pipeline
from api.utils.image_validator import get_validator

load_dotenv()

app = FastAPI(
    title="Medieval Character Transformer API",
    description="중세 캐릭터 변환 및 특징 추출 서비스",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {"image/jpeg", "image/png", "image/webp"}

# 전역 파이프라인 캐싱
_pipeline = None

def get_pipeline():
    """파이프라인 싱글톤 (서버 시작 시 한 번만 로드)"""
    global _pipeline
    if _pipeline is None:
        _pipeline = medieval_pipeline.MedievalPipeline()
    return _pipeline

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 파이프라인 초기화"""
    print("\n" + "=" * 60)
    print("  Initializing Medieval Pipeline...")
    print("=" * 60)
    get_pipeline()
    get_validator()  # 검증기도 초기화
    print("  ✓ Pipeline ready!\n")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 리소스 정리"""
    global _pipeline
    if _pipeline is not None:
        print("\n  Shutting down pipeline...")
        _pipeline = None


@app.get("/")
async def root():
    """Health check 및 API 정보"""
    return {
        "status": "ok",
        "service": "Medieval Character Transformer",
        "version": "1.0.0",
        "endpoints": {"health": "/health", "transform": "/images/transform"},
    }


@app.get("/health")
async def health_check():
    """서버 상태 체크"""
    return {"status": "healthy", "service": "running"}


@app.post("/images/transform")
async def transform_image(file: UploadFile = File(...)):
    """
    중세 캐릭터 변환 API

    Args:
        file: 업로드된 이미지 파일 (JPEG, PNG, WebP)

    Returns:
        {
            "status": "success",
            "card_data": {...},
            "medieval_image": "base64_string",
            "output_path": "uploads/result_xxx.png"
        }
    """
    # 1. Content-Type 검증
    if file.content_type not in ALLOWED:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED}",
        )

    # 2. 이미지 로드
    image_bytes = await file.read()

    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    print(f"\n[Request] File: {file.filename}, Size: {image.size}")

    # 2.5. 이미지 검증 (사람 감지, 얼굴 감지, 크기 체크)
    validator = get_validator()
    validation_result = validator.validate(image)

    if not validation_result["valid"]:
        error_msg = " | ".join(validation_result["errors"])
        raise HTTPException(
            status_code=400,
            detail=f"이미지 검증 실패: {error_msg}"
        )

    # 경고가 있으면 로그 출력
    if validation_result["warnings"]:
        for warning in validation_result["warnings"]:
            print(f"  ⚠ {warning}")

    print(f"  ✓ Validation passed: {validation_result['metadata']}")

    # 3. 파이프라인 실행 (특징 추출 + 이미지 생성 + 캐릭터 카드)
    try:
        pipeline = get_pipeline()  # 캐시된 파이프라인 사용
        result = pipeline.run(image)

        result_image = result["generated_image"]
        card_data = result["card_data"]

        # 결과 저장
        output_filename = f"result_{Path(file.filename).stem}.png"
        output_path = UPLOAD_DIR / output_filename
        result_image.save(output_path)

        print(f"✓ Medieval image saved: {output_path}")

    except Exception as e:
        print(f"✗ Pipeline error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Image transformation failed: {str(e)}"
        )

    # 4. 이미지를 Base64로 인코딩 (클라이언트 전송용)
    buffered = BytesIO()
    result_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 5. 응답 반환
    return JSONResponse(
        {
            "status": "success",
            "card_data": card_data.model_dump(),
            "medieval_image": img_base64,
            "output_path": str(output_path),
            "metadata": {
                "original_filename": file.filename,
                "image_size": f"{image.size[0]}x{image.size[1]}",
                "output_size": f"{result_image.size[0]}x{result_image.size[1]}",
            },
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(_request, exc):
    """전역 에러 핸들러"""
    print(f"✗ Unhandled error: {exc}")
    import traceback

    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc), "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("  Medieval Character Transformer API Server")
    print("=" * 60)
    print("  Server starting at http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드 (프로덕션에서는 False)
        log_level="info",
    )
