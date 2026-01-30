"""
통합 테스트 스크립트: Model 1 → Model 2 전체 파이프라인
단일 이미지 테스트용
"""

# # 프로젝트 루트에서 실행
# python backend/tests/test_model.py test_images/photo1.jpg

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (import 오류 방지)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
from datetime import datetime

from PIL import Image

# Model 2: 중세 이미지 생성
from backend.app.models.model2 import MedievalCharacterTransformer

# Model 1: 특징 추출
from backend.pipelines.extract_features_pipeline import main as extract_features

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
    print("  전체 파이프라인 테스트: Model 1 → Model 2 → Stats")
    print("=" * 70)

    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = Path(image_path).stem

    try:
        # ===== Step 1: 이미지 로드 =====
        print(f"\n[Step 1/5] Loading image: {image_path}")
        input_image = Image.open(image_path).convert("RGB")
        print(f"✓ Image loaded: {input_image.size}")

        # 원본 이미지 저장
        original_output = output_path / f"{timestamp}_{test_name}_01_original.png"
        input_image.save(original_output)
        print(f"  Saved: {original_output.name}")

        # ===== Step 2: Model 1 - 특징 추출 =====
        print("\n[Step 2/5] Model 1: Extracting features...")
        features = extract_features(input_image)

        quality = features["quality"]
        pose_derived = features["pose"]["derived"]
        tags = features["tags"]["top"]

        print("✓ Features extracted:")
        print(f"  - Person detected: {quality['person_detected']}")
        print(f"  - Full body: {quality['has_full_body']}")
        print(f"  - Pose confidence: {quality['pose_conf']:.2f}")
        print(f"  - Top 5 tags: {[t['tag'] for t in tags[:5]]}")

        print("\n  Pose Metrics:")
        print(f"    - Stance width: {pose_derived.get('stance_width', 0):.2f}")
        print(f"    - Arms open: {pose_derived.get('arms_open', 0):.2f}")
        print(f"    - Body lean: {pose_derived.get('body_lean', 0):.2f}")
        print(f"    - Shoulder tilt: {pose_derived.get('shoulder_tilt', 0):.2f}")

        # Features JSON 저장
        features_output = output_path / f"{timestamp}_{test_name}_02_features.json"
        with open(features_output, "w", encoding="utf-8") as f:
            json.dump(features, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved: {features_output.name}")

        # ===== Step 3: 스탯 계산 =====
        print("\n[Step 3/5] Calculating stats...")
        stats = calculate_stats(features)

        print("✓ Stats calculated:")
        for stat, value in stats.items():
            bar = "█" * (value // 2)  # 막대 그래프
            print(f"  {stat}: {value:2d} {bar}")

        # Stats JSON 저장
        stats_output = output_path / f"{timestamp}_{test_name}_03_stats.json"
        with open(stats_output, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved: {stats_output.name}")

        # ===== Step 4: Model 2 - 중세 이미지 생성 =====
        print("\n[Step 4/5] Model 2: Generating medieval character...")

        # MedievalCharacterTransformer 사용
        transformer = MedievalCharacterTransformer()

        # Model 1 출력을 description으로 전달
        model1_output = {
            "quality": quality,
            "pose": features["pose"],
            "tags": features["tags"],
        }

        print("  Generating... (this may take 30-60 seconds)")

        result = transformer.generate(
            input_image=input_image,
            description=model1_output,
            pose_strength=0.5,  # 기본값
        )

        print(f"✓ Medieval image generated in {result['metadata']['total_time']:.1f}s")
        print(f"  - Detected occupation: {result['detected_occupation']}")
        print(f"  - Parsed description: {result['parsed_description']}")
        print("\n  Prompt used:")
        print(f"    {result['metadata']['prompt_used']}")

        # 결과 이미지 저장
        medieval_output = output_path / f"{timestamp}_{test_name}_04_medieval.png"
        result["image"].save(medieval_output)
        print(f"\n  Saved: {medieval_output.name}")

        # Pose skeleton 저장
        pose_output = output_path / f"{timestamp}_{test_name}_05_pose_skeleton.png"
        result["pose_skeleton"].save(pose_output)
        print(f"  Saved: {pose_output.name}")

        # ===== Step 5: 결과 요약 저장 =====
        print("\n[Step 5/5] Saving summary...")

        summary = {
            "test_name": test_name,
            "image_path": image_path,
            "timestamp": timestamp,
            "model1_results": {
                "person_detected": quality["person_detected"],
                "full_body": quality["has_full_body"],
                "pose_confidence": quality["pose_conf"],
                "top_tags": [t["tag"] for t in tags[:5]],
                "pose_metrics": pose_derived,
            },
            "stats": stats,
            "model2_results": {
                "detected_occupation": result["detected_occupation"],
                "parsed_description": result["parsed_description"],
                "generation_time": result["metadata"]["total_time"],
                "prompt_used": result["metadata"]["prompt_used"],
                "pose_strength": result["metadata"]["pose_strength"],
            },
            "output_files": {
                "original": str(original_output.name),
                "features_json": str(features_output.name),
                "stats_json": str(stats_output.name),
                "medieval_image": str(medieval_output.name),
                "pose_skeleton": str(pose_output.name),
            },
        }

        summary_output = output_path / f"{timestamp}_{test_name}_06_summary.json"
        with open(summary_output, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"✓ Summary saved: {summary_output.name}")

        # ===== 완료 =====
        print("\n" + "=" * 70)
        print("  ✓ 전체 파이프라인 완료!")
        print("=" * 70)
        print("\n저장된 파일들 (총 6개):")
        print(f"  1. 원본 이미지: {original_output.name}")
        print(f"  2. 특징 JSON: {features_output.name}")
        print(f"  3. 스탯 JSON: {stats_output.name}")
        print(f"  4. 중세 이미지: {medieval_output.name}")
        print(f"  5. Pose skeleton: {pose_output.name}")
        print(f"  6. 요약 JSON: {summary_output.name}")
        print(f"\n출력 디렉토리: {output_path.absolute()}")

        return {"success": True, "summary": summary}

    except FileNotFoundError:
        print(f"\n✗ Error: 이미지 파일을 찾을 수 없습니다: {image_path}")
        print("  경로를 확인하고 다시 시도하세요.")
        print(f"  현재 작업 디렉토리: {Path.cwd()}")
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
        print(f"\n[1/2] Loading image: {image_path}")
        input_image = Image.open(image_path).convert("RGB")
        print(f"✓ Image loaded: {input_image.size}")

        print("\n[2/2] Extracting features...")
        features = extract_features(input_image)

        print("\n✓ Features extracted successfully!")

        # 주요 정보만 출력
        quality = features["quality"]
        tags = features["tags"]["top"]

        print("\nQuality:")
        print(f"  - Person detected: {quality['person_detected']}")
        print(f"  - Full body: {quality['has_full_body']}")
        print(f"  - Pose confidence: {quality['pose_conf']:.2f}")

        print("\nTop Tags:")
        for i, tag in enumerate(tags[:5], 1):
            print(f"  {i}. {tag['tag']} (score: {tag['score']:.2f})")

        print("\nPose Metrics:")
        pose_derived = features["pose"]["derived"]
        for key, value in pose_derived.items():
            print(f"  - {key}: {value:.2f}")

        return features

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_model2_only(
    image_path: str, output_path: str = "test_medieval_only.png", occupation: str = None
):
    """Model 2만 단독 테스트 (이미지 생성만)"""
    print("\n" + "=" * 70)
    print("  Model 2 단독 테스트 (중세 이미지 생성만)")
    print("=" * 70)

    try:
        print(f"\n[1/3] Loading image: {image_path}")
        input_image = Image.open(image_path).convert("RGB")
        print(f"✓ Image loaded: {input_image.size}")

        print("\n[2/3] Initializing Model 2...")
        transformer = MedievalCharacterTransformer()

        # 간단한 description (실제로는 Model 1 필요)
        if occupation:
            description = {
                "quality": {
                    "person_detected": True,
                    "has_full_body": True,
                    "pose_conf": 0.8,
                },
                "pose": {"derived": {}},
                "tags": {"top": [{"tag": occupation, "score": 0.9}]},
            }
        else:
            description = "medieval character"

        print("\n[3/3] Generating... (this may take 30-60 seconds)")

        result = transformer.generate(
            input_image=input_image,
            description=description,
            pose_strength=0.5,
        )

        result["image"].save(output_path)
        print(f"\n✓ Image saved to: {output_path}")
        print(f"  Generation time: {result['metadata']['total_time']:.1f}s")
        print(f"  Detected occupation: {result['detected_occupation']}")

        return result

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return None


# ===== 메인 실행 =====
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Model 1 → Model 2 파이프라인 테스트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 기본 (전체 파이프라인)
  python backend/tests/test_model.py test_images/photo1.jpg
  
  # Model 1만 (빠른 확인)
  python backend/tests/test_model.py test_images/photo1.jpg --model1-only
  
  # Model 2만
  python backend/tests/test_model.py test_images/photo1.jpg --model2-only
  
  # 출력 디렉토리 지정
  python backend/tests/test_model.py test_images/photo1.jpg --output-dir my_results
        """,
    )

    parser.add_argument(
        "image_path",
        nargs="?",
        default="test_images/sample.jpg",
        help="테스트할 이미지 경로 (기본값: test_images/sample.jpg)",
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
        "--occupation", help="Model 2 전용: 직업 지정 (예: warrior, mage, merchant)"
    )

    args = parser.parse_args()

    # 이미지 경로 확인
    image_file = Path(args.image_path)
    if not image_file.exists():
        print(f"\n✗ Error: 이미지 파일이 존재하지 않습니다: {args.image_path}")
        print(f"  현재 작업 디렉토리: {Path.cwd()}")
        print("\n이미지 저장 위치:")
        print("  프로젝트 루트에 'test_images' 폴더를 만들고")
        print("  테스트할 이미지를 그 안에 넣으세요.")
        print("\n예시:")
        print("  Past-Life-Card-with-Stat/")
        print("  ├── test_images/")
        print("  │   ├── photo1.jpg")
        print("  │   ├── photo2.jpg")
        print("  │   └── photo3.jpg")
        print("  └── backend/")
        sys.exit(1)

    # Model 1만
    if args.model1_only:
        test_model1_only(args.image_path)

    # Model 2만
    elif args.model2_only:
        test_model2_only(args.image_path, occupation=args.occupation)

    # 전체 파이프라인 (기본)
    else:
        test_full_pipeline(args.image_path, args.output_dir)
