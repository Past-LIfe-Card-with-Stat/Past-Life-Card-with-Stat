def calculate_stats(features: dict) -> dict:
    stats = {"STR": 10, "AGI": 10, "INT": 10, "CHA": 10, "LUK": 10, "VIT": 10}

    pose = features.get("pose", {}).get("derived", {})
    tags = features.get("tags", {})
    equip = features.get("equipment", {})
    symbol = features.get("symbol", {})
    silhouette = features.get("silhouette", {})

    # -----------------------
    # Pose 기반 스탯
    # -----------------------
    body_lean = pose.get("body_lean", 0)
    arms_open = pose.get("arms_open", 0)
    stance_width = pose.get("stance_width", 0)

    # AGI 쏠림 완화
    stats["AGI"] += int(body_lean * 12)
    stats["AGI"] += int(arms_open * 6)
    stats["CHA"] += int(arms_open * 4)

    stats["STR"] += int(stance_width * 5)
    stats["VIT"] += int(stance_width * 3)

    # -----------------------
    # Tag 기반 보정
    # -----------------------
    top_tags = {t["tag"]: t["score"] for t in tags.get("top", [])}

    stats["CHA"] += int(top_tags.get("full-body portrait", 0) * 20)
    stats["LUK"] += int(top_tags.get("relaxed pose", 0) * 30)

    # -----------------------
    # 장비 기반 보정
    # -----------------------
    armor_map = {"none": 0, "cloth": 1, "leather": 2, "chain": 3, "plate": 4}
    stats["VIT"] += armor_map.get(equip.get("armor", "none"), 0) * 2

    weapon_map = {
        "none": 0,
        "sword": 3,
        "dagger": 3,
        "spear": 2,
        "bow": 2,
        "staff": 2,
        "tool": 1,
    }
    stats["STR"] += weapon_map.get(equip.get("main_item", "none"), 0)

    if equip.get("shield", False):
        stats["VIT"] += 2

    # -----------------------
    # 상징 요소
    # -----------------------
    if symbol.get("cloak", False):
        stats["AGI"] += 1
    if symbol.get("emblem", False):
        stats["CHA"] += 1
    if symbol.get("religious_mark", False):
        stats["INT"] += 1

    ornament_map = {"low": 0, "medium": 2, "high": 4}
    stats["CHA"] += ornament_map.get(symbol.get("ornament_level", "low"), 0)

    # -----------------------
    # 실루엣 기반
    # -----------------------
    bulk = silhouette.get("bulk", "medium")
    mobility = silhouette.get("mobility", "medium")

    bulk_map_str = {"light": 0, "medium": 2, "heavy": 4}
    bulk_map_vit = {"light": 0, "medium": 1, "heavy": 3}
    mobility_map = {"low": 0, "medium": 2, "high": 4}

    stats["STR"] += bulk_map_str.get(bulk, 0)
    stats["VIT"] += bulk_map_vit.get(bulk, 0)
    stats["AGI"] += mobility_map.get(mobility, 0)

    # -----------------------
    # VIT 정체성 트리거
    # -----------------------
    if stance_width > 1.2 and bulk == "heavy":
        stats["VIT"] += 3

    # -----------------------
    # 스탯 범위 제한
    # -----------------------
    for k in stats:
        stats[k] = max(1, min(50, stats[k]))

    return stats



def analyze_stat_profile(stats: dict) -> dict:
    sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
    dominant = [k for k, _ in sorted_stats[:2]]
    weak = [k for k, _ in sorted_stats[-1:]]
    highest_stat, highest_val = sorted_stats[0]

    # 조합 기반 전투 스타일
    dominant_set = set(dominant)

    preferred_role_hint = None
    if highest_stat == "CHA" and highest_val > 25:
        preferred_role_hint = "Primary role is a leader, commander, or noble. Combat is secondary. Prioritize job titles like '기사', '성기사', '지휘관', '귀족'."
    elif highest_stat == "INT" and highest_val > 25:
        preferred_role_hint = "Primary role is a strategist, mage, or scholar. Combat is secondary. Prioritize job titles like '마법사', '학자', '전략가'."
    elif {"STR", "VIT"} <= dominant_set:
        preferred_role_hint = "This is a frontline bruiser. Prioritize job titles like '전사', '광전사', '방패병'."

    if {"STR", "VIT"} <= dominant_set:
        combat_style = "frontline bruiser"
    elif {"AGI", "VIT"} <= dominant_set:
        combat_style = "mobile tank"
    elif {"AGI", "STR"} <= dominant_set:
        combat_style = "skirmisher"
    elif {"INT", "CHA"} <= dominant_set:
        combat_style = "tactical support"
    elif "INT" in dominant_set:
        combat_style = "magic-based"
    elif "CHA" in dominant_set:
        combat_style = "leadership/support"
    else:
        combat_style = "balanced"

    survivability_score = stats.get("VIT", 0) + stats.get("AGI", 0)
    if survivability_score > 60:
        survivability = "high"
    elif survivability_score > 30:
        survivability = "medium"
    else:
        survivability = "low"

    return {
        "dominant": dominant,
        "weak": weak,
        "combat_style": combat_style,
        "survivability": survivability,
        "preferred_role_hint": preferred_role_hint
    }

def summarize_observed_appearance(features: dict) -> dict:
    pose = features.get("pose", {}).get("derived", {})
    tags = features.get("tags", {})
    top_tags = [t["tag"] for t in tags.get("top", [])]

    # 1. Posture & Stance (from Pose)
    body_lean = pose.get("body_lean", 0)
    arms_open = pose.get("arms_open", 0)
    stance_width = pose.get("stance_width", 0)

    # Posture interpretation
    if body_lean > 0.2:
        lean_desc = "leaning"
    elif body_lean < -0.2:
        lean_desc = "leaning back"
    else:
        lean_desc = "upright"

    if arms_open > 0.8:
        openness = "open"
    elif arms_open < 0.3:
        openness = "closed/guarded"
    else:
        openness = "neutral"
    
    posture = f"{openness} and {lean_desc}"

    # Stance interpretation
    if stance_width > 0.8:
        stance = "wide and stable"
    elif stance_width < 0.3:
        stance = "narrow"
    else:
        stance = "balanced"

    # 2. Gesture & Vibe (from Tags & Pose)
    gesture = "neutral"
    if "hands clasped" in top_tags:
        gesture = "polite/clasped hands"
    elif "hands on hips" in top_tags:
        gesture = "confident/hands on hips"
    elif arms_open > 1.0:
        gesture = "expressive/expansive"

    vibe = "neutral"
    if "calm vibe" in top_tags or "relaxed pose" in top_tags:
        vibe = "calm"
    elif "smile" in top_tags or "happy" in top_tags:
        vibe = "cheerful"
    elif "serious" in top_tags or "stern" in top_tags:
        vibe = "serious"
    
    # 3. Composition
    composition = "standard"
    if "full-body portrait" in top_tags:
        composition = "full-body centered"
    elif "half-body portrait" in top_tags:
        composition = "half-body focus"

    return {
        "posture": posture,
        "stance": stance,
        "gesture": gesture,
        "vibe": vibe,
        "composition": composition
    }