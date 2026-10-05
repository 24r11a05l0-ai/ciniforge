"""CineForge AI Agents — Five specialized film pre-production agents."""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from schemas import (
    ScriptAnalysis, ShotPlan, ProductionSchedule, 
    Budget, ValidationResult, ValidationIssue
)
from prompts import (
    SCRIPT_ANALYST_PROMPT, SHOT_PLANNER_PROMPT,
    PRODUCTION_PLANNER_PROMPT, BUDGET_PROMPT, CONSISTENCY_PROMPT
)
from tools import ACTOR_AVAILABILITY, calculate_budget

load_dotenv()

def get_llm(temperature: float = 0) -> ChatOpenAI:
    """Get configured LLM instance. Single point of model configuration."""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

# ─── Agent 1: Script Analyst ─────────────────────────────────────────────────
def build_script_analyst():
    """Build the Script Analyst chain that extracts structured data from screenplay text."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(ScriptAnalysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SCRIPT_ANALYST_PROMPT),
        ("human", "Analyze this screenplay and extract ALL production information:\n\n{screenplay_text}")
    ])
    
    chain = prompt | structured_llm
    return chain

def run_script_analyst(screenplay_text: str) -> ScriptAnalysis:
    """Run the Script Analyst on screenplay text."""
    chain = build_script_analyst()
    result = chain.invoke({"screenplay_text": screenplay_text})
    return result

# ─── Agent 2: Shot Planner ────────────────────────────────────────────────────
def build_shot_planner():
    """Build the Shot Planner chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(ShotPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SHOT_PLANNER_PROMPT),
        ("human", "Create a shot plan for this production:\n\n{script_analysis_json}")
    ])
    
    chain = prompt | structured_llm
    return chain

def run_shot_planner(script_analysis: ScriptAnalysis) -> ShotPlan:
    """Run the Shot Planner on script analysis."""
    chain = build_shot_planner()
    result = chain.invoke({"script_analysis_json": script_analysis.model_dump_json(indent=2)})
    # Set total_shots
    result.total_shots = len(result.shots)
    return result

# ─── Agent 3: Production Planner ──────────────────────────────────────────────
def build_production_planner():
    """Build the Production Planner chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(ProductionSchedule)
    
    # Format actor availability for the prompt
    avail_str = json.dumps(ACTOR_AVAILABILITY, indent=2)
    system_prompt = PRODUCTION_PLANNER_PROMPT.replace("{actor_availability}", avail_str)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Create a production schedule for this project.\n\nScript Analysis:\n{script_analysis_json}\n\nShot Plan:\n{shot_plan_json}")
    ])
    
    chain = prompt | structured_llm
    return chain

def run_production_planner(script_analysis: ScriptAnalysis, shot_plan: ShotPlan, repair_context: str = "") -> ProductionSchedule:
    """Run the Production Planner."""
    chain = build_production_planner()
    
    sa_json = script_analysis.model_dump_json(indent=2)
    sp_json = shot_plan.model_dump_json(indent=2)
    
    if repair_context:
        sa_json += f"\n\nREPAIR INSTRUCTIONS:\n{repair_context}"
    
    result = chain.invoke({
        "script_analysis_json": sa_json,
        "shot_plan_json": sp_json
    })
    result.total_shoot_days = len(result.shoot_days)
    return result

# ─── Agent 4: Budget Agent ────────────────────────────────────────────────────
def build_budget_agent():
    """Build the Budget Agent chain.
    
    NOTE: The actual budget arithmetic is done by Python in tools.py.
    The LLM only provides qualitative notes.
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", BUDGET_PROMPT),
        ("human", "Review this production plan and provide budget notes:\n\nScript: {script_summary}\nShots: {shot_count} total\nSchedule: {schedule_days} shoot days")
    ])
    
    chain = prompt | llm
    return chain

def run_budget_agent(script_analysis: ScriptAnalysis, shot_plan: ShotPlan, schedule: ProductionSchedule) -> Budget:
    """Run the Budget Agent. Uses Python for all arithmetic."""
    # Step 1: Calculate budget deterministically with Python
    budget = calculate_budget(schedule, shot_plan, script_analysis)
    
    # Step 2: Optionally get LLM notes (non-critical)
    try:
        chain = build_budget_agent()
        llm_response = chain.invoke({
            "script_summary": f"{script_analysis.title}: {len(script_analysis.scenes)} scenes, {len(script_analysis.characters)} characters, {len(script_analysis.locations)} locations",
            "shot_count": str(len(shot_plan.shots)),
            "schedule_days": str(len(schedule.shoot_days))
        })
        budget.notes = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
    except Exception:
        budget.notes = "Budget calculated using standard rate card."
    
    return budget

# ─── Agent 5: Consistency Agent ───────────────────────────────────────────────
def build_consistency_agent():
    """Build the Consistency Agent chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(ValidationResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", CONSISTENCY_PROMPT),
        ("human", "Review this complete production plan for consistency:\n\nScript Analysis:\n{script_analysis_json}\n\nShot Plan:\n{shot_plan_json}\n\nProduction Schedule:\n{schedule_json}\n\nBudget:\n{budget_json}\n\nDeterministic Validation Results:\n{validator_results}")
    ])
    
    chain = prompt | structured_llm
    return chain

def run_consistency_agent(
    script_analysis: ScriptAnalysis,
    shot_plan: ShotPlan,
    schedule: ProductionSchedule,
    budget: Budget,
    validator_issues: list[ValidationIssue]
) -> ValidationResult:
    """Run the Consistency Agent."""
    chain = build_consistency_agent()
    
    # Format validator issues
    if validator_issues:
        validator_str = "\n".join([
            f"[{issue.severity}] {issue.category}: {issue.message} (Scenes: {', '.join(issue.scene_ids)})"
            for issue in validator_issues
        ])
    else:
        validator_str = "No issues found by deterministic validators."
    
    result = chain.invoke({
        "script_analysis_json": script_analysis.model_dump_json(indent=2),
        "shot_plan_json": shot_plan.model_dump_json(indent=2),
        "schedule_json": schedule.model_dump_json(indent=2),
        "budget_json": budget.model_dump_json(indent=2),
        "validator_results": validator_str
    })
    
    # Merge deterministic issues into the result
    if validator_issues:
        all_issues = list(validator_issues) + list(result.issues)
        has_errors = any(i.severity == "ERROR" for i in all_issues)
        result.issues = all_issues
        result.status = "FAIL" if has_errors else result.status
    
    return result
