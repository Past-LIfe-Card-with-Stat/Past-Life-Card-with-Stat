import time

import torch
from controlnet_aux import OpenposeDetector
from diffusers import StableDiffusionXLControlNetPipeline
from diffusers.models.controlnets.controlnet import ControlNetModel
from PIL import Image


class MedievalCharacterTransformer:
    """
    입력 이미지 + 텍스트 특징 → 중세풍 캐릭터 변환
    GPU 14GB 최적화 버전
    """

    def __init__(self):
        print("Loading models... (첫 실행 시 다운로드에 시간 소요)")

        # 1. ControlNet OpenPose 로드
        self.controlnet = ControlNetModel.from_pretrained(
            "thibaud/controlnet-openpose-sdxl-1.0", torch_dtype=torch.float16
        )

        # 2. SDXL Turbo 파이프라인
        self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
            "stabilityai/sdxl-turbo",
            controlnet=self.controlnet,
            torch_dtype=torch.float16,
        )

        # 3. GPU로 이동
        self.pipe.to("cuda")

        # 4. 메모리 최적화
        self.pipe.enable_xformers_memory_efficient_attention()  # xformers 설치 시

        # 5. OpenPose 감지기
        self.openpose = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")

        print("✓ Models loaded successfully!")

    def generate(
        self,
        input_image: Image.Image,
        description: str,
        style: str = "medieval fantasy",
    ) -> dict:
        """
        메인 생성 함수

        Args:
            input_image: PIL Image 객체
            description: 모델1이 추출한 텍스트 특징
            style: 스타일 키워드

        Returns:
            dict: {
                "image": PIL Image,
                "pose_skeleton": PIL Image,
                "metadata": {...}
            }
        """
        start_time = time.time()

        # Step 1: 포즈 추출
        print("Extracting pose...")
        pose_start = time.time()
        pose_image = self.openpose(input_image, hand_and_face=True)
        pose_time = time.time() - pose_start
        print(f"✓ Pose extraction: {pose_time:.2f}s")

        # Step 2: 프롬프트 구성
        prompt = self.build_prompt(description, style)
        negative_prompt = self.build_negative_prompt()

        print(f"Prompt: {prompt}")

        # Step 3: 이미지 생성
        print("Generating medieval character...")
        gen_start = time.time()

        result_image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=pose_image,
            num_inference_steps=4,  # Turbo는 4 steps 최적
            guidance_scale=0.0,  # Turbo는 guidance_scale 0
            controlnet_conditioning_scale=0.7,
            height=768,  # SDXL 기본 해상도
            width=768,
        ).images[0]

        gen_time = time.time() - gen_start
        total_time = time.time() - start_time

        print(f"✓ Generation: {gen_time:.2f}s")
        print(f"✓ Total: {total_time:.2f}s")

        return {
            "image": result_image,
            "pose_skeleton": pose_image,
            "metadata": {
                "description": description,
                "prompt_used": prompt,
                "pose_extraction_time": round(pose_time, 2),
                "generation_time": round(gen_time, 2),
                "total_time": round(total_time, 2),
                "model": "sdxl-turbo-controlnet",
            },
        }

    def build_prompt(self, description: str, style: str) -> str:
        """텍스트 특징을 프롬프트로 변환"""
        return (
            f"{style} RPG game character, full body portrait, "
            f"{description}, "
            "wearing medieval armor and fantasy clothing, "
            "detailed character illustration, concept art, "
            "dramatic lighting, high quality"
        )

    def build_negative_prompt(self) -> str:
        """네거티브 프롬프트"""
        return (
            "modern clothing, photograph, realistic photo, "
            "blurry, low quality, distorted, ugly, deformed, "
            "watermark, text, signature"
        )


# 싱글톤 인스턴스
_transformer = None


def get_transformer():
    """전역 싱글톤 반환"""
    global _transformer
    if _transformer is None:
        _transformer = MedievalCharacterTransformer()
    return _transformer
