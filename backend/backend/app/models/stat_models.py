from pydantic import BaseModel


class Stats(BaseModel):
    STR: int
    AGI: int
    INT: int
    CHA: int
    LUK: int
    VIT: int
