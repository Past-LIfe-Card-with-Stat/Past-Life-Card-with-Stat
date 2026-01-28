# backend/test_model.py
from app.models.model2 import MedievalCharacterTransformer
from PIL import Image


def test_transformation():
    """모델 테스트"""

    # 모델 로드
    transformer = MedievalCharacterTransformer()

    # 테스트 이미지 (본인 사진이나 샘플 이미지 사용)
    input_image = Image.open("test_input.jpg")  # 준비 필요

    # 텍스트 특징 (모델1 출력 시뮬레이션)
    description = "young male with short black hair, athletic build, standing upright"

    # 변환 실행
    result = transformer.generate(input_image=input_image, description=description)

    # 결과 저장
    result["image"].save("output_medieval.png")
    result["pose_skeleton"].save("output_pose.png")

    print("\n✓ 테스트 완료!")
    print(f"  - 생성 시간: {result['metadata']['total_time']}초")
    print("  - 결과 저장: output_medieval.png")


if __name__ == "__main__":
    test_transformation()
