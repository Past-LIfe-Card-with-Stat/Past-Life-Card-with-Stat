from fastapi.testclient import TestClient
from main import app
import json
import os

client = TestClient(app)

def test_api_endpoint():
    # User provided input payload
    payload = {
      "quality": {
        "person_detected": True,
        "has_full_body": True,
        "pose_conf": 0.8966888189315796
      },
      "pose": {
        "bbox_norm": [
          0.37511757016181946,
          0.2633904218673706,
          0.6857571005821228,
          0.9582711458206177
        ],
        "derived": {
          "shoulder_tilt": 0.028505342760484994,
          "body_lean": 0.12159186043675733,
          "stance_width": 1.424453610453984,
          "arms_open": 1.3656002086553984
        }
      },
      "tags": {
        "top": [
          {
            "tag": "full-body portrait",
            "score": 0.3178461492061615
          },
          {
            "tag": "subject in the center",
            "score": 0.28673356771469116
          },
          {
            "tag": "standing",
            "score": 0.0814925879240036
          },
          {
            "tag": "sharp photo",
            "score": 0.043738141655921936
          },
          {
            "tag": "neutral expression",
            "score": 0.03890633210539818
          },
          {
            "tag": "centered composition",
            "score": 0.03578338027000427
          },
          {
            "tag": "relaxed pose",
            "score": 0.027043651789426804
          },
          {
            "tag": "half-body portrait",
            "score": 0.026274174451828003
          },
          {
            "tag": "sitting",
            "score": 0.02136201411485672
          },
          {
            "tag": "hands clasped",
            "score": 0.019684717059135437
          },
          {
            "tag": "calm vibe",
            "score": 0.017087608575820923
          },
          {
            "tag": "hands on hips",
            "score": 0.015374425798654556
          }
        ]
      },
      "description": {
        "appearance": {
          "clothing_style": "ceremonial",
          "build_type": "lean",
          "posture": "elegant"
        }
      }
    }

    print("Sending request to /character endpoint...")
    
    # Check if HF token is present to anticipate delay
    if os.getenv("HF_TOKEN"):
        print("HF_TOKEN found. Expecting LLM processing (this may take a few seconds)...")
    else:
        print("HF_TOKEN NOT found. Using fallback logic (fast response).")

    response = client.post("/character", json=payload)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("\n=== API Response ===")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("\n=== Error ===")
        print(response.text)

if __name__ == "__main__":
    test_api_endpoint()
