from pathlib import Path

capsule = """# Hackathon Context — Film Production Factory

## Project Overview

The project is a **Film Production Factory** that converts a screenplay into a connected film pre-production plan.

The system uses six specialized agents:

1. Script Analyst Agent
2. Shot Planner Agent
3. Production Planner Agent
4. Budget Agent
5. Consistency Agent
6. Manager Agent

The goal is to demonstrate agents collaborating on a real production workflow rather than producing disconnected pieces of AI-generated text.

---

## Complete Workflow

The high-level pipeline is:

Screenplay
→ Script Analyst
→ Shot Planner
→ Production Planner
→ Budget Agent
→ Consistency Agent
→ Manager
→ Final Production Plan

If the Consistency Agent detects problems, the Manager initiates a repair loop:

Consistency Agent
→ Manager
→ relevant specialist agent
→ updated output
→ Consistency Agent
→ PASS
→ Final Production Plan

---

## Agent Responsibilities

### 1. Script Analyst Agent

Input:
- Uploaded screenplay, usually PDF
- Extracted screenplay text

Responsibilities:
- Extract scenes
- Identify scene numbers
- Identify INT/EXT
- Identify locations
- Identify time of day
- Identify characters
- Identify props
- Identify important production elements
- Preserve screenplay page references

Output:
- Structured ScriptAnalysis object

Example entities:
- Scene
- Character
- Location
- Prop

Important rule:
The agent should not invent screenplay facts. It should distinguish explicit information from reasonable inference.

---

### 2. Shot Planner Agent

Input:
- Structured ScriptAnalysis from Script Analyst

Responsibilities:
- Generate practical shot coverage for every scene
- Determine shot type
- Determine camera angle
- Determine camera movement
- Identify subjects
- Identify required equipment
- Estimate setup time
- Explain the rationale for each shot

Output:
- Structured ShotPlan

Important rule:
Shot recommendations are production suggestions and should not be presented as if they were explicitly written in the screenplay.

Every shot must reference a valid scene_id.

---

### 3. Production Planner Agent

Input:
- ScriptAnalysis
- ShotPlan
- Actor availability
- Location availability
- Other production constraints

Responsibilities:
- Convert scenes and shot requirements into a practical shooting schedule
- Group scenes by location where practical
- Consider actor availability
- Consider location availability
- Consider time of day
- Consider estimated scene duration
- Consider shot setup time
- Consider daily working limits
- Consider company moves

Output:
- Structured ProductionSchedule

Important rule:
Do not schedule scenes when required actors are unavailable.
Do not schedule beyond the allowed daily production capacity.
Every scheduled scene must reference a valid scene_id.

---

### 4. Budget Agent

Input:
- ScriptAnalysis
- ShotPlan
- ProductionSchedule
- Rate card / production resource costs

Responsibilities:
- Estimate equipment costs
- Estimate location costs
- Estimate crew costs
- Estimate transport
- Estimate catering
- Estimate other production resources
- Produce line-item budget
- Calculate subtotal
- Calculate contingency
- Calculate total

Output:
- Structured Budget

Important rule:
Use supplied rate-card values where available.
Do not invent arbitrary prices when a known rate is available.
Arithmetic should be calculated and verified by Python rather than relying on the LLM.

---

### 5. Consistency Agent

Input:
- Complete ScriptAnalysis
- ShotPlan
- ProductionSchedule
- Budget

Responsibilities:
- Check the complete production plan
- Find missing scenes
- Find missing shots
- Check actor availability conflicts
- Check location conflicts
- Check time-of-day conflicts
- Check equipment conflicts
- Check impossible schedules
- Check budget inconsistencies
- Check broken entity references
- Check unsupported assumptions

Output:
- Structured ValidationResult

The agent should report:
- severity
- category
- message/evidence
- affected scene IDs
- suggested correction

If no problems exist:
status = PASS

The Consistency Agent should not rewrite the entire plan. It should identify specific issues.

---

### 6. Manager Agent

The Manager controls the workflow.

Responsibilities:
- Decide which specialist should run
- Pass the correct structured data to the correct specialist
- Inspect Consistency Agent results
- Decide whether the plan passes
- Decide whether a repair is needed
- Identify which agent should repair the problem
- Trigger the repair
- Send the repaired result back through validation

Conceptually:

Manager
→ route task
→ specialist
→ output
→ Consistency Agent
→ Manager
→ PASS or REPAIR

For the initial MVP, the Manager can be implemented as deterministic Python orchestration in `pipeline.py`. A true LLM-based Manager/router can be added later.

---

# Architecture

The initial architecture should remain simple and similar to the reference multi-agent research project.

Core files:

film-production-factory/
├── app.py
├── pipeline.py
├── agents.py
├── tools.py
├── schemas.py
├── prompts.py
├── validators.py
├── requirements.txt
├── .env
├── .gitignore
├── sample_data/
│   └── demo_screenplay.pdf
└── outputs/

---

## app.py

Purpose:
- Streamlit user interface
- Screenplay upload
- Show pipeline progress
- Display scenes
- Display shot list
- Display schedule
- Display budget
- Display consistency issues
- Allow final production plan/report download

The UI should visually communicate the agent pipeline:

🎬 Screenplay uploaded
↓
🎭 Script Analyst
↓
🎥 Shot Planner
↓
📅 Production Planner
↓
💰 Budget Agent
↓
🧪 Consistency Agent
↓
🔧 Repair if needed
↓
✅ Production Plan Ready

---

## pipeline.py

Purpose:
- Main orchestration layer
- Execute agents in order
- Pass structured outputs between stages
- Invoke deterministic validators
- Invoke Consistency Agent
- Implement repair loop
- Return final production plan

Main function:

run_pipeline(file_path)

Initial execution:

1. Extract screenplay text
2. Run Script Analyst
3. Run Shot Planner
4. Run Production Planner
5. Run Budget Agent
6. Run deterministic validators
7. Run Consistency Agent
8. If PASS → return final plan
9. If FAIL → identify relevant repair agent
10. Repair
11. Revalidate
12. Return final plan after validation

---

## agents.py

Purpose:
Define the AI chains/agents.

Functions:

build_script_analyst()
build_shot_planner()
build_production_planner()
build_budget_agent()
build_consistency_agent()

The agents use LangChain and structured Pydantic output.

The LLM should be used for:
- interpretation
- extraction
- reasoning
- planning
- recommendations

The LLM should NOT be trusted for:
- arithmetic
- hard constraints
- deterministic reference validation

---

## schemas.py

Purpose:
Define the structured contracts between agents using Pydantic.

Important models:

Character
Location
Prop
Scene
ScriptAnalysis
Shot
ShotPlan
ShootDay
ProductionSchedule
BudgetItem
Budget
ValidationIssue
ValidationResult

The key principle:

Agent 1
→ structured ScriptAnalysis
→ Agent 2
→ structured ShotPlan
→ Agent 3
→ structured ProductionSchedule
→ Agent 4
→ structured Budget
→ Agent 5
→ structured ValidationResult

Do not pass large unstructured text between agents when a structured object can be used.

---

## prompts.py

Purpose:
Store the system prompts/instructions for every agent.

Prompts should clearly define:
- Agent role
- Input
- Responsibilities
- Constraints
- Output expectations
- What the agent must not invent
- Relationships to downstream agents

Prompts:

SCRIPT_ANALYST_PROMPT
SHOT_PLANNER_PROMPT
PRODUCTION_PLANNER_PROMPT
BUDGET_PROMPT
CONSISTENCY_PROMPT

A Manager prompt can be added when implementing an LLM-based Manager.

---

## tools.py

Purpose:
Normal deterministic Python utilities.

Potential functions:

extract_pdf_text()
calculate_budget()
check_actor_availability()
check_location_availability()
check_schedule_capacity()
export_production_plan()

PDF extraction can use PyMuPDF.

Budget arithmetic should be Python.

Example rate card:

camera = 5000
lighting = 2500
tripod = 500
location = 3000
catering_per_person = 300
transport = 2000

The actual values can be changed to match the demo scenario.

---

## validators.py

Purpose:
Deterministic hard validation.

Examples:

validate_scene_references()
validate_schedule_capacity()
validate_budget()
validate_actor_conflicts()
validate_location_conflicts()
validate_equipment_conflicts()

Examples of deterministic checks:

- Does every shot reference a real scene?
- Does every scheduled scene exist?
- Does the daily schedule exceed maximum minutes?
- Does budget subtotal equal line items?
- Does total equal subtotal + contingency?
- Are required actors available?
- Are locations double-booked?

This makes the project more reliable than an LLM-only pipeline.

---

# Structured Data Models

## Scene

Possible fields:

id
scene_number
heading
location_id
time_of_day
characters
props
description
page_start
page_end

## Shot

Possible fields:

id
scene_id
shot_type
camera_angle
camera_movement
subjects
equipment
estimated_setup_minutes
rationale

## ShootDay

Possible fields:

day_number
date
location_id
scene_ids
estimated_minutes

## BudgetItem

Possible fields:

category
description
quantity
unit_cost
total_cost

## ValidationIssue

Possible fields:

severity
category
message
scene_ids
suggested_fix

---

# Deterministic Validation + AI Validation

The system should use two layers.

## Layer 1 — Python deterministic validation

Checks facts and constraints.

Examples:
- arithmetic
- references
- capacity
- availability
- double booking

## Layer 2 — Consistency Agent

Checks higher-level production reasoning.

Examples:
- Does the overall plan make practical sense?
- Are there suspicious assumptions?
- Are there missing production dependencies?
- Are there inconsistencies that simple rules did not catch?

Combined:

Deterministic Validators
+
AI Consistency Agent
→
Validation Result

---

# Repair Loop

The repair loop is a major differentiator.

Example:

Production Planner creates:

Day 2:
- Scene 5
- Scene 7
- Scene 8

Consistency Agent detects:

Actor Sarah is required for Scene 7 but is only available until 17:00.
Scene 7 is scheduled after 17:00.

Manager decides:

REPAIR → Production Planner

Production Planner creates a revised schedule.

Consistency Agent checks again.

If valid:

PASS

If invalid:

REPAIR again, subject to a maximum retry count.

Recommended safety limit:
3 repair attempts.

If still invalid:
Return a human-review warning rather than looping forever.

---

# Technology Stack

Initial MVP:

Python
+
LangChain
+
OpenAI-compatible LLM
+
Pydantic
+
PyMuPDF
+
Streamlit
+
python-dotenv

Optional later:

Pandas
ReportLab
LangGraph

LangGraph should only be introduced if conditional routing/repair becomes sufficiently complex. The initial sequential pipeline can be implemented cleanly in Python.

---

# requirements.txt

Suggested dependencies:

streamlit
langchain
langchain-openai
pydantic
pymupdf
python-dotenv
pandas
reportlab

---

# Environment

.env

OPENAI_API_KEY=your_key_here

Never commit .env.

.gitignore should include:

.env
venv/
__pycache__/
*.pyc
outputs/
uploaded_script.pdf

---

# Six-Person Team Responsibilities

Member 1:
- pipeline.py
- integration
- Manager/orchestration

Member 2:
- Script Analyst
- agents.py
- script-analysis prompts

Member 3:
- Shot Planner
- agents.py
- shot-planning prompts

Member 4:
- Production Planner
- Budget Agent
- scheduling/budget logic

Member 5:
- app.py
- Streamlit UI
- visualization of agent pipeline

Member 6:
- schemas.py
- validators.py
- testing
- deterministic constraint checks

prompts.py should be collaboratively maintained.

---

# Recommended Development Order

1. Define schemas.py first.
2. Implement PDF extraction in tools.py.
3. Make Script Analyst work:
   PDF → ScriptAnalysis
4. Make Shot Planner work:
   ScriptAnalysis → ShotPlan
5. Make Production Planner work:
   ScriptAnalysis + ShotPlan → ProductionSchedule
6. Make Budget Agent work:
   ProductionSchedule → Budget
7. Make deterministic validators work.
8. Make Consistency Agent work.
9. Connect everything in pipeline.py.
10. Build Streamlit UI.
11. Add repair loop.
12. Add report export.
13. Polish the visual demo.

---

# Demo Goal

The final demo should show:

SCREENPLAY
↓
18 scenes extracted
↓
Characters / locations / props identified
↓
Shot list generated
↓
Scenes grouped into shooting days
↓
Budget generated
↓
Consistency check finds a deliberate conflict
↓
Manager identifies the responsible agent
↓
Production Planner repairs schedule
↓
Consistency Agent rechecks
↓
✅ VALIDATED PRODUCTION PLAN

The important point is that the agents are not merely producing independent AI outputs. They are connected through shared structured data and can react to each other's outputs.

---

# Differentiation / Avoiding Generic AI Slop

Do not make the project simply:

Upload PDF → LLM → giant report.

Instead demonstrate:

1. Structured intermediate state
2. Traceability from every shot to a scene
3. Deterministic validation
4. Cross-agent dependencies
5. Conflict detection
6. Automatic repair
7. Visual agent orchestration
8. Final production package

The strongest demo moment should be a visible conflict:

Schedule created
→ Consistency Agent catches conflict
→ Manager routes repair
→ Schedule changes
→ Validation passes

That demonstrates actual multi-agent collaboration rather than a collection of chatbot calls.

---

# Reference Architecture

The project is inspired by the architecture of the AkarshVyas Multi-agent Research System:

agents.py
→ specialized agents/chains

pipeline.py
→ sequential orchestration

tools.py
→ supporting tools

app.py
→ Streamlit UI

The Film Production Factory adapts the same general architecture to:

Screenplay
→ Breakdown
→ Shots
→ Schedule
→ Budget
→ Validation
→ Repair
→ Final Production Plan

---

# Core Principle

The entire system can be summarized as:

SCREENPLAY
    ↓
SCRIPT ANALYST
    ↓
STRUCTURED PRODUCTION STATE
    ↓
SHOT PLANNER
    ↓
STRUCTURED SHOT PLAN
    ↓
PRODUCTION PLANNER
    ↓
STRUCTURED SCHEDULE
    ↓
BUDGET AGENT
    ↓
STRUCTURED BUDGET
    ↓
CONSISTENCY AGENT
    ↓
MANAGER
    ↓
PASS → FINAL PLAN
or
FAIL → REPAIR → REVALIDATE

The objective is to build a credible AI-assisted film pre-production system, not simply a multi-agent chatbot.
"""

md_path = Path("/mnt/data/film_production_factory_hackathon_context.md")
txt_path = Path("/mnt/data/film_production_factory_hackathon_context.txt")

md_path.write_text(capsule, encoding="utf-8")
txt_path.write_text(capsule, encoding="utf-8")

print(f"Created Markdown: {md_path}")
print(f"Created Text: {txt_path}")
print(f"Markdown size: {md_path.stat().st_size / 1024:.1f} KB")
print(f"Text size: {txt_path.stat().st_size / 1024:.1f} KB")
