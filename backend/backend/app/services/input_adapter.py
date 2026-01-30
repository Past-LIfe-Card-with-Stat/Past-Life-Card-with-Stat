from typing import Any, Dict


class InputAdapter:
    """
    Adapts the raw input from the vision/sensor system to the internal feature structure
    expected by the StatCalculator and the intent structure for LLM.
    """

    @staticmethod
    def to_internal_features(raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms raw input JSON into internal 'features' dictionary
        used by calculate_stats().
        """
        # 1. Base Structures (Direct Copy)
        pose = raw_input.get("pose", {})
        tags = raw_input.get("tags", {})
        
        # 2. Extract Description Info
        description = raw_input.get("description", {})
        appearance = description.get("appearance", {})

        clothing_style = appearance.get("clothing_style", "unknown").lower()
        build_type = appearance.get("build_type", "average").lower()
        posture_desc = appearance.get("posture", "neutral").lower()

        # 3. Map to Internal Structures for Stat Calculation
        equipment = InputAdapter._map_equipment(clothing_style)
        symbol = InputAdapter._map_symbol(clothing_style, tags)
        silhouette = InputAdapter._map_silhouette(build_type, posture_desc)

        return {
            "pose": pose,
            "tags": tags,
            "equipment": equipment,
            "symbol": symbol,
            "silhouette": silhouette,
        }

    @staticmethod
    def extract_intent(raw_input: Dict[str, Any]) -> Dict[str, str]:
        """
        Extracts the user's intended appearance from the raw input.
        """
        description = raw_input.get("description", {})
        appearance = description.get("appearance", {})

        return {
            "clothing_style": appearance.get("clothing_style", "adventurer gear"),
            "body_build": appearance.get("build_type", "average"),
            "posture_style": appearance.get("posture", "neutral")
        }

    @staticmethod
    def _map_equipment(clothing_style: str) -> Dict[str, Any]:
        """Maps clothing style to equipment stats."""
        equip = {"armor": "none", "main_item": "none", "shield": False}

        # Armor Mapping
        if "armor" in clothing_style or "plate" in clothing_style:
            equip["armor"] = "plate"
        elif "chain" in clothing_style or "mail" in clothing_style:
            equip["armor"] = "chain"
        elif "leather" in clothing_style or "ranger" in clothing_style:
            equip["armor"] = "leather"
        elif "ceremonial" in clothing_style or "robe" in clothing_style:
            equip["armor"] = "cloth"
        else:
            equip["armor"] = "cloth"  # Default

        if "warrior" in clothing_style or "knight" in clothing_style:
            equip["main_item"] = "sword"
        
        return equip

    @staticmethod
    def _map_symbol(clothing_style: str, tags: Dict[str, Any]) -> Dict[str, Any]:
        """Maps style and tags to symbolic items."""
        symbol = {
            "cloak": False,
            "emblem": False,
            "religious_mark": False,
            "ornament_level": "low"
        }

        # Ornament Level
        if "ceremonial" in clothing_style or "royal" in clothing_style:
            symbol["ornament_level"] = "high"
        elif "noble" in clothing_style:
            symbol["ornament_level"] = "medium"
        
        # Specific Symbols
        tag_list = [t.get("tag", "") for t in tags.get("top", [])]
        if "cloak" in tag_list or "cape" in clothing_style:
            symbol["cloak"] = True
        
        return symbol

    @staticmethod
    def _map_silhouette(build_type: str, posture_desc: str) -> Dict[str, Any]:
        """Maps build and posture to silhouette stats."""
        silhouette = {"bulk": "medium", "mobility": "medium"}

        # Bulk
        if build_type in ["lean", "slender", "thin"]:
            silhouette["bulk"] = "light"
        elif build_type in ["muscular", "heavy", "large"]:
            silhouette["bulk"] = "heavy"
        else:
            silhouette["bulk"] = "medium"

        # Mobility
        if "elegant" in posture_desc or "dynamic" in posture_desc:
            silhouette["mobility"] = "high"
        elif "rigid" in posture_desc or "heavy" in posture_desc:
            silhouette["mobility"] = "low"
        
        return silhouette
