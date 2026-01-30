import json
import os

from pathlib import Path

from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# Explicitly find and load the .env file to ensure HF_TOKEN is available.
# This makes the script runnable from any directory.
# backend/backend/pipelines -> backend/backend -> backend
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

HF_TOKEN = os.getenv("HF_TOKEN")

# Step 1: Logical Analysis (Qwen 2.5)
qwen_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    huggingfacehub_api_token=HF_TOKEN,
    temperature=0.3,
    max_new_tokens=300,
    timeout=120,  # 모델 cold start 대비 타임아웃 증가
)
qwen_llm = ChatHuggingFace(llm=qwen_endpoint)

# Step 2: Creative Writing (Llama 3.1)
llama_endpoint = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    huggingfacehub_api_token=HF_TOKEN,
    temperature=0.7,
    max_new_tokens=500,
    timeout=120,  # 모델 cold start 대비 타임아웃 증가
)
llama_llm = ChatHuggingFace(llm=llama_endpoint)


def _parse_json_response(response_text: str) -> dict:
    """Helper to parse JSON from LLM output, handling code blocks."""
    if not response_text:
        raise ValueError("Empty response from LLM")

    text = response_text.strip()
    # Remove markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Simple retry or fallback: try to find the first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Failed to parse JSON: {text}")


def infer_job_and_role(llm_context: dict, role_constraints: dict) -> dict:
    preferred_hint = role_constraints.get("preferred_role_hint")

    prompt = f"""
You are a Medieval Fantasy game system analyzer.

IMPORTANT CONSTRAINTS:
- Leadership roles are {"ALLOWED" if role_constraints["allow_leadership"] else "NOT ALLOWED"}.
- Frontline tank roles are {"ALLOWED" if role_constraints["allow_front_tank"] else "NOT ALLOWED"}.
{f"- Strong Role Preference: {preferred_hint}" if preferred_hint else ""}
- High-rank titles (e.g. 장군, 대장, 사령관, 군주) are {"ALLOWED" if role_constraints["allow_high_rank_titles"] else "NOT ALLOWED"}.

Job Title Domain Restriction:
- Allowed Domain: COMBAT or LEADERSHIP ONLY

COMBAT Job Titles include:
- 전사, 방패병, 광전사, 중갑병, 창병, 검투사, 기사, 성기사, 암살자, 궁수

LEADERSHIP Job Titles include:
- 지휘관, 대장, 기사단장, 길드장

SOCIAL or CULTURAL Titles are NOT ALLOWED:
- 장로, 족장, 수도원장, 현자, 군주, 왕

If a role is NOT ALLOWED, you MUST NOT assign it.
If a Strong Role Preference is given, you MUST prioritize it. It is the most important instruction.


Input Data:
{json.dumps(llm_context, indent=2)}

Task (Follow in order):

1. FIRST, check for a "Strong Role Preference". If it exists, it is your primary guide for the Job Title.
   - The Role should still be consistent with the stats (e.g., high CHA for leadership).

2. SECOND, if no hint exists, determine the Role strictly from stats and pose.
   - Ignore job titles at this step.
   - If CHA is low, avoid command/leadership.
   - If posture is closed or half-body, avoid frontline tank roles.

3. THIRD, choose a Job Class that fits the chosen Role and Hint.
   - Job must not exceed the scale implied by the Role.
   - Use ONLY Medieval Fantasy terminology from the provided lists.

Output (JSON only, Korean):
{{
  "job_title": "...",
  "role": "..."
}}

Respond with ONLY JSON.
"""

    messages = [HumanMessage(content=prompt)]
    try:
        response = qwen_llm.invoke(messages).content
        return _parse_json_response(response)
    except Exception as e:
        print(f"Qwen Error: {e}")
        return {"job_title": "모험가", "role": "자유로운 영혼"}


def infer_flavor_text(job_title: str, role: str, appearance_observed: dict) -> str:
    prompt = f"""
You are a fantasy novelist. Write a short, atmospheric flavor text for a character.

Character Info:
- Job: {job_title}
- Role: {role}
- Vibe: {appearance_observed.get('vibe')}
- Posture: {appearance_observed.get('posture')}

Pose Signals:
- body_lean: {appearance_observed.get('body_lean')}
- arms_open: {appearance_observed.get('arms_open')}
- stance_width: {appearance_observed.get('stance_width')}

Task:
Write exactly **ONE core sentence** in Korean that captures the essence of this character's appearance and aura.
Ensure it is concise, impactful, and descriptive.
- Do NOT imply large armies, command over groups, or grand battles
  unless the Role explicitly involves leadership.
- Do NOT use metaphorical objects or locations not implied by the input.
- Do NOT invent injuries, scars, or wounds unless explicitly stated.


Example:
"단단한 근육질의 몸체와 굳건한 자세에서 뿜어져 나오는 위압감은 그가 수많은 전장을 누벼온 베테랑임을 증명합니다."

Output:
Just the Korean text (one sentence). No JSON.
"""
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = llama_llm.invoke(messages).content.strip()
        # Clean up quotes
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        return response
    except Exception as e:
        print(f"Llama Error: {e}")
        return "알 수 없는 신비한 기운이 감도는 모험가입니다."
    

def derive_role_constraints(
    stats: dict, appearance_observed: dict, preferred_role_hint: str | None = None
) -> dict:
    constraints = {
        "allow_leadership": True,
        "allow_front_tank": True,
        "allow_high_rank_titles": False,
        "job_domain": "combat",
        "preferred_role_hint": preferred_role_hint,
    }

    # CHA 높고 -> 지휘 가능
    if stats.get("CHA", 0) >= 18:
        constraints["allow_leadership"] = True
        constraints["allow_high_rank_titles"] = True

    # INT 높으면 사회 직군 가능
    if stats.get("INT", 0) >= 18:
        constraints["job_domain"] = "social"

    # arms_open 낮거나 half-body → 전면 탱커 불가
    if appearance_observed.get("arms_open", 1) < 0.4:
        constraints["allow_front_tank"] = False

    return constraints