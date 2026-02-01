"""
Model 3에게 전달할 Description 생성
Appearance 정보만 포함 (clothing_style, build_type, posture)
"""

# ===== 기본값 정의 =====
DEFAULT_APPEARANCE = {
    "clothing_style": "casual",
    "build_type": "average",
    "posture": "neutral",
}


def generate_description_for_model3(
    features: dict, stats: dict, detected_occupation: str = None
) -> dict:
    """
    Model 3용 description 생성 (appearance만 포함)

    Args:
        features: extract_features_pipeline의 출력
        stats: calculate_stats의 출력
        detected_occupation: Model 2에서 감지한 직업 (optional)

    Returns:
        {
            "appearance": {
                "clothing_style": str (항상 값 존재),
                "build_type": str (항상 값 존재),
                "posture": str (항상 값 존재)
            }
        }
    """
    pose_derived = features.get("pose", {}).get("derived", {})
    tags_list = features.get("tags", {}).get("top", [])
    quality = features.get("quality", {})

    # ===== 1. Clothing Style (직업 + Tags 기반) =====
    clothing_style = infer_clothing_style(
        stats=stats, tags=tags_list, detected_occupation=detected_occupation
    )

    # ===== 2. Build Type (Pose + Stats 기반) =====
    build_type = infer_build_type(
        pose_derived=pose_derived, stats=stats, quality=quality
    )

    # ===== 3. Posture (Pose metrics 기반) =====
    posture = infer_posture(pose_derived=pose_derived, quality=quality)

    return {
        "appearance": {
            "clothing_style": clothing_style,
            "build_type": build_type,
            "posture": posture,
        }
    }


# ===== Clothing Style 추론 =====
def infer_clothing_style(
    stats: dict, tags: list, detected_occupation: str = None
) -> str:
    """
    의상 스타일 추론 (항상 값 반환, 최소 "casual")

    우선순위:
    1. detected_occupation (Model 2에서 감지한 직업)
    2. Stats 기반 추론 (STR/INT/CHA 비율)
    3. Tags 키워드 매칭
    4. 기본값: "casual"
    """
    # 1. Occupation 기반
    if detected_occupation:
        occupation_map = {
            "knight": "combat-ready",
            "warrior": "combat-ready",
            "mage": "ceremonial",
            "priest": "ceremonial",
            "noble": "formal",
            "merchant": "formal",
            "craftsman": "work-clothes",
            "peasant": "work-clothes",
        }
        if detected_occupation in occupation_map:
            return occupation_map[detected_occupation]

    # 2. Stats 기반 추론
    str_val = stats.get("STR", 10)
    int_val = stats.get("INT", 10)
    cha_val = stats.get("CHA", 10)
    vit_val = stats.get("VIT", 10)

    # STR + VIT 높으면 → combat-ready
    if str_val + vit_val >= 45:
        return "combat-ready"

    # INT 높으면 → ceremonial
    if int_val >= 25:
        return "ceremonial"

    # CHA 높으면 → formal
    if cha_val >= 25:
        return "formal"

    # 3. Tags 키워드 매칭
    tags_dict = {t["tag"].lower(): t["score"] for t in tags}

    # 전투/무기 관련 태그
    combat_keywords = ["warrior", "fighter", "soldier", "armed", "battle"]
    if any(keyword in tag for keyword in combat_keywords for tag in tags_dict.keys()):
        return "combat-ready"

    # 격식 있는 태그
    formal_keywords = ["elegant", "formal", "noble", "refined"]
    if any(keyword in tag for keyword in formal_keywords for tag in tags_dict.keys()):
        return "formal"

    # 작업복 관련 태그
    work_keywords = ["worker", "laborer", "craftsman", "farmer", "tool"]
    if any(keyword in tag for keyword in work_keywords for tag in tags_dict.keys()):
        return "work-clothes"

    # 4. 기본값
    return "casual"


# ===== Build Type 추론 =====
def infer_build_type(pose_derived: dict, stats: dict, quality: dict) -> str:
    """
    체격 추론 (항상 값 반환, 최소 "average")

    우선순위:
    1. STR + VIT + stance_width 조합
    2. STR + VIT만 사용
    3. 기본값: "average"
    """
    str_val = stats.get("STR", 10)
    vit_val = stats.get("VIT", 10)
    stance_width = pose_derived.get("stance_width", 1.0)

    # Pose 감지 실패 시 Stats만 사용
    if not quality.get("person_detected", False):
        # Stats만으로 판단
        strength_sum = str_val + vit_val

        if strength_sum >= 50:
            return "bulky"
        elif strength_sum >= 40:
            return "muscular"
        elif strength_sum >= 30:
            return "athletic"
        elif strength_sum >= 20:
            return "average"
        else:
            return "lean"

    # Pose 감지 성공 시 stance_width 포함
    build_score = str_val + vit_val + (stance_width * 10)

    if build_score >= 55:
        return "bulky"
    elif build_score >= 45:
        return "muscular"
    elif build_score >= 35:
        return "athletic"
    elif build_score >= 25:
        return "average"
    else:
        return "lean"


# ===== Posture 추론 =====
def infer_posture(pose_derived: dict, quality: dict) -> str:
    """
    자세 추론 (항상 값 반환, 최소 "neutral")

    우선순위:
    1. Pose metrics (arms_open, body_lean, shoulder_tilt)
    2. Pose confidence 기반 추정
    3. 기본값: "neutral"
    """
    # Pose 감지 실패 시 기본값
    if not quality.get("person_detected", False):
        return "neutral"

    arms_open = pose_derived.get("arms_open", 0.5)
    body_lean = pose_derived.get("body_lean", 0.0)
    shoulder_tilt = pose_derived.get("shoulder_tilt", 0.0)
    stance_width = pose_derived.get("stance_width", 1.0)

    # Pose metrics가 비어있으면 기본값
    if not pose_derived:
        return "neutral"

    # 1. Aggressive (공격적): 앞으로 기울임 + 넓은 자세
    if body_lean > 0.15 and stance_width > 1.2:
        return "aggressive"

    # 2. Confident (자신감): 팔 벌림 + 안정적 어깨
    if arms_open > 0.6 and shoulder_tilt < 0.1:
        return "confident"

    # 3. Cautious (조심스러운): 좁은 자세 + 팔 모음
    if stance_width < 0.8 and arms_open < 0.4:
        return "cautious"

    # 4. Elegant (우아한): 안정적 + 중간 팔 벌림
    if shoulder_tilt < 0.08 and 0.4 <= arms_open <= 0.6:
        return "elegant"

    # 5. Relaxed (편안한): 중간 수치들
    if body_lean < 0.1 and 0.3 <= arms_open <= 0.7:
        return "relaxed"

    # 6. 기본값
    return "neutral"


# ===== 디버깅/테스트용 함수 =====
def explain_appearance(
    features: dict, stats: dict, detected_occupation: str = None
) -> dict:
    """
    Appearance 생성 과정을 상세히 설명 (디버깅용)
    """
    pose_derived = features.get("pose", {}).get("derived", {})
    quality = features.get("quality", {})

    appearance = generate_description_for_model3(features, stats, detected_occupation)

    reasoning = {
        "clothing_style": {
            "value": appearance["appearance"]["clothing_style"],
            "reason": f"Occupation={detected_occupation}, STR={stats.get('STR')}, CHA={stats.get('CHA')}",
        },
        "build_type": {
            "value": appearance["appearance"]["build_type"],
            "reason": f"STR={stats.get('STR')}, VIT={stats.get('VIT')}, stance_width={pose_derived.get('stance_width', 'N/A')}",
        },
        "posture": {
            "value": appearance["appearance"]["posture"],
            "reason": f"arms_open={pose_derived.get('arms_open', 'N/A')}, body_lean={pose_derived.get('body_lean', 'N/A')}",
        },
    }

    return {
        "appearance": appearance["appearance"],
        "reasoning": reasoning,
        "fallback_used": {
            "clothing_style": appearance["appearance"]["clothing_style"]
            == DEFAULT_APPEARANCE["clothing_style"],
            "build_type": appearance["appearance"]["build_type"]
            == DEFAULT_APPEARANCE["build_type"],
            "posture": appearance["appearance"]["posture"]
            == DEFAULT_APPEARANCE["posture"],
        },
    }
