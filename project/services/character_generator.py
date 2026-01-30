from llm.llm_inferer import derive_role_constraints, infer_job_and_role, infer_flavor_text
from models.character_models import CharacterCardResponse, Identity, StatBar, UIStats
from services.input_adapter import InputAdapter
from services.stat_calculator import (
    calculate_stats,
    analyze_stat_profile,
    summarize_observed_appearance,
)


class CharacterGenerator:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm

    def generate(self, raw_input: dict) -> CharacterCardResponse:
        # 1. Adapt Input (Raw -> Internal Features)
        features = InputAdapter.to_internal_features(raw_input)

        # 2. Calculate Stats (Rule-based)
        stats_dict = calculate_stats(features)

        if self.use_llm:
            # 3. Prepare Context for LLM
            stat_profile = analyze_stat_profile(stats_dict)
            appearance_intent = InputAdapter.extract_intent(raw_input)
            appearance_observed = summarize_observed_appearance(features)

            llm_context = {
                "world": "medieval_fantasy",
                "appearance_intent": appearance_intent,
                "appearance_observed": appearance_observed,
                "stat_profile": stat_profile,
            }
            
            preferred_role_hint = stat_profile.get("preferred_role_hint")
            role_constraints = derive_role_constraints(
                stats_dict, appearance_observed, preferred_role_hint
            )

            # 4. Step 1: Infer Job & Role (Logical)
            identity_data = infer_job_and_role(llm_context, role_constraints)
            job_title = identity_data.get("job_title", "모험가")
            role = identity_data.get("role", "방랑자")

            # 5. Step 2: Infer Flavor Text (Creative)
            flavor_text = infer_flavor_text(job_title, role, appearance_observed)
        else:
            job_title = "암살자"
            role = "근접 공격수"
            flavor_text = "은밀하게 움직이며 치명적인 일격을 가한다."

        ui_stats = UIStats(
            STR=StatBar(value=stats_dict["STR"]),
            AGI=StatBar(value=stats_dict["AGI"]),
            INT=StatBar(value=stats_dict["INT"]),
            CHA=StatBar(value=stats_dict["CHA"]),
            LUK=StatBar(value=stats_dict["LUK"]),
            VIT=StatBar(value=stats_dict["VIT"]),
        )

        return CharacterCardResponse(
            identity=Identity(job_title=job_title, role=role),
            stats=ui_stats,
            flavor_text=flavor_text,
        )


def generate_character(raw_input: dict, use_llm=True) -> CharacterCardResponse:
    generator = CharacterGenerator(use_llm=use_llm)
    return generator.generate(raw_input)