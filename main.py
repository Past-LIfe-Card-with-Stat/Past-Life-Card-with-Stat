import base64
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from backend.app.models.model2 import MedievalCharacterTransformer
from backend.pipelines import extract_features_pipeline

load_dotenv()

app = FastAPI(
    title="Medieval Character Transformer API",
    description="중세 캐릭터 변환 및 특징 추출 서비스",
    version="1.0.0",
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {"image/jpeg", "image/png", "image/webp"}

# ⭐ 모델2 싱글톤 (앱 시작 시 한 번만 로드)
print("Loading Model 2 (MedievalCharacterTransformer)...")
transformer = MedievalCharacterTransformer()
print("✓ Model 2 loaded successfully")


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
            "features": {...},
            "medieval_image": "base64_string",
            "output_path": "uploads/result_xxx.png",
            "metadata": {...}
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

    # 3. 특징 추출 (모델1)
    try:
        features = extract_features_pipeline.main(image=image)
        print("✓ Features extracted")
        print(f"  - Person detected: {features['quality']['person_detected']}")
        print(f"  - Full body: {features['quality']['has_full_body']}")
        print(f"  - Pose conf: {features['quality']['pose_conf']:.2f}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Feature extraction failed: {str(e)}"
        )

    # 4. 중세 캐릭터 변환 (모델2) ⭐ 수정된 부분
    try:
        # Model 2: Model 1의 features(JSON)를 그대로 description으로 전달
        result = transformer.generate(
            input_image=image,
            description=features,  # ⭐ features를 그대로 전달
            pose_strength=0.5,  # 로컬 테스트와 동일
        )

        result_image = result["image"]

        # 결과 저장
        output_filename = f"result_{Path(file.filename).stem}.png"
        output_path = UPLOAD_DIR / output_filename
        result_image.save(output_path)

        print(f"✓ Medieval image saved: {output_path}")
        print(f"  - Detected occupation: {result['detected_occupation']}")
        print(f"  - Generation time: {result['metadata']['total_time']:.1f}s")

    except Exception as e:
        print(f"✗ Pipeline error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Image transformation failed: {str(e)}"
        )

    # 5. 이미지를 Base64로 인코딩 (클라이언트 전송용)
    buffered = BytesIO()
    result_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 6. 응답 반환 (Model2 메타데이터 포함)
    return JSONResponse(
        {
            "status": "success",
            "features": features,
            "medieval_image": img_base64,  # Base64 인코딩된 이미지
            "output_path": str(output_path),
            "metadata": {
                "original_filename": file.filename,
                "image_size": f"{image.size[0]}x{image.size[1]}",
                "output_size": f"{result_image.size[0]}x{result_image.size[1]}",
                "model2": {
                    "detected_occupation": result["detected_occupation"],
                    "parsed_description": result["parsed_description"],
                    "prompt_used": result["metadata"]["prompt_used"],
                    "generation_time": result["metadata"]["total_time"],
                    "pose_strength": result["metadata"]["pose_strength"],
                },
            },
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
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
