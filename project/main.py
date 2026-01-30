from typing import Any, Dict, Optional

from fastapi import FastAPI
from models.character_models import CharacterCardResponse
from pydantic import BaseModel
from services.character_generator import generate_character

app = FastAPI()


class CharacterInput(BaseModel):
    pose: Dict[str, Any]
    tags: Dict[str, Any]
    description: Optional[Dict[str, Any]] = {}
    quality: Optional[Dict[str, Any]] = {}


@app.post("/character", response_model=CharacterCardResponse)
def create_character(input_data: CharacterInput):
    # Convert Pydantic model to dict
    raw_input = input_data.model_dump()
    return generate_character(raw_input)
