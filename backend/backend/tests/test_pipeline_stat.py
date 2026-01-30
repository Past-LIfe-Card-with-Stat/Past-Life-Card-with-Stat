import os
import sys
import json

# Ensure 'project' directory is in path
sys.path.append(os.getcwd())

from services.character_generator import generate_character

def test_full_pipeline():
    raw_input = {
      "quality": {
        "person_detected": True,
        "has_full_body": True,
        "pose_conf": 0.89
      },
      "pose": {
        "bbox_norm": [0.3, 0.2, 0.6, 0.9],
        "derived": {
          "shoulder_tilt": 0.02,
          "body_lean": 0.12,
          "stance_width": 1.4,  # High -> Wide stance
          "arms_open": 1.3      # High -> Open/Expressive
        }
      },
      "tags": {
        "top": [
          {"tag": "full-body portrait", "score": 0.3},
          {"tag": "standing", "score": 0.08},
          {"tag": "calm vibe", "score": 0.01},
          {"tag": "hands on hips", "score": 0.015}
        ]
      },
      "description": {
        "appearance": {
          "clothing_style": "ceremonial armor",
          "build_type": "lean",
          "posture": "elegant"
        }
      }
    }

    print("Running full pipeline test...")
    
    use_llm = bool(os.getenv("HF_TOKEN"))
    if not use_llm:
        print("Warning: HF_TOKEN not set. Running in mock mode.")
    else:
        print("HF_TOKEN found. Running with LLM.")

    try:
        result = generate_character(raw_input, use_llm=use_llm)
        print("\n=== Generated Character ===")
        print(result.model_dump_json(indent=2))
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_pipeline()
