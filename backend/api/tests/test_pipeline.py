"""파이프라인 단위 테스트"""

from PIL import Image

from api.pipelines.medieval_pipeline import MedievalPipeline


def test_medieval_pipeline():
    """MedievalPipeline 기본 동작 테스트"""
    pipeline = MedievalPipeline()

    # 더미 이미지 생성
    test_image = Image.new("RGB", (512, 512), color="red")
    prompt = "A human living in medieval period "

    result = pipeline.run(test_image, prompt)

    assert isinstance(result, Image.Image)
    assert result.size == (768, 768)  # 예상 출력 크기


def test_pipeline_with_file():
    """실제 파일로 테스트"""
    pipeline = MedievalPipeline()

    input_path = "test_input.jpg"
    prompt = "A medieval warrior"

    result = pipeline.run(input_path, prompt)

    assert result is not None
    result.save("test_output.png")
