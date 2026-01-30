# backend/pipelines/stat_calculator.py


def calculate_stats(features: dict) -> dict:
    """
    이미지 features로부터 RPG 스탯 계산

    사용 데이터:
    - pose.derived: 자세 메트릭 (stance_width, arms_open, body_lean, shoulder_tilt)
    - tags.top: CLIP 기반 이미지 태그 리스트
    - quality: 포즈 감지 품질

    Args:
        features: extract_features_pipeline.main() 출력

    Returns:
        {"STR": int, "AGI": int, "INT": int, "CHA": int, "LUK": int, "VIT": int}
        각 스탯은 1~50 범위
    """
    # 기본값
    stats = {
        "STR": 10,  # Strength (힘)
        "AGI": 10,  # Agility (민첩)
        "INT": 10,  # Intelligence (지능)
        "CHA": 10,  # Charisma (매력)
        "LUK": 10,  # Luck (행운)
        "VIT": 10,  # Vitality (체력)
    }

    # ===== 1. Pose Derived Metrics 기반 스탯 =====
    pose_derived = features.get("pose", {}).get("derived", {})

    # stance_width: 발목 간 거리 / 골반 너비
    stance_width = pose_derived.get("stance_width", 0.0)
    if stance_width > 1.3:
        # 넓은 자세 → 힘과 안정성
        stats["STR"] += 5
        stats["VIT"] += 3
    elif stance_width > 1.0:
        stats["STR"] += 2
        stats["VIT"] += 1
    elif stance_width < 0.8:
        # 좁은 자세 → 민첩성
        stats["AGI"] += 3

    # arms_open: 손목 간 거리 / 어깨 너비
    arms_open = pose_derived.get("arms_open", 0.0)
    if arms_open > 0.7:
        # 팔을 크게 벌림 → 카리스마와 민첩성
        stats["CHA"] += 5
        stats["AGI"] += 4
    elif arms_open > 0.5:
        stats["CHA"] += 3
        stats["AGI"] += 2
    elif arms_open < 0.3:
        # 팔을 몸에 붙임 → 신중함 (지능)
        stats["INT"] += 3

    # body_lean: 상체 기울기
    body_lean = pose_derived.get("body_lean", 0.0)
    if body_lean > 0.15:
        # 앞으로 기울임 → 역동적, 민첩
        stats["AGI"] += 4
        stats["STR"] += 2
    elif body_lean > 0.08:
        stats["AGI"] += 2

    # shoulder_tilt: 어깨 기울기
    shoulder_tilt = pose_derived.get("shoulder_tilt", 0.0)
    if shoulder_tilt < 0.08:
        # 어깨가 수평 → 안정적
        stats["VIT"] += 3
    elif shoulder_tilt > 0.15:
        # 어깨가 기울어짐 → 역동적이지만 불안정
        stats["AGI"] += 2
        stats["VIT"] -= 1

    # ===== 2. Tags 기반 스탯 =====
    tags_list = features.get("tags", {}).get("top", [])

    # 태그를 딕셔너리로 변환 (소문자)
    tags_dict = {t["tag"].lower(): t["score"] for t in tags_list}

    # 키워드 기반 스탯 매핑
    tag_keywords = {
        # 힘 관련
        "STR": ["strong", "powerful", "muscular", "warrior", "fighter", "athletic"],
        # 민첩 관련
        "AGI": [
            "agile",
            "quick",
            "fast",
            "dynamic",
            "active",
            "running",
            "jumping",
            "flexible",
        ],
        # 지능 관련
        "INT": [
            "intelligent",
            "wise",
            "thoughtful",
            "scholar",
            "reading",
            "studying",
            "contemplative",
        ],
        # 매력 관련
        "CHA": [
            "charismatic",
            "elegant",
            "confident",
            "portrait",
            "stylish",
            "attractive",
            "charming",
        ],
        # 행운 관련
        "LUK": [
            "relaxed",
            "happy",
            "casual",
            "peaceful",
            "fortunate",
            "smiling",
            "cheerful",
        ],
        # 체력 관련
        "VIT": ["healthy", "robust", "sturdy", "standing", "stable", "balanced"],
    }

    # 각 스탯별로 키워드 매칭
    for stat, keywords in tag_keywords.items():
        for tag, score in tags_dict.items():
            for keyword in keywords:
                if keyword in tag:
                    # score는 0~1 사이 값, 최대 10점까지 추가
                    bonus = int(score * 10)
                    stats[stat] += bonus
                    break  # 같은 태그는 한 번만 카운트

    # 특정 태그 직접 매칭 (동료 코드 호환성)
    if "full-body portrait" in tags_dict:
        stats["CHA"] += int(tags_dict["full-body portrait"] * 15)

    if "relaxed pose" in tags_dict:
        stats["LUK"] += int(tags_dict["relaxed pose"] * 20)

    # ===== 3. Quality 기반 보정 =====
    quality = features.get("quality", {})

    # 전신 사진 감지 → 전체 스탯 소폭 상승
    if quality.get("has_full_body", False):
        for stat_key in stats:
            stats[stat_key] += 2

    # 포즈 신뢰도가 높으면 → VIT, LUK 보너스
    pose_conf = quality.get("pose_conf", 0.0)
    if pose_conf > 0.85:
        stats["VIT"] += 4
        stats["LUK"] += 3
    elif pose_conf > 0.7:
        stats["VIT"] += 2
        stats["LUK"] += 1
    elif pose_conf < 0.5:
        # 포즈 신뢰도가 낮으면 스탯 감소
        stats["VIT"] -= 2

    # 사람이 감지되지 않은 경우 → 모든 스탯 패널티
    if not quality.get("person_detected", False):
        for stat_key in stats:
            stats[stat_key] = max(1, stats[stat_key] - 5)

    # ===== 4. 밸런싱: 1~50 범위로 제한 =====
    for key in stats:
        stats[key] = max(1, min(50, stats[key]))

    return stats


# ===== 테스트/디버깅용 함수 =====
def explain_stats(features: dict) -> dict:
    """
    스탯 계산 과정을 상세히 설명 (디버깅용)

    Returns:
        {
            "stats": {...},
            "breakdown": {
                "pose_contributions": {...},
                "tag_contributions": {...},
                "quality_bonus": {...}
            }
        }
    """
    breakdown = {"pose_contributions": {}, "tag_contributions": {}, "quality_bonus": {}}

    # 기본 스탯
    stats = {"STR": 10, "AGI": 10, "INT": 10, "CHA": 10, "LUK": 10, "VIT": 10}

    # Pose 분석
    pose_derived = features.get("pose", {}).get("derived", {})
    stance_width = pose_derived.get("stance_width", 0.0)
    arms_open = pose_derived.get("arms_open", 0.0)
    body_lean = pose_derived.get("body_lean", 0.0)
    shoulder_tilt = pose_derived.get("shoulder_tilt", 0.0)

    breakdown["pose_contributions"] = {
        "stance_width": {
            "value": round(stance_width, 3),
            "description": "넓은 자세"
            if stance_width > 1.3
            else ("좁은 자세" if stance_width < 0.8 else "보통"),
            "stats_affected": [],
        },
        "arms_open": {
            "value": round(arms_open, 3),
            "description": "팔 벌림"
            if arms_open > 0.6
            else ("팔 모음" if arms_open < 0.3 else "보통"),
            "stats_affected": [],
        },
        "body_lean": {
            "value": round(body_lean, 3),
            "description": "앞으로 기울임" if body_lean > 0.15 else "안정적",
            "stats_affected": [],
        },
        "shoulder_tilt": {
            "value": round(shoulder_tilt, 3),
            "description": "수평" if shoulder_tilt < 0.08 else "기울어짐",
            "stats_affected": [],
        },
    }

    # 실제 계산 (위의 calculate_stats 로직과 동일)
    final_stats = calculate_stats(features)

    return {
        "stats": final_stats,
        "breakdown": breakdown,
        "features_summary": {
            "pose_confidence": features.get("quality", {}).get("pose_conf", 0.0),
            "has_full_body": features.get("quality", {}).get("has_full_body", False),
            "top_tags": [t["tag"] for t in features.get("tags", {}).get("top", [])[:3]],
        },
    }
