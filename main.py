from backend.pipelines.medieval_pipeline import MedievalPipeline


def main():
    # 파이프라인 초기화 (모델 로딩 시간 소요됨)
    pipeline = MedievalPipeline()

    # 테스트 실행
    input_path = "backend/IMG_6386.jpg"  # 테스트할 이미지 경로
    prompt = "A human who lives in medieval period"

    try:
        result_image = pipeline.run(input_path, prompt)
        result_image.save("result_medieval.png")
        print("Image saved to result_medieval.png")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
