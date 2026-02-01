from PIL import Image

from api.pipelines import extract_features_pipeline
from api.pipelines.generate_description import generate_description_for_model3
from api.app.services.character_generator import CharacterGenerator
from api.app.services.stat_calculator import calculate_stats
from api.app.services.input_adapter import InputAdapter
from api.app.models.face_cropper import FaceCropper
from api.app.models.face_detector import FaceDetector
from api.app.models.image_blender import ImageBlender
from api.app.models.model2 import get_transformer


class MedievalPipeline:
    def __init__(self):
        # Face Tools
        self.detector = FaceDetector()
        self.cropper = FaceCropper()
        self.blender = ImageBlender()

        # Image Generator (SDXL-Turbo + ControlNet)
        self.image_generator = get_transformer()

        # Stat/Card Generator
        self.stat_generator = CharacterGenerator(use_llm=True)

    def run(self, input_image: Image.Image) -> dict:
        print("=== Medieval Pipeline Started ===")

        # -----------------------------------------------------
        # Step 1: 이미지 분석 특징 추출 (Input Features)
        # -----------------------------------------------------
        print("[Step 1] Extracting features from Input Image...")
        input_features = extract_features_pipeline.main(input_image)

        # -----------------------------------------------------
        # Step 2: 원본 얼굴 찾기 & 추출
        # -----------------------------------------------------
        print("[Step 2] Detecting source face...")
        source_face_info = self.detector.detect(input_image)
        source_face_img = None

        if source_face_info:
            source_face_img = self.cropper.crop(input_image, source_face_info)
        else:
            print("  Warning: No face detected in source image.")

        # -----------------------------------------------------
        # Step 3: 중세 이미지 생성
        # -----------------------------------------------------
        print("[Step 3] Generating Medieval Image...")

        # Description 생성
        temp_internal = InputAdapter.to_internal_features(input_features)
        temp_stats = calculate_stats(temp_internal)
        description_data = generate_description_for_model3(input_features, temp_stats)

        # 이미지 생성 (SDXL-Turbo + ControlNet)
        gen_result = self.image_generator.generate(
            input_image=input_image,
            description=input_features,  # 모델1 출력 전달
            style="medieval fantasy",
            pose_strength=0.5,
        )
        generated_image = gen_result["image"]

        # 디버깅용 저장
        generated_image.save("debug_generated_image.png")
        print("  DEBUG: Saved 'debug_generated_image.png'")

        # -----------------------------------------------------
        # Step 4: Face Swap (원본 얼굴을 생성된 이미지에 합성)
        # -----------------------------------------------------
        if source_face_img:
            print("[Step 4] Detecting target face for blending...")
            target_face_info = self.detector.detect(generated_image)

            if target_face_info:
                print("  Blending faces...")
                generated_image = self.blender.blend(
                    target_image=generated_image,
                    source_face=source_face_img,
                    target_face_box=target_face_info["facial_area"],
                )
            else:
                # Fallback: 얼굴 감지 실패 시 중앙 영역에 배치
                print("  Warning: Face not detected in generated image. Using center placement fallback...")
                img_w, img_h = generated_image.size
                face_w, face_h = source_face_img.size
                # 중앙에 배치
                x1 = max(0, (img_w - face_w) // 2)
                y1 = max(0, (img_h - face_h) // 2)
                x2 = min(img_w, x1 + face_w)
                y2 = min(img_h, y1 + face_h)
                fallback_box = [x1, y1, x2, y2]
                generated_image = self.blender.blend(
                    target_image=generated_image,
                    source_face=source_face_img,
                    target_face_box=fallback_box,
                )
        else:
            print("[Step 4] Skipping face blend (no source face)")

        # -----------------------------------------------------
        # Step 5: 생성된 이미지에서 특징 추출
        # -----------------------------------------------------
        print("[Step 5] Extracting features from Medieval Image...")
        generated_features = extract_features_pipeline.main(generated_image)

        # -----------------------------------------------------
        # Step 6: 스탯, 직업, flavor_text 생성
        # -----------------------------------------------------
        print("[Step 6] Calculating Stats & Identity...")

        merged_input = {
            "pose": input_features.get("pose"),
            "tags": generated_features.get("tags"),
            "description": description_data
        }

        card_data = self.stat_generator.generate(merged_input)

        print("=== Pipeline Complete ===")

        return {
            "input_features": input_features,
            "generated_image": generated_image,
            "generated_features": generated_features,
            "card_data": card_data
        }
