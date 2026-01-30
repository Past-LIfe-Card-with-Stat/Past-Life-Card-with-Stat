# model2.py (수정 버전)
import time
from typing import Dict, Optional, Union

import cv2
import numpy as np
import torch
from controlnet_aux import OpenposeDetector
from diffusers import StableDiffusionXLControlNetPipeline
from diffusers.models.controlnets.controlnet import ControlNetModel
from PIL import Image


class MedievalCharacterTransformer:
    """
    입력 이미지 + 텍스트 특징 → 중세 유럽풍 캐릭터 변환
    GPU 14GB 최적화 버전 + 단일 인물 보장
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

    def _filter_largest_person(self, pose_image: Image.Image) -> Image.Image:
        """OpenPose 결과에서 가장 큰 skeleton만 남기기"""
        pose_np = np.array(pose_image)

        # Grayscale 변환
        if len(pose_np.shape) == 3:
            gray = cv2.cvtColor(pose_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = pose_np

        # 이진화
        _, binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

        # Connected Components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        if num_labels <= 2:  # 배경 + 1명
            print("  ✓ Single person detected")
            return pose_image

        # 가장 큰 컴포넌트 (배경 제외)
        areas = stats[1:, cv2.CC_STAT_AREA]
        largest_idx = np.argmax(areas) + 1

        # 마스크 생성
        mask = (labels == largest_idx).astype(np.uint8) * 255

        # 적용
        if len(pose_np.shape) == 3:
            filtered = cv2.bitwise_and(pose_np, pose_np, mask=mask)
        else:
            filtered = cv2.bitwise_and(pose_np, pose_np, mask=mask)

        print(f"  ⚠ {num_labels - 1} persons detected, kept largest")

        return Image.fromarray(filtered)

    def parse_model1_output(self, model1_data: Union[str, Dict]) -> tuple:
        """
        모델1의 JSON 출력을 (description, occupation)으로 변환

        Returns:
            (description: str, occupation: str)
        """
        if isinstance(model1_data, str):
            return model1_data, None

        description_parts = []
        occupation = None

        # Tags에서 직업 추출
        if "tags" in model1_data and "top" in model1_data["tags"]:
            tags = model1_data["tags"]["top"]

            # 직업 관련 태그 우선 추출
            occupation_keywords = {
                "warrior": "knight",
                "fighter": "knight",
                "strong": "knight",
                "magic": "mage",
                "wise": "mage",
                "intelligent": "mage",
                "agile": "archer",
                "quick": "archer",
                "merchant": "merchant",
                "trader": "merchant",
                "farmer": "peasant",
                "worker": "peasant",
                "noble": "noble",
                "elegant": "noble",
                "priest": "priest",
                "holy": "priest",
            }

            for tag_obj in tags[:3]:
                tag = tag_obj.get("tag", "").lower()
                if tag:
                    description_parts.append(tag)
                    # 직업 매칭
                    if not occupation:
                        for keyword, job in occupation_keywords.items():
                            if keyword in tag:
                                occupation = job
                                break

        # Pose 기반 특성 추가
        if "pose" in model1_data and "derived" in model1_data["pose"]:
            pose = model1_data["pose"]["derived"]
            stance_width = pose.get("stance_width", 1.0)
            arms_open = pose.get("arms_open", 0.5)

            if stance_width > 1.3:
                description_parts.append("wide confident stance")
            if arms_open > 0.6:
                description_parts.append("open arms gesture")

        description = (
            ", ".join(description_parts) if description_parts else "person in portrait"
        )

        # 직업이 없으면 기본값
        if not occupation:
            occupation = None  # 프롬프트에서 자동 선택

        print(f"  Parsed - Description: {description}, Occupation: {occupation}")

        return description, occupation

    def generate(
        self,
        input_image: Image.Image,
        description: Union[str, Dict],
        style: str = "medieval fantasy",
        pose_strength: float = 0.5,  # pose 따라가기 강도 (0.3~0.7)
    ) -> dict:
        """
        메인 생성 함수

        Args:
            input_image: PIL Image 객체
            description: 모델1의 JSON 또는 텍스트 특징
            style: 스타일 키워드
            pose_strength: ControlNet 강도 (0.3=창의적, 0.7=정확한 자세)

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
            parsed_description, occupation = self.parse_model1_output(description)
            print(f"✓ Parsed - Desc: {parsed_description}, Job: {occupation}")
        else:
            parsed_description = description
            occupation = None

        # Step 1: 포즈 추출 + 단일 인물 필터링
        print("Extracting pose...")
        pose_start = time.time()
        pose_image_raw = self.openpose(input_image, hand_and_face=True)

        # ⭐ 핵심: 가장 큰 사람만 남기기
        pose_image = self._filter_largest_person(pose_image_raw)

        pose_time = time.time() - pose_start
        print(f"✓ Pose extraction: {pose_time:.2f}s")

        # Step 2: 프롬프트 구성 (직업 기반)
        prompt = self.build_prompt(parsed_description, style, occupation)
        negative_prompt = self.build_negative_prompt()

        print(f"Prompt: {prompt[:100]}...")

        # Step 3: 이미지 생성
        print("Generating medieval character...")
        gen_start = time.time()

        result_image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=pose_image,
            num_inference_steps=6,
            guidance_scale=1.0,  # ⭐ 0→1 (프롬프트 따라가기)
            controlnet_conditioning_scale=pose_strength,  # ⭐ pose 강도
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
            "original_input": description,
            "parsed_description": parsed_description,
            "detected_occupation": occupation,
            "metadata": {
                "prompt_used": prompt,
                "pose_strength": pose_strength,
                "pose_extraction_time": round(pose_time, 2),
                "generation_time": round(gen_time, 2),
                "total_time": round(total_time, 2),
                "model": "sdxl-turbo-controlnet",
            },
        }

    def build_prompt(
        self, description: str, style: str, occupation: Optional[str] = None
    ) -> str:
        """텍스트 특징을 프롬프트로 변환 (직업별 의상)"""
        outfit_map = {
            "knight": "wearing heavy plate armor and helmet with sword",
            "mage": "wearing long wizard robes with staff and pointed hat",
            "archer": "wearing leather armor and hooded cloak with bow",
            "merchant": "wearing rich merchant clothing and cape with coins",
            "peasant": "wearing simple linen tunic and pants with farming tools",
            "noble": "wearing elegant noble attire with jewelry and crown",
            "priest": "wearing religious robes with cross necklace",
            "blacksmith": "wearing leather apron and work clothes with hammer",
            None: "wearing medieval fantasy clothing appropriate for their role",
        }

        outfit = outfit_map.get(occupation, outfit_map[None])

        return (
            f"{style} RPG character portrait, {description}, "
            f"{outfit}, "
            "full body shot, single person, solo character, "
            "detailed character concept art, painterly style, "
            "dramatic cinematic lighting, high quality, masterpiece"
        )

    def build_negative_prompt(self) -> str:
        """네거티브 프롬프트"""
        return (
            "multiple people, two people, crowd, group, "
            "extra limbs, extra legs, extra arms, third leg, multiple legs, "
            "deformed limbs, mutated limbs, fused limbs, "
            "modern clothing, photograph, realistic photo, "
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
