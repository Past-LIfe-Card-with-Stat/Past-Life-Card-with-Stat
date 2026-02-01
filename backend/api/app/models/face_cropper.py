from PIL import Image


class FaceCropper:
    """
    얼굴 영역을 적절한 여백(Margin)과 함께 잘라내는 클래스
    """

    def crop(
        self, image: Image.Image, face_data, margin_scale: float = 1.2
    ) -> Image.Image:
        """
        face_data['facial_area']를 기반으로 여백을 두고 자름
        margin_scale: 1.2 (이전 1.5에서 축소하여 배경 혼입 감소)
        """
        if not face_data:
            return None

        # RetinaFace output: [x1, y1, x2, y2]
        box = face_data["facial_area"]
        x1, y1, x2, y2 = box

        w = x2 - x1
        h = y2 - y1

        # 중심점
        cx = x1 + w // 2
        cy = y1 + h // 2

        # 여백 적용하여 크기 키우기
        new_w = int(w * margin_scale)
        new_h = int(h * margin_scale)

        # 이미지 경계 체크
        img_w, img_h = image.size

        nx1 = max(0, cx - new_w // 2)
        ny1 = max(0, cy - new_h // 2)
        nx2 = min(img_w, cx + new_w // 2)
        ny2 = min(img_h, cy + new_h // 2)

        cropped_face = image.crop((nx1, ny1, nx2, ny2))
        return cropped_face
