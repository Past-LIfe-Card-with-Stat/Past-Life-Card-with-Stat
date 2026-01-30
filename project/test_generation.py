import os
import sys

# Ensure 'project' directory is in path if running from inside project/ or outside
sys.path.append(os.getcwd())

from services.character_generator import generate_character
import json

def test_run():
    features = {
        "pose": {
            "derived": {
                "body_lean": 0.1, 
                "arms_open": 0.2, 
                "stance_width": 0.8,
                "shoulder_tilt": 0.1
            }
        },
        "tags": {
            "top": [
                {"tag": "full-body portrait", "score": 0.95},
                {"tag": "warrior", "score": 0.8}
            ]
        },
        "equipment": {
            "armor": "plate", 
            "main_item": "sword", 
            "shield": True
        },
        "symbol": {
            "cloak": True,
            "emblem": True,
            "ornament_level": "high"
        },
        "silhouette": {
            "bulk": "heavy", 
            "mobility": "low"
        }
    }

    print("Running generation...")
    try:
        # Mocking LLM to avoid API calls if we just want to test logic flow? 
        # Actually, let's try with use_llm=False first to check wiring, then True if env is set.
        # But wait, the user wants me to implement the changes, likely the API keys are set in the environment.
        # I will try use_llm=True but catch errors if key is missing.
        
        # Check if HF_TOKEN is set
        if not os.getenv("HF_TOKEN"):
             print("Warning: HF_TOKEN not set. Running with use_llm=False")
             result = generate_character(features, use_llm=False)
        else:
             print("HF_TOKEN found. Attempting LLM generation...")
             result = generate_character(features, use_llm=True)
        
        print("\n=== Result ===")
        print(result.model_dump_json(indent=2))
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_run()
