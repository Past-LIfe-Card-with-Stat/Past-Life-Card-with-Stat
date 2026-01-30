from typing import Optional

from pydantic import BaseModel


class StatBar(BaseModel):
    value: int
    max: int = 50


class UIStats(BaseModel):
    STR: StatBar
    AGI: StatBar
    INT: StatBar
    CHA: StatBar
    LUK: StatBar
    VIT: StatBar


class Identity(BaseModel):
    job_title: str
    role: str


class CharacterCardResponse(BaseModel):
    identity: Identity
    stats: Optional[UIStats] = None
    flavor_text: str
