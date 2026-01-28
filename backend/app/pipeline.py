"""
전체 파이프라인: 모델1 → 모델2 → 모델3
"""

import time
from typing import Dict

# 각 모델 import
from app.models.model1 import get_feature_extractor  # 팀원이 작성
from app.models.model2 import get_transformer
from app.models.model3 import get_stat_generator  # 팀원이 작성
from PIL import Image


def full_pipeline(input_image: Image.Image) -> Dict:
    """
    전체 파이프라인 실행

    Args:
        input_image: 사용자가 업로드한 전신 사진

    Returns:
        {
            "medieval_image": base64 string,
            "stats": {...},
            "features": {...},
            "processing_time": float
        }
    """
    start_time = time.time()

    # === Step 1: 모델1 - 특징 추출 ===
    print("[Pipeline] Step 1: Extracting features...")
    extractor = get_feature_extractor()
    features_json = extractor.extract(input_image)
    print(f"✓ Features: {features_json}")

    # === Step 2: 모델2 - 중세 이미지 생성 ===
    print("[Pipeline] Step 2: Transforming to medieval style...")
    transformer = get_transformer()
    medieval_result = transformer.generate(
        input_image=input_image,
        description=features_json,  # JSON 또는 문자열
    )
    print("✓ Medieval image generated")

    # === Step 3: 모델3 - 스탯 생성 ===
    print("[Pipeline] Step 3: Generating RPG stats...")
    stat_gen = get_stat_generator()
    stats = stat_gen.calculate_stats(
        features=features_json, medieval_image=medieval_result["image"]
    )
    print(f"✓ Stats: {stats}")

    total_time = time.time() - start_time

    return {
        "medieval_image": medieval_result["image"],  # PIL Image
        "pose_skeleton": medieval_result.get("pose_skeleton"),
        "stats": stats,
        "features": features_json,
        "metadata": {
            "total_processing_time": round(total_time, 2),
            "model1_time": extractor.last_processing_time,
            "model2_time": medieval_result["metadata"]["total_time"],
            "model3_time": stat_gen.last_processing_time,
        },
    }
