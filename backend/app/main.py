import base64
import io
import time

# 파이프라인 import
from app.pipeline import full_pipeline
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

app = FastAPI(
    title="Past Life Card with Stats API",
    description="중세 캐릭터 변환 및 스탯 생성 서비스",
    version="1.0.0",
)

# CORS 설정 (프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    print("=" * 50)
    print("  Past Life Card API Server Starting...")
    print("=" * 50)
    # 모델 초기화는 각 싱글톤에서 처리
    print("✓ Server ready!")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Past Life Card with Stats API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "full_pipeline": "/api/v1/transform-full",
            "model2_only": "/api/v1/transform",
        },
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/api/v1/transform-full")
async def transform_full_pipeline(image: UploadFile = File(...)):
    """
    전체 파이프라인: 이미지 → 중세 캐릭터 + 스탯

    Request:
        - image: 전신 사진 (multipart/form-data)

    Response:
        {
            "status": "success",
            "medieval_image": "base64...",
            "stats": {...},
            "features": {...},
            "metadata": {...}
        }
    """
    try:
        start_time = time.time()

        # 이미지 로드
        print(f"\n[Request] File: {image.filename}")
        image_bytes = await image.read()
        input_image = Image.open(io.BytesIO(image_bytes))
        print(f"✓ Image loaded: {input_image.size}")

        # 전체 파이프라인 실행
        result = full_pipeline(input_image)

        # PIL Image → Base64
        buffered = io.BytesIO()
        result["medieval_image"].save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # 포즈 스켈레톤도 변환 (있다면)
        pose_base64 = None
        if result.get("pose_skeleton"):
            pose_buffered = io.BytesIO()
            result["pose_skeleton"].save(pose_buffered, format="PNG")
            pose_base64 = base64.b64encode(pose_buffered.getvalue()).decode()

        total_time = time.time() - start_time

        print(f"✓ Pipeline completed in {total_time:.2f}s\n")

        return JSONResponse(
            {
                "status": "success",
                "medieval_image": img_base64,
                "pose_skeleton": pose_base64,
                "stats": result["stats"],
                "features": result["features"],
                "metadata": {
                    **result["metadata"],
                    "api_processing_time": round(total_time, 2),
                },
            }
        )

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail={"error": str(e), "type": type(e).__name__}
        )


@app.post("/api/v1/transform")
async def transform_model2_only(
    image: UploadFile = File(...), description: str = Form(...)
):
    """
    모델2만 단독 실행 (테스트/개발용)
    """
    import json

    from app.models.model2 import get_transformer

    try:
        image_bytes = await image.read()
        input_image = Image.open(io.BytesIO(image_bytes))

        # description이 JSON 문자열이면 파싱
        try:
            desc_data = json.loads(description)
        except:
            desc_data = description

        transformer = get_transformer()
        result = transformer.generate(input_image, desc_data)

        # Base64 변환
        buffered = io.BytesIO()
        result["image"].save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        return {
            "status": "success",
            "generated_image": img_base64,
            "metadata": result["metadata"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,  # 개발 시에만
    )
