"""
로컬 테스트 스크립트: Model 1 → Model 2 전체 흐름
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (import 오류 방지)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
from datetime import datetime

from PIL import Image

# Model 1: 특징 추출
from backend.pipelines.extract_features_pipeline import main as extract_features

# Model 2: 중세 이미지 생성
from backend.pipelines.medieval_pipeline import MedievalPipeline

# 스탯 계산
from backend.pipelines.stat_calculator import calculate_stats


def test_full_pipeline(image_path: str, output_dir: str = "test_outputs"):
    """
    전체 파이프라인 테스트: Model 1 → Model 2 → Stats

    Args:
        image_path: 테스트할 이미지 경로
        output_dir: 결과 저장 디렉토리
    """
    print("=" * 70)
    print("  Model 1 → Model 2 전체 파이프라인 테스트")
    print("=" * 70)

    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # ===== Step 1: 이미지 로드 =====
        print(f"\n[Step 1] Loading image: {image_path}")
        input_image = Image.open(image_path).convert("RGB")
        print(f"✓ Image loaded: {input_image.size}")

        # 원본 이미지 저장
        original_output = output_path / f"{timestamp}_01_original.png"
        input_image.save(original_output)
        print(f"  Saved: {original_output}")

        # ===== Step 2: Model 1 - 특징 추출 =====
        print("\n[Step 2] Model 1: Extracting features...")
        features = extract_features(input_image)

        print("✓ Features extracted:")
        print(f"  - Person detected: {features['quality']['person_detected']}")
        print(f"  - Full body: {features['quality']['has_full_body']}")
        print(f"  - Pose confidence: {features['quality']['pose_conf']:.2f}")
        print(f"  - Top tags: {[t['tag'] for t in features['tags']['top'][:3]]}")

        # Pose metrics 출력
        pose_derived = features["pose"]["derived"]
        print("\n  Pose Metrics:")
        print(f"    - Stance width: {pose_derived.get('stance_width', 0):.2f}")
        print(f"    - Arms open: {pose_derived.get('arms_open', 0):.2f}")
        print(f"    - Body lean: {pose_derived.get('body_lean', 0):.2f}")
        print(f"    - Shoulder tilt: {pose_derived.get('shoulder_tilt', 0):.2f}")

        # JSON 저장
        features_output = output_path / f"{timestamp}_02_features.json"
        with open(features_output, "w", encoding="utf-8") as f:
            json.dump(features, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved: {features_output}")

        # ===== Step 3: Model 2 - 중세 이미지 생성 =====
        print("\n[Step 3] Model 2: Generating medieval character...")

        pipeline = MedievalPipeline()

        # 프롬프트는 고정 또는 features 기반
        prompt = "A person who lives in medieval period"

        print(f"  Prompt: {prompt}")
        print("  Generating... (this may take 10-30 seconds)")

        medieval_image = pipeline.run(input_image, prompt)

        print("✓ Medieval image generated")

        # 결과 이미지 저장
        medieval_output = output_path / f"{timestamp}_03_medieval.png"
        medieval_image.save(medieval_output)
        print(f"  Saved: {medieval_output}")

        # ===== Step 4: 스탯 계산 =====
        print("\n[Step 4] Calculating stats...")
        stats = calculate_stats(features)

        print("✓ Stats calculated:")
        for stat, value in stats.items():
            bar = "█" * (value // 2)  # 막대 그래프
            print(f"  {stat}: {value:2d} {bar}")

        # 스탯 JSON 저장
        stats_output = output_path / f"{timestamp}_04_stats.json"
        with open(stats_output, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved: {stats_output}")

        # ===== 완료 =====
        print("\n" + "=" * 70)
        print("  ✓ 전체 파이프라인 완료!")
        print("=" * 70)
        print("\n저장된 파일들:")
        print(f"  1. 원본 이미지: {original_output}")
        print(f"  2. 특징 JSON: {features_output}")
        print(f"  3. 중세 이미지: {medieval_output}")
        print(f"  4. 스탯 JSON: {stats_output}")
        print(f"\n출력 디렉토리: {output_path.absolute()}")

        return {
            "success": True,
            "features": features,
            "stats": stats,
            "outputs": {
                "original": str(original_output),
                "features_json": str(features_output),
                "medieval_image": str(medieval_output),
                "stats_json": str(stats_output),
            },
        }

    except FileNotFoundError:
        print(f"\n✗ Error: 이미지 파일을 찾을 수 없습니다: {image_path}")
        print("  경로를 확인하고 다시 시도하세요.")
        return {"success": False, "error": "File not found"}

    except Exception as e:
        print(f"\n✗ Error occurred: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


def test_model1_only(image_path: str):
    """Model 1만 단독 테스트 (빠른 확인용)"""
    print("\n" + "=" * 70)
    print("  Model 1 단독 테스트 (특징 추출만)")
    print("=" * 70)

    try:
        print(f"\nLoading image: {image_path}")
        input_image = Image.open(image_path).convert("RGB")

        print("Extracting features...")
        features = extract_features(input_image)

        print("\n✓ Features extracted successfully!")
        print("\nJSON Output:")
        print(json.dumps(features, indent=2, ensure_ascii=False))

        return features

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_model2_only(image_path: str, output_path: str = "test_medieval_only.png"):
    """Model 2만 단독 테스트 (이미지 생성만)"""
    print("\n" + "=" * 70)
    print("  Model 2 단독 테스트 (중세 이미지 생성만)")
    print("=" * 70)

    try:
        print(f"\nLoading image: {image_path}")
        input_image = Image.open(image_path).convert("RGB")

        print("Initializing pipeline...")
        pipeline = MedievalPipeline()

        prompt = "A person who lives in medieval period"
        print(f"Prompt: {prompt}")
        print("Generating... (this may take 10-30 seconds)")

        result_image = pipeline.run(input_image, prompt)

        result_image.save(output_path)
        print(f"\n✓ Image saved to: {output_path}")

        return result_image

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return None


def compare_multiple_images(image_paths: list, output_dir: str = "test_outputs_batch"):
    """여러 이미지를 배치로 테스트"""
    print("\n" + "=" * 70)
    print(f"  배치 테스트: {len(image_paths)}개 이미지")
    print("=" * 70)

    results = []

    for i, image_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] Processing: {image_path}")
        result = test_full_pipeline(image_path, output_dir)
        results.append({"image": image_path, "result": result})

    print("\n" + "=" * 70)
    print("  배치 테스트 완료")
    print("=" * 70)

    # 결과 요약
    success_count = sum(1 for r in results if r["result"].get("success"))
    print(f"\n성공: {success_count}/{len(image_paths)}")

    return results


# ===== 메인 실행 =====
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Model 1 → Model 2 파이프라인 테스트")
    parser.add_argument(
        "image_path",
        nargs="?",
        default="IMG_6386.jpg",
        help="테스트할 이미지 경로 (기본값: test_input.jpg)",
    )
    parser.add_argument(
        "--output-dir",
        default="test_outputs",
        help="결과 저장 디렉토리 (기본값: test_outputs)",
    )
    parser.add_argument(
        "--model1-only", action="store_true", help="Model 1만 실행 (특징 추출만)"
    )
    parser.add_argument(
        "--model2-only", action="store_true", help="Model 2만 실행 (이미지 생성만)"
    )
    parser.add_argument(
        "--batch",
        nargs="+",
        help="여러 이미지를 배치로 처리 (예: --batch img1.jpg img2.jpg img3.jpg)",
    )

    args = parser.parse_args()

    # 배치 모드
    if args.batch:
        compare_multiple_images(args.batch, args.output_dir)

    # Model 1만
    elif args.model1_only:
        test_model1_only(args.image_path)

    # Model 2만
    elif args.model2_only:
        test_model2_only(args.image_path)

    # 전체 파이프라인 (기본)
    else:
        test_full_pipeline(args.image_path, args.output_dir)
