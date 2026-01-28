import time
from typing import Dict, Union

import torch
from controlnet_aux import OpenposeDetector
from diffusers import StableDiffusionXLControlNetPipeline
from diffusers.models.controlnets.controlnet import ControlNetModel
from PIL import Image


class MedievalCharacterTransformer:
    """
    입력 이미지 + 텍스트 특징 → 중세 유럽풍 캐릭터 변환
    GPU 14GB 최적화 버전 + 얼굴 보존 강화
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
        try:
            self.pipe.enable_xformers_memory_efficient_attention()
            print("✓ xformers enabled")
        except:
            print("⚠ xformers not available")

        # 5. OpenPose 감지기
        self.openpose = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")

        print("✓ Models loaded successfully!")

    def parse_model1_output(self, model1_data: Union[str, Dict]) -> str:
        """
        모델1의 JSON 출력을 자연어 프롬프트로 변환

        Args:
            model1_data: 모델1의 JSON 또는 문자열

        Returns:
            자연어 설명 문자열
        """
        # 이미 문자열이면 그대로 반환
        if isinstance(model1_data, str):
            return model1_data

        description_parts = []

        # === 1. Tags 기반 설명 ===
        if "tags" in model1_data and "top" in model1_data["tags"]:
            tags = model1_data["tags"]["top"]
            # 상위 3개 태그만 사용
            for tag_obj in tags[:3]:
                tag = tag_obj.get("tag", "")
                if tag:
                    description_parts.append(tag)

        # === 2. Pose 기반 특성 추가 ===
        if "pose" in model1_data and "derived" in model1_data["pose"]:
            pose = model1_data["pose"]["derived"]

            # 자세 해석
            stance_width = pose.get("stance_width", 1.0)
            arms_open = pose.get("arms_open", 0.5)
            body_lean = pose.get("body_lean", 0.0)

            # 자세 설명 추가
            if stance_width > 1.3:
                description_parts.append("wide confident stance")
            elif stance_width < 0.8:
                description_parts.append("narrow cautious stance")

            if arms_open > 0.6:
                description_parts.append("open arms gesture")
            elif arms_open < 0.3:
                description_parts.append("arms close to body")

            if abs(body_lean) > 0.15:
                if body_lean > 0:
                    description_parts.append("leaning forward")
                else:
                    description_parts.append("leaning backward")

        # === 3. Quality 정보 (로그용) ===
        if "quality" in model1_data:
            quality = model1_data["quality"]
            print(
                f"  Quality - Person: {quality.get('person_detected')}, "
                f"Full Body: {quality.get('has_full_body')}, "
                f"Confidence: {quality.get('pose_conf', 0):.2f}"
            )

        # 설명 조합
        if description_parts:
            return ", ".join(description_parts)
        else:
            return "person in portrait"

    def generate(
        self,
        input_image: Image.Image,
        description: Union[str, Dict],
        style: str = "medieval fantasy",
        face_preservation_strength: float = 0.85,  # 얼굴 보존 강도 (높을수록 원본 유지)
    ) -> dict:
        """
        메인 생성 함수

        Args:
            input_image: PIL Image 객체
            description: 모델1의 JSON 또는 텍스트 특징
            style: 스타일 키워드
            face_preservation_strength: 얼굴 보존 강도 (0.7-0.95 권장)

        Returns:
            dict: {
                "image": PIL Image,
                "pose_skeleton": PIL Image,
                "metadata": {...}
            }
        """
        start_time = time.time()

        # === JSON 파싱 ===
        if isinstance(description, dict):
            parsed_description = self.parse_model1_output(description)
            print(f"✓ Parsed description: {parsed_description}")
        else:
            parsed_description = description

        # Step 1: 포즈 추출
        print("Extracting pose...")
        pose_start = time.time()
        pose_image = self.openpose(input_image, hand_and_face=True)
        pose_time = time.time() - pose_start
        print(f"✓ Pose extraction: {pose_time:.2f}s")

        # Step 2: 프롬프트 구성 (얼굴 보존 강조)
        prompt = self.build_prompt(parsed_description, style)
        negative_prompt = self.build_negative_prompt()

        print(f"Prompt: {prompt[:100]}...")

        # Step 3: 이미지 생성 (얼굴 보존 파라미터 조정)
        print("Generating medieval character...")
        gen_start = time.time()

        result_image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=pose_image,
            num_inference_steps=6,  # 4→6으로 증가 (품질 향상)
            guidance_scale=0.0,
            controlnet_conditioning_scale=face_preservation_strength,  # 얼굴 보존 강화
            height=768,
            width=768,
        ).images[0]

        gen_time = time.time() - gen_start
        total_time = time.time() - start_time

        print(f"✓ Generation: {gen_time:.2f}s")
        print(f"✓ Total: {total_time:.2f}s")

        return {
            "image": result_image,
            "pose_skeleton": pose_image,
            "original_input": description,  # 원본 JSON 보존
            "parsed_description": parsed_description,
            "metadata": {
                "prompt_used": prompt,
                "face_preservation_strength": face_preservation_strength,
                "pose_extraction_time": round(pose_time, 2),
                "generation_time": round(gen_time, 2),
                "total_time": round(total_time, 2),
                "model": "sdxl-turbo-controlnet",
            },
        }

    def build_prompt(self, description: str, style: str) -> str:
        """
        텍스트 특징을 프롬프트로 변환 (얼굴 보존 강조)
        """
        return (
            f"{style} RPG character portrait, {description}, "
            "wearing medieval fantasy armor and clothing, "
            "IMPORTANT: preserve original face, keep facial features, maintain face identity, "
            "detailed character concept art, painterly style, "
            "dramatic cinematic lighting, high quality, masterpiece"
        )

    def build_negative_prompt(self) -> str:
        """네거티브 프롬프트 - 얼굴 변경 방지 강화"""
        return (
            "modern clothing, photograph, realistic photo, "
            "different face, changed facial features, altered face, face swap, "
            "wrong face, distorted face, multiple faces, "
            "blurry, low quality, ugly, deformed, "
            "watermark, text, signature, logo"
        )


# 싱글톤 인스턴스
_transformer = None


def get_transformer():
    """전역 싱글톤 반환"""
    global _transformer
    if _transformer is None:
        _transformer = MedievalCharacterTransformer()
    return _transformer
