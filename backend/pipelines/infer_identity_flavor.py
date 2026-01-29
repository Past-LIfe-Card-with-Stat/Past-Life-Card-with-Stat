import json
import os

from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

base_llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    huggingfacehub_api_token=HF_TOKEN,
    temperature=0.35,
    max_new_tokens=500,
)

llm = ChatHuggingFace(llm=base_llm)


def infer_identity_and_flavor(stats: dict) -> dict:
    prompt = f"""
Medieval fantasy RPG character.
Stats: {stats}

You are a fantasy RPG character generator for a medieval setting.
Your task is to generate only the following JSON output in Korean:

{{
    "identity": {{
        "job_title": "A short, fantasy-style job title in Korean (e.g., '검술사', '마법사', '도적')",
        "role": "Character role, concise, in Korean (e.g., '근접 공격수', '마법사', '원거리 지원')"
    }},
    "flavor_text": "A short, atmospheric description in Korean"
}}

Rules:
1. Do not calculate stats; ignore them. Stats are handled elsewhere.
2. Focus on fantasy flavor for job_title and role.
3. flavor_text should capture the character's mood, style, and appearance.
4. flavor_text must be a natural, grammatically correct Korean sentence.
5. flavor_text length: 1~2 sentences.
6. Output must be valid JSON.
7. Output must be in **Korean**.

Example Output:
{{
    "identity": {{
        "job_title": "검술사",
        "role": "근접 공격수"
    }},
    "flavor_text": "어두운 숲 속에서 칼날을 번뜩이며 적을 노리는 날렵한 전사."
}}

Output JSON:
Please respond with ONLY valid JSON in the above format. No extra text.
"""

    messages = [HumanMessage(content=prompt)]
    generated_text = llm.invoke(messages).content
    print("LLM OUTPUT:", generated_text)

    if not generated_text:
        raise ValueError("LLM에서 아무 값도 반환하지 않았습니다.")

    try:
        data = json.loads(generated_text)
    except json.JSONDecodeError:
        raise ValueError(f"LLM 출력이 JSON이 아닙니다: {generated_text}")

    return data
