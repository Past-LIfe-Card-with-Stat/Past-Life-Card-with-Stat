from PIL import Image

from backend.app.models.character_generator import CharacterGenerator
from backend.app.models.face_cropper import FaceCropper
from backend.app.models.face_detector import FaceDetector
from backend.app.models.image_blender import ImageBlender


class MedievalPipeline:
    def __init__(self):
        self.detector = FaceDetector()
        self.cropper = FaceCropper()
        self.generator = CharacterGenerator()
        self.blender = ImageBlender()

    def run(self, input_path: str, prompt: str) -> Image.Image:
        # 1. 이미지 로드
        input_image = Image.open(input_path).convert("RGB")

        # 2. 원본 얼굴 찾기
        print("Detecting source face...")
        source_face_info = self.detector.detect(input_image)

        if not source_face_info:
            print("⚠️ Warning: No face detected in source image.")
            # 얼굴 없으면 그냥 생성 결과 반환
            result = self.generator.generate(input_image, prompt)
            return result["image"]

        # 3. 원본 얼굴 추출 (Crop)
        source_face_img = self.cropper.crop(input_image, source_face_info)

        # 4. 캐릭터 생성
        print("Generating character...")
        gen_result = self.generator.generate(input_image, prompt)
        generated_image = gen_result["image"]

        # [추가됨] 디버깅용 저장: 생성된 이미지가 어떻게 생겼는지 확인
        generated_image.save("debug_generated_image.png")
        print("DEBUG: Saved 'debug_generated_image.png' for inspection.")

        # 5. 생성된 이미지에서 얼굴 위치 찾기
        print("Detecting target face...")
        target_face_info = self.detector.detect(generated_image)

        if not target_face_info:
            print("⚠️ Warning: No face detected in generated image.")
            return generated_image

        # 6. 블렌딩 (합성)
        print("Blending faces...")
        final_image = self.blender.blend(
            target_image=generated_image,
            source_face=source_face_img,
            target_face_box=target_face_info["facial_area"],
        )

        print("✓ Process Complete")
        return final_image
