from services.character_generator import generate_character
from models.character_models import CharacterCardResponse

def run_example(name: str, sample_input: dict):
    print(f"\n--- Running Example: {name} ---")
    print("Running generation...")
    print("HF_TOKEN found. Attempting LLM generation...")

    character_card: CharacterCardResponse = generate_character(sample_input)

    print("=== Result ===")
    print(character_card.model_dump_json(indent=2))
    print("-" * (len(name) + 20))


# Example 1: High Strength, Low Intelligence (Warrior/Berserker)
# Expect: Combat-oriented, physical job/role
sample_input_1 = {
    "pose": {"left_hand": "axe", "right_hand": "none", "derived": {"stance_width": 1.5, "body_lean": 0.1, "arms_open": 0.2}},
    "tags": {"gender": "male", "hair_color": "brown", "muscular": 0.9, "fierce expression": 0.8},
    "description": {"text": "A hulking warrior, ready for battle."},
    "equipment": {"armor": "plate", "main_item": "axe", "shield": False},
    "silhouette": {"bulk": "heavy", "mobility": "low"}
}
run_example("High STR Warrior", sample_input_1)


# Example 2: High Intelligence, Low Strength (Mage/Scholar)
# Expect: Magic-oriented, intellectual job/role
sample_input_2 = {
    "pose": {"left_hand": "staff", "right_hand": "none", "derived": {"stance_width": 0.5, "body_lean": -0.3, "arms_open": 0.7}},
    "tags": {"gender": "female", "hair_color": "white", "wise expression": 0.9, "robes": 0.8},
    "description": {"text": "An ancient scholar with immense magical power."},
    "equipment": {"armor": "cloth", "main_item": "staff", "shield": False},
    "symbol": {"religious_mark": True, "ornament_level": "high"},
    "silhouette": {"bulk": "light", "mobility": "medium"}
}
run_example("High INT Mage", sample_input_2)


# Example 3: High Agility, Balanced other stats (Rogue/Scout)
# Expect: Agile, stealthy, combat job/role
sample_input_3 = {
    "pose": {"left_hand": "dagger", "right_hand": "none", "derived": {"stance_width": 0.7, "body_lean": 0.5, "arms_open": 0.6}},
    "tags": {"gender": "any", "hair_color": "black", "agile pose": 0.9, "hooded": 0.8},
    "description": {"text": "A nimble and elusive figure, moving through shadows."},
    "equipment": {"armor": "leather", "main_item": "dagger", "shield": False},
    "symbol": {"cloak": True},
    "silhouette": {"bulk": "medium", "mobility": "high"}
}
run_example("High AGI Rogue", sample_input_3)


# Example 4: Balanced Stats (Adventurer/Jack-of-all-trades)
# Expect: Generalist, versatile job/role
sample_input_4 = {
    "pose": {"left_hand": "sword", "right_hand": "shield", "derived": {"stance_width": 1.0, "body_lean": 0.0, "arms_open": 0.5}},
    "tags": {"gender": "male", "hair_color": "blonde", "determined expression": 0.7},
    "description": {"text": "A well-rounded adventurer, ready for anything."},
    "equipment": {"armor": "chain", "main_item": "sword", "shield": True},
    "silhouette": {"bulk": "medium", "mobility": "medium"}
}
run_example("Balanced Adventurer", sample_input_4)

# Example 5: High Charisma (Commander/Noble) - This was the problematic case before
# Expect: Leadership job/role
sample_input_5 = {
    "pose": {"left_hand": "none", "right_hand": "none", "derived": {"stance_width": 0.5, "body_lean": -0.1, "arms_open": 0.9}},
    "tags": {"gender": "female", "hair_color": "red", "regal": 0.9, "confident pose": 0.8, "full-body portrait": 0.9},
    "description": {"text": "A charismatic leader, inspiring her troops."},
    "equipment": {"armor": "none", "main_item": "none", "shield": False},
    "symbol": {"emblem": True, "ornament_level": "high"},
    "silhouette": {"bulk": "light", "mobility": "medium"}
}
run_example("High CHA Commander (Fixed Case)", sample_input_5)