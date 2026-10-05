"""CineForge Pipeline — Main orchestration layer.

Connects five AI agents in sequence and handles the repair loop.
The Manager is deterministic Python orchestration (not an LLM agent).
"""

import traceback
from typing import Callable, Optional
from schemas import PipelineState, ValidationIssue
from tools import extract_pdf_text, calculate_budget, generate_report
from agents import (
    run_script_analyst, run_shot_planner, run_production_planner,
    run_budget_agent, run_consistency_agent
)
from validators import run_all_validators


def run_pipeline(
    file_bytes: bytes,
    status_callback: Optional[Callable] = None
) -> PipelineState:
    """Run the complete CineForge pipeline.
    
    Args:
        file_bytes: Raw bytes of the uploaded PDF file.
        status_callback: Optional callback function(agent_name, status, message)
                        for live UI updates.
    
    Returns:
        PipelineState with all agent outputs and validation results.
    """
    state = PipelineState()
    
    def update_status(agent: str, status: str, message: str = ""):
        state.agent_statuses[agent] = status
        log_entry = f"{_status_icon(status)} {_agent_label(agent)}: {message or status}"
        state.execution_log.append(log_entry)
        if status_callback:
            status_callback(agent, status, message)
    
    # ═══════════════════════════════════════════════════════════
    # STEP 0: Extract screenplay text
    # ═══════════════════════════════════════════════════════════
    try:
        state.screenplay_text = extract_pdf_text(file_bytes)
        if not state.screenplay_text.strip():
            raise ValueError("Extracted text is empty")
        state.execution_log.append("📄 Screenplay text extracted successfully")
    except Exception as e:
        state.execution_log.append(f"❌ PDF extraction failed: {e}")
        state.final_status = "ERROR"
        return state
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Script Analyst
    # ═══════════════════════════════════════════════════════════
    try:
        update_status("script_analyst", "running", "Analyzing screenplay...")
        state.script_analysis = run_script_analyst(state.screenplay_text)
        update_status("script_analyst", "complete", 
                     f"Extracted {len(state.script_analysis.scenes)} scenes, "
                     f"{len(state.script_analysis.characters)} characters, "
                     f"{len(state.script_analysis.locations)} locations")
    except Exception as e:
        update_status("script_analyst", "error", f"Failed: {e}")
        state.final_status = "ERROR"
        return state
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Shot Planner
    # ═══════════════════════════════════════════════════════════
    try:
        update_status("shot_planner", "running", "Generating shot coverage...")
        state.shot_plan = run_shot_planner(state.script_analysis)
        update_status("shot_planner", "complete",
                     f"Generated {len(state.shot_plan.shots)} shots")
    except Exception as e:
        update_status("shot_planner", "error", f"Failed: {e}")
        state.final_status = "ERROR"
        return state
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: Production Planner
    # ═══════════════════════════════════════════════════════════
    try:
        update_status("production_planner", "running", "Creating shooting schedule...")
        state.production_schedule = run_production_planner(
            state.script_analysis, state.shot_plan
        )
        update_status("production_planner", "complete",
                     f"Scheduled {state.production_schedule.total_shoot_days} shoot days")
    except Exception as e:
        update_status("production_planner", "error", f"Failed: {e}")
        state.final_status = "ERROR"
        return state
    
    # ═══════════════════════════════════════════════════════════
    # STEP 4: Budget Agent
    # ═══════════════════════════════════════════════════════════
    try:
        update_status("budget_agent", "running", "Calculating budget...")
        state.budget = run_budget_agent(
            state.script_analysis, state.shot_plan, state.production_schedule
        )
        update_status("budget_agent", "complete",
                     f"Total budget: ₹{state.budget.total:,.0f}")
    except Exception as e:
        update_status("budget_agent", "error", f"Failed: {e}")
        state.final_status = "ERROR"
        return state
    
    # ═══════════════════════════════════════════════════════════
    # STEP 5: Validation + Consistency Agent
    # ═══════════════════════════════════════════════════════════
    try:
        update_status("consistency_agent", "running", "Running validation...")
        
        # Run deterministic validators first
        validator_issues = run_all_validators(
            state.script_analysis, state.shot_plan,
            state.production_schedule, state.budget
        )
        
        if validator_issues:
            issues_str = "; ".join([f"{i.category}: {i.message}" for i in validator_issues])
            state.execution_log.append(f"🔍 Deterministic validators found {len(validator_issues)} issues: {issues_str}")
        
        # Run Consistency Agent (LLM-based higher-level check)
        state.validation_result = run_consistency_agent(
            state.script_analysis, state.shot_plan,
            state.production_schedule, state.budget,
            validator_issues
        )
        
        if state.validation_result.status == "PASS":
            update_status("consistency_agent", "complete", "All checks passed ✓")
            state.final_status = "PASS"
            return state
        else:
            error_count = len([i for i in state.validation_result.issues if i.severity == "ERROR"])
            warn_count = len([i for i in state.validation_result.issues if i.severity == "WARNING"])
            update_status("consistency_agent", "needs_repair",
                         f"Found {error_count} errors, {warn_count} warnings")
    except Exception as e:
        update_status("consistency_agent", "error", f"Failed: {e}")
        state.final_status = "ERROR"
        return state
    
    # ═══════════════════════════════════════════════════════════
    # STEP 6: Repair Loop (max 3 attempts)
    # ═══════════════════════════════════════════════════════════
    while state.repair_count < state.max_repairs and state.validation_result.status == "FAIL":
        state.repair_count += 1
        repair_msg = f"Repair attempt {state.repair_count}/{state.max_repairs}"
        state.execution_log.append(f"🔧 {repair_msg}")
        state.repair_history.append(repair_msg)
        
        # Find ERROR issues and their responsible agents
        error_issues = [i for i in state.validation_result.issues if i.severity == "ERROR"]
        if not error_issues:
            # Only warnings remain, consider it a pass
            state.validation_result.status = "PASS"
            state.final_status = "PASS"
            break
        
        # Identify which agents need to repair
        agents_to_repair = set()
        repair_context_parts = []
        for issue in error_issues:
            agent = issue.responsible_agent or "production_planner"  # default
            agents_to_repair.add(agent)
            repair_context_parts.append(f"[{issue.category}] {issue.message}. Fix: {issue.suggested_fix}")
        
        repair_context = "\n".join(repair_context_parts)
        
        # Run repairs
        try:
            if "production_planner" in agents_to_repair:
                update_status("production_planner", "running", f"Repairing schedule (attempt {state.repair_count})...")
                state.repair_history.append(f"Production Planner repairing: {repair_context}")
                state.production_schedule = run_production_planner(
                    state.script_analysis, state.shot_plan, repair_context
                )
                update_status("production_planner", "complete", "Schedule repaired")
            
            if "budget_agent" in agents_to_repair:
                update_status("budget_agent", "running", f"Recalculating budget (attempt {state.repair_count})...")
                state.budget = run_budget_agent(
                    state.script_analysis, state.shot_plan, state.production_schedule
                )
                update_status("budget_agent", "complete", "Budget recalculated")
            elif "production_planner" in agents_to_repair:
                # Recalculate budget anyway since schedule changed
                state.budget = run_budget_agent(
                    state.script_analysis, state.shot_plan, state.production_schedule
                )
            
            if "shot_planner" in agents_to_repair:
                update_status("shot_planner", "running", f"Regenerating shots (attempt {state.repair_count})...")
                state.shot_plan = run_shot_planner(state.script_analysis)
                update_status("shot_planner", "complete", "Shots regenerated")
            
            # Re-validate
            update_status("consistency_agent", "running", f"Re-validating (attempt {state.repair_count})...")
            
            validator_issues = run_all_validators(
                state.script_analysis, state.shot_plan,
                state.production_schedule, state.budget
            )
            
            state.validation_result = run_consistency_agent(
                state.script_analysis, state.shot_plan,
                state.production_schedule, state.budget,
                validator_issues
            )
            
            if state.validation_result.status == "PASS":
                update_status("consistency_agent", "complete", "All checks passed after repair ✓")
                state.final_status = "PASS"
                state.repair_history.append("✓ Validation passed after repair")
                break
            else:
                error_count = len([i for i in state.validation_result.issues if i.severity == "ERROR"])
                update_status("consistency_agent", "needs_repair", f"Still {error_count} errors after repair")
                state.repair_history.append(f"✗ Still {error_count} errors after attempt {state.repair_count}")
        
        except Exception as e:
            state.repair_history.append(f"Repair attempt {state.repair_count} failed: {e}")
            state.execution_log.append(f"❌ Repair error: {e}")
    
    # If we exhausted repair attempts
    if state.final_status != "PASS":
        state.final_status = "HUMAN_REVIEW_REQUIRED"
        state.execution_log.append("⚠️ Maximum repair attempts reached. Human review required.")
    
    return state


def _status_icon(status: str) -> str:
    """Get emoji icon for status."""
    return {
        "waiting": "○",
        "running": "◉",
        "complete": "✓",
        "needs_repair": "⚠",
        "error": "❌",
    }.get(status, "○")

def _agent_label(agent: str) -> str:
    """Get display label for agent."""
    return {
        "script_analyst": "🎭 Script Analyst",
        "shot_planner": "🎥 Shot Planner",
        "production_planner": "📅 Production Planner",
        "budget_agent": "💰 Budget Agent",
        "consistency_agent": "🧪 Consistency Agent",
    }.get(agent, agent)
