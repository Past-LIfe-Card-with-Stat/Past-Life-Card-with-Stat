"""
이미지 검증 로직
- 이미지 크기, 사람 감지, 얼굴 감지 등을 체크
"""
from PIL import Image
from ultralytics import YOLO
from retinaface import RetinaFace
import numpy as np
import cv2


class ImageValidator:
    def __init__(self):
        self.yolo_model = YOLO("yolov8n-pose.pt")
        self.min_size = 256
        self.max_size = 4096
        
    def validate(self, image: Image.Image) -> dict:
        """
        이미지 검증 수행
        
        Returns:
            {
                "valid": bool,
                "errors": list[str],
                "warnings": list[str],
                "metadata": dict
            }
        """
        errors = []
        warnings = []
        metadata = {}
        
        # 1. 이미지 크기 검증
        w, h = image.size
        metadata["size"] = {"width": w, "height": h}
        
        if w < self.min_size or h < self.min_size:
            errors.append(f"이미지가 너무 작습니다 (최소 {self.min_size}x{self.min_size} 필요)")
        
        if w > self.max_size or h > self.max_size:
            errors.append(f"이미지가 너무 큽니다 (최대 {self.max_size}x{self.max_size} 지원)")
        
        # 2. 이미지 손상 체크 (기본 로드 성공 여부)
        try:
            image.verify()
            image = image.copy()  # verify 후 재로드 필요
        except Exception as e:
            errors.append(f"이미지 파일이 손상되었습니다: {str(e)}")
            return {"valid": False, "errors": errors, "warnings": warnings, "metadata": metadata}
        
        # 3. 사람 감지 (YOLO Pose)
        img_np = np.array(image.convert("RGB"))
        results = self.yolo_model.predict(img_np, verbose=False)
        
        person_detected = False
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None and len(result.boxes) > 0:
                person_detected = True
                metadata["person_count"] = len(result.boxes)
        
        if not person_detected:
            errors.append("이미지에서 사람을 감지할 수 없습니다. 전신 사진을 사용해주세요.")
        
        # 4. 얼굴 감지 (RetinaFace)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        try:
            faces = RetinaFace.detect_faces(img_bgr, threshold=0.5)
            
            if not faces or isinstance(faces, tuple):
                warnings.append("얼굴을 명확하게 감지할 수 없습니다. Face Swap 기능이 제한될 수 있습니다.")
                metadata["face_detected"] = False
            else:
                metadata["face_detected"] = True
                metadata["face_count"] = len(faces)
        except Exception as e:
            warnings.append(f"얼굴 감지 중 오류 발생: {str(e)}")
            metadata["face_detected"] = False
        
        # 5. 전체 검증 결과
        is_valid = len(errors) == 0
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }


# 싱글톤 인스턴스
_validator = None

def get_validator() -> ImageValidator:
    """검증기 싱글톤"""
    global _validator
    if _validator is None:
        _validator = ImageValidator()
    return _validator
