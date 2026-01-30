import cv2
import numpy as np
from PIL import Image
from retinaface import RetinaFace


class FaceDetector:
    """
    RetinaFace를 사용한 얼굴 검출기
    """

    def __init__(self):
        pass

    def detect(self, image: Image.Image):
        """
        가장 큰 얼굴 1개를 찾아 반환
        """
        # 1. PIL 이미지를 numpy 배열로 변환 (RGB)
        img_np = np.array(image)

        # 2. RGB -> BGR 변환 (RetinaFace/OpenCV 호환성 확보 핵심)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        print(f"DEBUG: Image shape: {img_bgr.shape}")

        try:
            # 3. 얼굴 검출 실행
            # threshold를 0.5로 낮춰서(기본 0.9) 인식률 높임
            resp = RetinaFace.detect_faces(img_bgr, threshold=0.5)

            # 디버깅: 결과가 무엇인지 출력
            # print(f"DEBUG: Raw Detection Result: {resp}")

            # 결과가 없거나 튜플(에러/빈값)인 경우 처리
            if not resp or isinstance(resp, tuple):
                print("DEBUG: No faces detected (empty response).")
                return None

            # 4. 가장 큰 얼굴 추출
            best_face = None
            max_area = 0

            for key, face_data in resp.items():
                # face_data 구조: {'score': 0.99, 'facial_area': [x1, y1, x2, y2], ...}
                area_coords = face_data["facial_area"]

                # 면적 계산 (x2-x1) * (y2-y1)
                width = area_coords[2] - area_coords[0]
                height = area_coords[3] - area_coords[1]
                current_area = width * height

                if current_area > max_area:
                    max_area = current_area
                    best_face = face_data

            if best_face:
                print(
                    f"DEBUG: Face found! Score: {best_face.get('score', 0):.2f}, Area: {max_area}"
                )

            return best_face

        except Exception as e:
            print(f"DEBUG: Error inside RetinaFace: {e}")
            return None
