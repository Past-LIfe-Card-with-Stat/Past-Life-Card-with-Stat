# test_model2.py (수정 버전)
from app.models.model2 import MedievalCharacterTransformer
from PIL import Image


def test_transformation():
    """모델 테스트 - 모델1 JSON 형식 (수정된 버전)"""

    # 모델 로드
    transformer = MedievalCharacterTransformer()

    # 테스트 이미지
    input_image = Image.open(r"backend\IMG_6386.jpg")  # raw string으로 경로 처리

    # 모델1 출력 시뮬레이션 (실제 형식)
    model1_output = {
        "quality": {"person_detected": True, "has_full_body": True, "pose_conf": 0.83},
        "pose": {
            "derived": {
                "shoulder_tilt": 0.07,
                "body_lean": 0.05,
                "stance_width": 1.12,
                "arms_open": 0.34,
            }
        },
        "tags": {
            "top": [
                {"tag": "full-body portrait", "score": 0.82},
                {"tag": "standing", "score": 0.78},
                {"tag": "casual wear", "score": 0.65},
            ]
        },
    }

    print("=== 모델1 JSON 입력 테스트 ===\n")

    # 변환 실행 (파라미터명 변경: face_preservation_strength → pose_strength)
    result = transformer.generate(
        input_image=input_image,
        description=model1_output,
        pose_strength=0.5,  # ⭐ 변경됨: 0.3(창의적) ~ 0.7(정확한 자세)
    )

    # 결과 저장
    result["image"].save("output_medieval.png")
    result["pose_skeleton"].save("output_pose.png")

    print("\n✓ 테스트 완료!")
    print(f"  - 파싱된 설명: {result['parsed_description']}")
    print(f"  - 감지된 직업: {result['detected_occupation']}")  # ⭐ 새로 추가
    print(f"  - 생성 시간: {result['metadata']['total_time']}초")
    print(f"  - Pose 강도: {result['metadata']['pose_strength']}")
    print("  - 결과 저장: output_medieval.png, output_pose.png")


def test_different_occupations():
    """다양한 직업 태그 테스트"""

    transformer = MedievalCharacterTransformer()
    input_image = Image.open(r"backend\IMG_6386.jpg")

    # 직업별 테스트 케이스
    test_cases = [
        {
            "name": "Knight (전사)",
            "tags": [
                {"tag": "strong warrior", "score": 0.9},
                {"tag": "fighter", "score": 0.85},
                {"tag": "confident", "score": 0.8},
            ],
        },
        {
            "name": "Mage (마법사)",
            "tags": [
                {"tag": "wise intelligent", "score": 0.9},
                {"tag": "magic", "score": 0.85},
                {"tag": "mysterious", "score": 0.8},
            ],
        },
        {
            "name": "Merchant (상인)",
            "tags": [
                {"tag": "merchant trader", "score": 0.9},
                {"tag": "friendly", "score": 0.85},
                {"tag": "wealthy", "score": 0.8},
            ],
        },
        {
            "name": "Peasant (농민)",
            "tags": [
                {"tag": "worker farmer", "score": 0.9},
                {"tag": "hardworking", "score": 0.85},
                {"tag": "simple", "score": 0.8},
            ],
        },
    ]

    print("\n=== 직업별 생성 테스트 ===\n")

    for case in test_cases:
        print(f"\n[{case['name']}] 생성 중...")

        model1_output = {
            "quality": {
                "person_detected": True,
                "has_full_body": True,
                "pose_conf": 0.83,
            },
            "pose": {
                "derived": {
                    "shoulder_tilt": 0.07,
                    "body_lean": 0.05,
                    "stance_width": 1.12,
                    "arms_open": 0.34,
                }
            },
            "tags": {"top": case["tags"]},
        }

        result = transformer.generate(
            input_image=input_image,
            description=model1_output,
            pose_strength=0.5,
        )

        output_path = f"output_{case['name'].split()[0].lower()}.png"
        result["image"].save(output_path)
        print(f"✓ 저장: {output_path}")
        print(f"  감지된 직업: {result['detected_occupation']}")
        print(f"  사용된 프롬프트: {result['metadata']['prompt_used'][:80]}...")


def test_pose_strength_comparison():
    """Pose 강도별 비교 테스트"""

    transformer = MedievalCharacterTransformer()
    input_image = Image.open(r"backend\IMG_6386.jpg")

    model1_output = {
        "quality": {"person_detected": True, "has_full_body": True, "pose_conf": 0.83},
        "pose": {
            "derived": {
                "shoulder_tilt": 0.07,
                "body_lean": 0.05,
                "stance_width": 1.12,
                "arms_open": 0.34,
            }
        },
        "tags": {
            "top": [
                {"tag": "strong warrior", "score": 0.9},
                {"tag": "confident", "score": 0.85},
            ]
        },
    }

    print("\n=== Pose 강도별 테스트 ===\n")
    print("(낮음: 창의적/자유로운 자세, 높음: 원본 자세 정확히 따라감)\n")

    strengths = [0.3, 0.5, 0.7]

    for strength in strengths:
        print(f"\n[강도 {strength}] 생성 중...")
        result = transformer.generate(
            input_image=input_image,
            description=model1_output,
            pose_strength=strength,
        )

        output_path = f"output_pose_{int(strength * 100)}.png"
        result["image"].save(output_path)
        print(f"✓ 저장: {output_path}")


def test_single_vs_multiple_people():
    """단일 인물 필터링 테스트 (여러 사람이 있는 이미지)"""

    transformer = MedievalCharacterTransformer()

    # 여러 사람이 있는 이미지로 테스트 (있다면)
    # input_image = Image.open("test_multiple_people.jpg")

    # 또는 단일 인물 이미지로 필터링 로직 확인
    input_image = Image.open(r"backend\IMG_6386.jpg")

    model1_output = {
        "quality": {"person_detected": True, "has_full_body": True, "pose_conf": 0.83},
        "pose": {
            "derived": {
                "shoulder_tilt": 0.07,
                "body_lean": 0.05,
                "stance_width": 1.12,
                "arms_open": 0.34,
            }
        },
        "tags": {"top": [{"tag": "person standing", "score": 0.9}]},
    }

    print("\n=== 단일 인물 필터링 테스트 ===")
    print("(OpenPose가 여러 사람을 감지하면 가장 큰 사람만 선택)\n")

    result = transformer.generate(
        input_image=input_image, description=model1_output, pose_strength=0.5
    )

    result["image"].save("output_single_person.png")
    result["pose_skeleton"].save("output_pose_filtered.png")

    print("\n✓ 테스트 완료!")
    print("  - pose skeleton을 확인하여 1명만 남았는지 확인하세요")


def test_text_description_only():
    """텍스트 description만으로 테스트 (JSON 없이)"""

    transformer = MedievalCharacterTransformer()
    input_image = Image.open(r"backend\IMG_6386.jpg")

    print("\n=== 텍스트 description 테스트 ===\n")

    # 단순 텍스트로 전달
    text_description = "powerful warrior, confident stance, strong build"

    result = transformer.generate(
        input_image=input_image, description=text_description, pose_strength=0.5
    )

    result["image"].save("output_text_only.png")

    print("\n✓ 테스트 완료!")
    print(f"  - 파싱된 설명: {result['parsed_description']}")
    print(f"  - 감지된 직업: {result['detected_occupation']}")


if __name__ == "__main__":
    # 1. 기본 테스트
    print("\n" + "=" * 60)
    print("1. 기본 변환 테스트")
    print("=" * 60)
    test_transformation()

    # 2. 직업별 테스트 (선택)
    print("\n" + "=" * 60)
    print("2. 직업별 생성 테스트")
    print("=" * 60)
    test_different_occupations()

    # 3. Pose 강도 비교 (선택)
    print("\n" + "=" * 60)
    print("3. Pose 강도별 비교")
    print("=" * 60)
    test_pose_strength_comparison()

    # 4. 단일 인물 필터링 테스트 (선택)
    # print("\n" + "=" * 60)
    # print("4. 단일 인물 필터링 테스트")
    # print("=" * 60)
    # test_single_vs_multiple_people()

    # 5. 텍스트 전용 테스트 (선택)
    # print("\n" + "=" * 60)
    # print("5. 텍스트 description 테스트")
    # print("=" * 60)
    # test_text_description_only()

    print("\n" + "=" * 60)
    print("모든 테스트 완료!")
    print("=" * 60)
