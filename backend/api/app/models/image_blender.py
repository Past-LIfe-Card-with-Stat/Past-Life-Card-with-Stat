from PIL import Image, ImageDraw, ImageFilter, ImageOps  # ImageOps 추가
import cv2
import numpy as np


class ImageBlender:
    """
    이미지 합성 및 블렌딩 처리
    """

    def create_soft_mask(self, size: tuple) -> Image.Image:
        """
        타원형의 부드러운 그라데이션 마스크 생성
        """
        w, h = size
        # 검정 배경
        mask = Image.new("L", size, 0)

        # 내부 흰색 타원 (약간 작게 그려서 가장자리 확보)
        draw = ImageDraw.Draw(mask)

        # 타원 좌표 (여백 10% 둠)
        margin_w = w * 0.1
        margin_h = h * 0.1
        draw.ellipse((margin_w, margin_h, w - margin_w, h - margin_h), fill=255)

        # 가우시안 블러로 경계 부드럽게
        mask = mask.filter(ImageFilter.GaussianBlur(radius=15))
        return mask

    def correct_color_tone(self, source_face: Image.Image, target_region: Image.Image) -> Image.Image:
        """
        원본 얼굴의 색상을 타겟 이미지의 톤에 맞춤
        """
        # PIL → numpy
        src_np = np.array(source_face).astype(np.float32)
        tgt_np = np.array(target_region).astype(np.float32)

        # 평균 색상 계산
        src_mean = np.mean(src_np, axis=(0, 1))
        tgt_mean = np.mean(tgt_np, axis=(0, 1))

        # 표준편차 계산
        src_std = np.std(src_np, axis=(0, 1))
        tgt_std = np.std(tgt_np, axis=(0, 1))

        # 색상 정규화 (타겟 톤으로 맞춤)
        corrected = src_np.copy()
        for c in range(3):
            if src_std[c] > 1:  # 0으로 나누기 방지
                corrected[:, :, c] = (src_np[:, :, c] - src_mean[c]) * (tgt_std[c] / src_std[c]) + tgt_mean[c]
            else:
                corrected[:, :, c] = src_np[:, :, c] - src_mean[c] + tgt_mean[c]

        # 범위 정규화
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        return Image.fromarray(corrected)

    def blend(
        self, target_image: Image.Image, source_face: Image.Image, target_face_box: list
    ) -> Image.Image:
        """
        target_image: 생성된 캐릭터 전신 사진
        source_face: 원본에서 잘라낸 얼굴 이미지
        target_face_box: 생성된 캐릭터의 얼굴 좌표 [x1, y1, x2, y2]
        """
        # 1. 타겟 얼굴 크기 계산
        tx1, ty1, tx2, ty2 = target_face_box
        t_w = tx2 - tx1
        t_h = ty2 - ty1

        # 2. 원본 얼굴 리사이즈 (LANCZOS 필터 사용)
        resized_face = source_face.resize((t_w, t_h), Image.Resampling.LANCZOS)

        # 3. 타겟 영역 추출
        target_region = target_image.crop((tx1, ty1, tx2, ty2))

        # 4. 색상 보정 (타겟 톤에 맞추기)
        resized_face = self.correct_color_tone(resized_face, target_region)

        # 5. 마스크 생성
        mask = self.create_soft_mask((t_w, t_h))

        # 6. 붙여넣기 (PIL paste 기능 활용)
        # 이미지를 복사해서 원본 보존
        final_image = target_image.copy()
        final_image.paste(resized_face, (tx1, ty1), mask)

        return final_image
