import torch
from controlnet_aux import OpenposeDetector
from diffusers import AutoencoderKL, StableDiffusionXLControlNetPipeline
from diffusers.models.controlnets.controlnet import ControlNetModel
from PIL import Image


class CharacterGenerator:
    """
    SDXL Turbo + ControlNet OpenPose 생성기
    """

    def __init__(self):
        print("Loading Generation Models...")

        # 1. ControlNet
        self.controlnet = ControlNetModel.from_pretrained(
            "thibaud/controlnet-openpose-sdxl-1.0", torch_dtype=torch.float16
        )

        # 2. VAE (메모리 최적화용, 선택사항)
        vae = AutoencoderKL.from_pretrained(
            "madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16
        )

        # 3. Pipeline
        self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
            "stabilityai/sdxl-turbo",
            controlnet=self.controlnet,
            vae=vae,
            torch_dtype=torch.float16,
            variant="fp16",
        ).to("cuda")

        # 스케줄러 설정 (Turbo용)
        self.pipe.scheduler.config.use_karras_sigmas = True

        # 4. OpenPose Detector
        self.openpose = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
        print("✓ Generation Models Loaded")

    def generate(self, input_image: Image.Image, prompt: str) -> dict:
        """
        포즈를 추출하고 캐릭터 생성
        """
        # 포즈 추출
        pose_image = self.openpose(input_image, hand_and_face=True)

        # 생성
        full_prompt = f"{prompt}, medieval fantasy style, highly detailed, masterpiece"
        negative_prompt = (
            "nsfw, low quality, bad anatomy, worst quality, text, watermark"
        )

        result = self.pipe(
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            image=pose_image,
            num_inference_steps=4,  # Turbo 모델이라 적은 스텝 수
            guidance_scale=0.0,  # Turbo 모델은 0.0 권장
            controlnet_conditioning_scale=0.6,  # 포즈 반영 강도
            height=1024,
            width=1024,
        ).images[0]

        return {"image": result, "pose": pose_image}
