# tags.py
# 해커톤 MVP용: "유지/구도/분위기" 중심 태그 (중세 변환은 서현이 따로)
PRESERVE_TAGS = [
    # shot / composition
    "full-body portrait", "half-body portrait", "close-up portrait",
    "centered composition", "subject in the center",
    "upper body", "standing", "sitting",

    # pose / gesture
    "arms crossed", "hands on hips", "one hand raised",
    "hands clasped", "open arms", "relaxed pose",

    # face / vibe (가벼운 표현)
    "smiling", "serious face", "neutral expression",
    "confident vibe", "calm vibe",

    # photo quality
    "sharp photo", "blurry photo", "well-lit", "low light",
]

# 필요하면 팀에서 태그 확장하면 됨
ALL_TAGS = PRESERVE_TAGS
