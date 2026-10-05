<<<<<<< HEAD
# 🎬 CineForge

**AI Film Pre-Production Factory**

CineForge transforms a screenplay into a complete, validated production plan using five specialized AI agents that collaborate through structured data.

---

## Problem

Film pre-production requires breaking down a screenplay into scenes, planning shots, creating a shooting schedule, estimating budgets, and checking for consistency — all interconnected tasks that are traditionally manual, time-consuming, and error-prone.

## Solution

CineForge automates this workflow using a pipeline of five AI agents, each specialized for a specific pre-production task. The agents share structured data, enabling genuine multi-agent collaboration with traceability from every budget line item back to the original screenplay.

---

## Agent Architecture

```
📄 Screenplay PDF
       ↓
🎭 Script Analyst    → ScriptAnalysis (scenes, characters, locations, props)
       ↓
🎥 Shot Planner      → ShotPlan (shots with camera, equipment, rationale)
       ↓
📅 Production Planner → ProductionSchedule (shoot days, times, locations)
       ↓
💰 Budget Agent      → Budget (line items, subtotal, contingency, total)
       ↓
🧪 Consistency Agent → ValidationResult (PASS or issues with suggested fixes)
       ↓
🔧 Manager           → PASS → Final Plan | FAIL → Repair → Revalidate
```

### Repair Loop

If the Consistency Agent finds issues, the Manager (deterministic Python orchestration) routes the problem back to the responsible agent for repair. Maximum 3 repair attempts before flagging for human review.

---

## Workflow

1. **Upload** a screenplay PDF
2. **Extract** text using PyMuPDF
3. **Analyze** — Script Analyst extracts scenes, characters, locations
4. **Plan Shots** — Shot Planner creates cinematic coverage
5. **Schedule** — Production Planner creates a shooting schedule
6. **Budget** — Python calculates costs from a rate card
7. **Validate** — Deterministic validators + AI Consistency Agent
8. **Repair** — If issues found, responsible agent fixes and re-validates
9. **Download** — Export the full production package as Markdown

---

## Project Structure

```
cineforge/
├── app.py              # Streamlit UI
├── pipeline.py         # Orchestration & repair loop
├── agents.py           # 5 AI agent definitions
├── schemas.py          # Pydantic models (shared contracts)
├── prompts.py          # System prompts for each agent
├── tools.py            # PDF extraction, budget calc, rate card
├── validators.py       # Deterministic validation (no LLM)
├── create_demo_pdf.py  # Demo screenplay generator
├── requirements.txt    # Dependencies
├── .env.example        # Environment variable template
├── .gitignore
├── README.md
├── sample_data/
│   └── demo_screenplay.pdf
└── outputs/
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| AI Framework | LangChain + OpenAI |
| Data Models | Pydantic v2 |
| PDF Extraction | PyMuPDF |
| UI | Streamlit |
| Budget Arithmetic | Python (never LLM) |
| Config | python-dotenv |

---

## Setup

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Generate demo screenplay (optional)

```bash
python create_demo_pdf.py
```

### 4. Run the application

```bash
streamlit run app.py
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model name |

---

## Demo Workflow

1. Upload `sample_data/demo_screenplay.pdf` (or any screenplay PDF)
2. Click **Generate Production Plan**
3. Watch the five agents execute sequentially
4. The demo screenplay includes a **deliberate conflict**: Sarah is unavailable after 17:00, but Scene 7 (requiring Sarah) gets scheduled at 18:00
5. The Consistency Agent detects the **ACTOR_CONFLICT**
6. The Manager routes repair to the **Production Planner**
7. Production Planner reschedules Scene 7
8. Consistency Agent re-validates → **PASS**
9. Download the final production report

---

## Key Design Decisions

- **Structured data between agents** — No giant string passing. Each agent produces typed Pydantic objects.
- **Python handles arithmetic** — Budget calculations, schedule capacity checks, and reference validation are deterministic Python, never LLM.
- **Dual validation** — Deterministic validators catch factual errors; AI Consistency Agent catches higher-level production logic issues.
- **Traceable pipeline** — Every shot traces back to a scene, every schedule entry to a scene and shots, every budget item to the schedule.

---

## Future Improvements

- [ ] PDF export with professional formatting
- [ ] LLM-based Manager agent for smarter repair routing
- [ ] Timeline visualization with drag-and-drop
- [ ] Multiple screenplay format support (Final Draft, Fountain)
- [ ] Cost charts and budget breakdowns
- [ ] Location map integration
- [ ] Weather-aware exterior scheduling
- [ ] Multi-project management

---

*Built for hackathon demonstration — CineForge: An AI production office for independent filmmakers.*
=======
# ciniforge
>>>>>>> 32d061a05e6bea96f0beff1dbb66665c9d5d9234
