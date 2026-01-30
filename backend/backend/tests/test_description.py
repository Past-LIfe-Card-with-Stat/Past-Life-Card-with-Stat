# backend/tests/test_description.py

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 이제 import 가능
from backend.pipelines.generate_description import (
    explain_appearance,
    generate_description_for_model3,
)


def test_normal_case():
    """정상 케이스 테스트"""
    features = {
        "quality": {"person_detected": True, "pose_conf": 0.85},
        "pose": {
            "derived": {
                "stance_width": 1.35,
                "arms_open": 0.72,
                "body_lean": 0.18,
                "shoulder_tilt": 0.06,
            }
        },
        "tags": {"top": [{"tag": "warrior", "score": 0.8}]},
    }

    stats = {"STR": 28, "AGI": 15, "INT": 12, "CHA": 18, "VIT": 25, "LUK": 14}

    result = generate_description_for_model3(features, stats)

    print("Normal Case:")
    print(result)

    assert result["appearance"]["clothing_style"] is not None
    assert result["appearance"]["build_type"] is not None
    assert result["appearance"]["posture"] is not None


def test_empty_pose():
    """Pose 비어있는 경우"""
    features = {
        "quality": {"person_detected": False, "pose_conf": 0.0},
        "pose": {"derived": {}},
        "tags": {"top": []},
    }

    stats = {"STR": 10, "AGI": 10, "INT": 10, "CHA": 10, "VIT": 10, "LUK": 10}

    result = generate_description_for_model3(features, stats)

    print("\nEmpty Pose Case:")
    print(result)

    # 기본값 확인
    assert result["appearance"]["clothing_style"] == "casual"
    assert result["appearance"]["build_type"] == "average"
    assert result["appearance"]["posture"] == "neutral"


def test_with_occupation():
    """직업 지정된 경우"""
    features = {
        "quality": {"person_detected": True, "pose_conf": 0.8},
        "pose": {"derived": {"stance_width": 1.2, "arms_open": 0.5}},
        "tags": {"top": []},
    }

    stats = {"STR": 20, "AGI": 15, "INT": 12, "CHA": 15, "VIT": 18, "LUK": 12}

    result = generate_description_for_model3(
        features, stats, detected_occupation="knight"
    )

    print("\nWith Occupation Case:")
    print(result)

    assert result["appearance"]["clothing_style"] == "combat-ready"


def test_explanation():
    """설명 기능 테스트"""
    features = {
        "quality": {"person_detected": True, "pose_conf": 0.85},
        "pose": {
            "derived": {
                "stance_width": 1.1,
                "arms_open": 0.4,
                "body_lean": 0.05,
                "shoulder_tilt": 0.07,
            }
        },
        "tags": {"top": [{"tag": "standing", "score": 0.7}]},
    }

    stats = {"STR": 15, "AGI": 18, "INT": 20, "CHA": 22, "VIT": 16, "LUK": 14}

    result = explain_appearance(features, stats)

    print("\nExplanation:")
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_normal_case()
    test_empty_pose()
    test_with_occupation()
    test_explanation()
    print("\n✓ All tests passed!")
