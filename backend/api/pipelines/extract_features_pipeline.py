import numpy as np
from PIL import Image

import torch
from transformers import CLIPProcessor, CLIPModel
from ultralytics import YOLO

from .tags import ALL_TAGS

# -----------------------------
# CLIP: tag scoring
# -----------------------------
_clip_model = None
_clip_processor = None

def load_clip():
    global _clip_model, _clip_processor
    if _clip_model is None:
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model.eval()
    return _clip_model, _clip_processor

@torch.inference_mode()
def clip_top_tags(image: Image.Image, top_k: int = 8):
    model, processor = load_clip()
    inputs = processor(text=ALL_TAGS, images=image, return_tensors="pt", padding=True)
    out = model(**inputs)
    probs = out.logits_per_image[0].softmax(dim=0)

    scored = [(tag, float(probs[i])) for i, tag in enumerate(ALL_TAGS)]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [{"tag": t, "score": p} for t, p in scored[:top_k]]


# -----------------------------
# YOLOv8 Pose
# -----------------------------
_pose_model = None

def load_pose_model():
    global _pose_model
    if _pose_model is None:
        _pose_model = YOLO("yolov8n-pose.pt")  # 최초 실행 시 자동 다운로드
    return _pose_model

KP_NAMES = [
    "nose","left_eye","right_eye","left_ear","right_ear",
    "left_shoulder","right_shoulder","left_elbow","right_elbow",
    "left_wrist","right_wrist","left_hip","right_hip",
    "left_knee","right_knee","left_ankle","right_ankle"
]

def extract_pose_features(image: Image.Image):
    """
    returns:
      found: bool
      pose_conf: float
      bbox_norm: [x1,y1,x2,y2] normalized (0~1)
      derived: dict
    """
    model = load_pose_model()

    w, h = image.size
    im = np.array(image.convert("RGB"))
    res = model.predict(im, verbose=False)[0]

    if res.keypoints is None or len(res.keypoints) == 0:
        return {
            "found": False,
            "pose_conf": 0.0,
            "bbox_norm": None,
            "derived": {},
        }

    # 여러 명이면 가장 큰 bbox를 선택
    boxes = res.boxes.xyxy.cpu().numpy()  # (n,4)
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    idx = int(np.argmax(areas))
    x1, y1, x2, y2 = boxes[idx]

    kpts = res.keypoints.xy[idx].cpu().numpy()     # (17,2)
    kconf = res.keypoints.conf[idx].cpu().numpy()  # (17,)
    pose_conf = float(np.mean(kconf))

    # keypoints dict (normalized)
    kp = {}
    for i, name in enumerate(KP_NAMES):
        x, y = kpts[i]
        kp[name] = [float(x / w), float(y / h), float(kconf[i])]

    derived = derive_metrics(kp)

    bbox_norm = [float(x1 / w), float(y1 / h), float(x2 / w), float(y2 / h)]
    return {
        "found": True,
        "pose_conf": pose_conf,
        "bbox_norm": bbox_norm,
        "derived": derived,
        "kp": kp
    }

def derive_metrics(kp: dict):
    """
    derived metrics (0~?):
      - shoulder_tilt: 좌우 어깨 높이 차 / 어깨 너비
      - body_lean: 상체 중심 기울기
      - stance_width: 발목 간 거리 / 골반 너비
      - arms_open: 손목 간 거리 / 어깨 너비
    """
    def get(name):
        v = kp.get(name)
        if not v:
            return None
        return (v[0], v[1], v[2])

    ls = get("left_shoulder"); rs = get("right_shoulder")
    lh = get("left_hip");      rh = get("right_hip")
    lw = get("left_wrist");    rw = get("right_wrist")
    la = get("left_ankle");    ra = get("right_ankle")

    if not (ls and rs and lh and rh):
        return {}

    shoulder_width = abs(ls[0] - rs[0]) + 1e-6
    hip_width = abs(lh[0] - rh[0]) + 1e-6

    shoulder_tilt = abs(ls[1] - rs[1]) / shoulder_width

    mid_sh_x = (ls[0] + rs[0]) / 2
    mid_hip_x = (lh[0] + rh[0]) / 2
    torso_len = abs(((ls[1] + rs[1]) / 2) - ((lh[1] + rh[1]) / 2)) + 1e-6
    body_lean = abs(mid_sh_x - mid_hip_x) / torso_len

    stance_width = 0.0
    if la and ra:
        ankle_dist = abs(la[0] - ra[0])
        stance_width = ankle_dist / hip_width

    arms_open = 0.0
    if lw and rw:
        wrist_dist = abs(lw[0] - rw[0])
        arms_open = wrist_dist / shoulder_width

    return {
        "shoulder_tilt": float(shoulder_tilt),
        "body_lean": float(body_lean),
        "stance_width": float(stance_width),
        "arms_open": float(arms_open),
    }


# -----------------------------
# Utilities
# -----------------------------
def detect_full_body_from_keypoints(kp: dict, conf_th: float = 0.25) -> bool:
    """
    전신 판정:
    - 최소 조건: 좌/우 어깨 + 좌/우 골반이 잡혀야 함 (기본 포즈 신뢰)
    - 전신 조건: 무릎 또는 발목이 충분한 confidence로 잡히면 전신으로 간주
    """

    def ok(name: str) -> bool:
        v = kp.get(name)
        return v is not None and v[2] >= conf_th  # [x, y, conf]

    core = ok("left_shoulder") and ok("right_shoulder") and ok("left_hip") and ok("right_hip")
    if not core:
        return False

    lower = (ok("left_knee") and ok("right_knee")) or (ok("left_ankle") and ok("right_ankle"))
    return lower

def resize_for_speed(image: Image.Image, max_side: int) -> Image.Image:
    w, h = image.size
    m = max(w, h)
    if m <= max_side:
        return image
    scale = max_side / m
    return image.resize((int(w * scale), int(h * scale)))


# -----------------------------
# Main
# -----------------------------
def main(image: Image.Image, topk: int = 8, max_side: int = 1024):
    image = resize_for_speed(image, max_side)

    # 1) pose derived metrics + bbox
    pose = extract_pose_features(image)
    has_full_body = False
    if pose.get("found"):
        has_full_body = detect_full_body_from_keypoints(pose["kp"])

    warnings = []
    if not pose["found"]:
        warnings.append("no pose detected (person might be missing or too small)")
    if pose["found"] and not has_full_body:
        warnings.append("person detected but not full-body (try stepping back)")

    # 2) clip tags
    tags = clip_top_tags(image, top_k=topk)

    # 3) output json
    return {
        "source": {
            "image_size": {"w": image.size[0], "h": image.size[1]},
            "python_version": "3.12.12",
        },
        "quality": {
            "person_detected": bool(pose["found"]),
            "has_full_body": bool(has_full_body),
            "pose_conf": float(pose["pose_conf"]),
        },
        "pose": {
            "bbox_norm": pose["bbox_norm"],
            "derived": pose["derived"],
        },
        "tags": {
            "top": tags
        }
    }
