# LLM Architecture & Prompt Engineering Report

## 1. Model Selection & Rationale

본 프로젝트는 캐릭터 생성의 정확성과 창의성을 극대화하기 위해 **Two-Stage Pipeline** 전략을 채택하였으며, 각 단계의 특성에 가장 적합한 모델을 선별하여 적용하였습니다.

### Stage 1: Logical Analysis & Classification
- **Model**: `Qwen/Qwen2.5-7B-Instruct`
- **Role**: 입력된 수치 데이터(스탯)와 메타 데이터(태그, 자세)를 분석하여 논리적으로 가장 타당한 **직업(Job)**과 **역할(Role)**을 추론합니다.
- **Why Qwen 2.5?**: 
    - 7B 파라미터 규모에서 **Coding 및 Logic/Math 성능**이 타 모델 대비 매우 우수합니다.
    - JSON 포맷을 엄격하게 준수하는 능력이 뛰어나, 시스템 간 데이터 연동(System-to-System)에 안정적입니다.
    - 복잡한 조건(의도 vs 관찰 불일치 등)을 해석하고 합리적인 결론을 도출하는 데 강점이 있습니다.

### Stage 2: Creative Writing & Storytelling
- **Model**: `meta-llama/Llama-3.1-8B-Instruct`
- **Role**: 확정된 직업/역할과 캐릭터의 외형 묘사를 바탕으로, 분위기 있는 **캐릭터 설명(Flavor Text)**을 생성합니다.
- **Why Llama 3.1?**:
    - **자연어 생성 및 문맥 이해 능력**이 탁월하여, 딱딱한 기계적 표현보다는 소설과 같은 매끄러운 문장을 잘 구사합니다.
    - 한국어 파인튜닝 모델이 아니더라도, Instruct 튜닝이 잘 되어 있어 자연스러운 한국어 작문이 가능합니다.
    - "판타지 소설가" 페르소나를 부여했을 때 톤앤매너(Tone & Manner) 조절이 유연합니다.

---

## 2. Pipeline Architecture

전체 캐릭터 생성 과정은 **[센서 데이터] → [룰 기반 연산] → [LLM 추론]** 순으로 진행됩니다.

```mermaid
graph TD
    UserInput[User Image Analysis Result] --> Adapter[InputAdapter]
    Adapter --> Features[Internal Features]
    Adapter --> Context[LLM Context Construction]
    
    Features --> Stats[StatCalculator]
    Stats --> BaseStats[STR/AGI/INT...]
    
    Stats --> Profile[Stat Profile Analysis]
    Profile --> Context
    
    subgraph "LLM Inference Pipeline"
        Context --> Qwen[Stage 1: Qwen 2.5]
        Qwen --> Identity[Job & Role (JSON)]
        
        Identity --> Llama[Stage 2: Llama 3.1]
        Context --> Llama
        Llama --> Flavor[Flavor Text (Korean)]
    end
    
    BaseStats --> FinalCard
    Identity --> FinalCard
    Flavor --> FinalCard
```

---

## 3. Prompt Engineering Flow

### Step 1: Context Preparation
LLM이 "단순 수치"가 아닌 "의미"를 이해하도록, Raw Data를 자연어에 가까운 문맥으로 변환합니다.

- **Appearance Intent (사용자 의도)**: `clothing_style`, `build_type` 등 사용자가 입력한 설정값.
- **Appearance Observed (관찰된 사실)**: 비전 AI가 분석한 `pose`, `tags`를 기반으로 해석한 값.
    - 예: `arms_open > 0.8` → "open and welcoming posture"
- **Stat Profile (능력치 분석)**: 계산된 스탯 중 가장 높은/낮은 능력치 추출.
    - 예: "High AGI, Low VIT" → "Speed-oriented, fragile"

### Step 2: Logical Inference (Qwen)
**System Persona**: `Game System Analyzer`
**Goal**: 데이터 간의 개연성을 판단하여 최적의 직업 부여.

> **Input Example**:
> - Intent: "Ceremonial armor" (사제/성기사 의도)
> - Observed: "Aggressive stance", "Sword" (전사적 특징)
> - Stats: High STR, Low INT
>
> **Reasoning**: 의도는 '의식용'이나, 실제 스탯과 자세는 '전투형'이므로 -> "성기사(Paladin)" 또는 "왕실 근위대(Royal Guard)"로 타협점 도출.

### Step 3: Creative Generation (Llama)
**System Persona**: `Fantasy Novelist`
**Goal**: 한 문장의 강렬한 묘사 생성.

> **Input**: Job="왕실 근위대장", Vibe="Serious", Posture="Upright"
> **Constraint**: "Exactly ONE core sentence", "Impactful"
>
> **Output**: "화려한 예식용 갑옷을 입고 있지만, 그 밑에 감춰진 날카로운 눈빛과 굳은살 박힌 손은 그가 실전에서 단련된 전사임을 말해줍니다."

---

## 4. Conclusion

이 구조는 **"데이터의 객관성"**과 **"표현의 창의성"**을 분리하여 관리합니다. 
스탯 계산은 100% 결정론적 알고리즘(Rule-based)을 따라 공정성을 보장하고, 직업 해석과 묘사는 LLM의 유연함을 활용하여 풍부한 사용자 경험을 제공합니다.