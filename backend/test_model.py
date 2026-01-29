from app.models.model2 import MedievalCharacterTransformer
from PIL import Image


def test_transformation():
    """모델 테스트 - 모델1 JSON 형식"""

    # 모델 로드
    transformer = MedievalCharacterTransformer()

    # 테스트 이미지
    input_image = Image.open("backend\IMG_6386.jpg")

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

    # 변환 실행 (얼굴 보존 강도 조정 가능)
    result = transformer.generate(
        input_image=input_image,
        description=model1_output,
        face_preservation_strength=0.85,  # 0.7-0.95 범위에서 조정
    )

    # 결과 저장
    result["image"].save("output_medieval.png")
    result["pose_skeleton"].save("output_pose.png")

    print("\n✓ 테스트 완료!")
    print(f"  - 파싱된 설명: {result['parsed_description']}")
    print(f"  - 생성 시간: {result['metadata']['total_time']}초")
    print(f"  - 얼굴 보존 강도: {result['metadata']['face_preservation_strength']}")
    print("  - 결과 저장: output_medieval.png")


def test_multiple_face_preservation():
    """다양한 얼굴 보존 강도 테스트"""

    transformer = MedievalCharacterTransformer()
    input_image = Image.open("test_input.jpg")

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
        "tags": {"top": [{"tag": "full-body portrait", "score": 0.82}]},
    }

    print("\n=== 얼굴 보존 강도별 테스트 ===\n")

    strengths = [0.70, 0.80, 0.90]

    for strength in strengths:
        print(f"\n[강도 {strength}] 생성 중...")
        result = transformer.generate(
            input_image=input_image,
            description=model1_output,
            face_preservation_strength=strength,
        )

        output_path = f"output_face_{int(strength * 100)}.png"
        result["image"].save(output_path)
        print(f"✓ 저장: {output_path}")


if __name__ == "__main__":
    test_transformation()

    # 얼굴 보존 강도 비교 테스트 (선택)
    # test_multiple_face_preservation()
