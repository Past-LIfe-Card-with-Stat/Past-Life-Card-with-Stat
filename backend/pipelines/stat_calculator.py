def calculate_stats(features: dict) -> dict:
    stats = {"STR": 10, "AGI": 10, "INT": 10, "CHA": 10, "LUK": 10, "VIT": 10}

    pose = features.get("pose", {}).get("derived", {})
    tags = features.get("tags", {})
    equip = features.get("equipment", {})
    symbol = features.get("symbol", {})
    silhouette = features.get("silhouette", {})

    stats["AGI"] += int(pose.get("body_lean", 0) * 20)
    stats["AGI"] += int(pose.get("arms_open", 0) * 10)
    stats["STR"] += int(pose.get("stance_width", 0) * 5)
    stats["VIT"] += int(pose.get("shoulder_tilt", 0) * 50)

    top_tags = {t["tag"]: t["score"] for t in tags.get("top", [])}
    stats["CHA"] += int(top_tags.get("full-body portrait", 0) * 20)
    stats["LUK"] += int(top_tags.get("relaxed pose", 0) * 30)

    armor_map = {"none": 0, "cloth": 1, "leather": 2, "chain": 3, "plate": 4}
    stats["VIT"] += armor_map.get(equip.get("armor", "none"), 0) * 2

    weapon_map = {
        "none": 0,
        "sword": 3,
        "spear": 2,
        "bow": 2,
        "dagger": 3,
        "staff": 2,
        "tool": 1,
    }
    stats["STR"] += weapon_map.get(equip.get("main_item", "none"), 0)

    if equip.get("shield", False):
        stats["VIT"] += 2

    if symbol.get("cloak", False):
        stats["AGI"] += 1
    if symbol.get("emblem", False):
        stats["CHA"] += 1
    if symbol.get("religious_mark", False):
        stats["INT"] += 1
    ornament_map = {"low": 0, "medium": 2, "high": 4}
    stats["CHA"] += ornament_map.get(symbol.get("ornament_level", "low"), 0)

    bulk_map = {"light": 0, "medium": 2, "heavy": 4}
    mobility_map = {"low": 0, "medium": 2, "high": 4}
    stats["STR"] += bulk_map.get(silhouette.get("bulk", "medium"), 0)
    stats["AGI"] += mobility_map.get(silhouette.get("mobility", "medium"), 0)

    # max 50으로 제한
    for k in stats:
        stats[k] = max(1, min(50, stats[k]))

    return stats
