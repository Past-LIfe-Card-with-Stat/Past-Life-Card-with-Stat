from infer_identity_flavor import infer_identity_and_flavor
from backend.app.models.character_models import CharacterCardResponse, Identity, StatBar, UIStats
from stat_calculator import calculate_stats


class CharacterGenerator:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm

    def generate(self, features: dict) -> CharacterCardResponse:
        stats_dict = calculate_stats(features)

        if self.use_llm:
            identity_data = infer_identity_and_flavor(stats_dict)
            identity_info = identity_data.get("identity", {})
            job_title = identity_info.get("job_title", "알 수 없음")
            role = identity_info.get("role", "알 수 없음")
            flavor_text = identity_data.get("flavor_text", "")
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


def generate_character(features: dict, use_llm=True) -> CharacterCardResponse:
    generator = CharacterGenerator(use_llm=use_llm)
    return generator.generate(features)
