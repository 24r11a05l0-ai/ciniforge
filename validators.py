"""Deterministic validators for CineForge production plans.

These validators check hard constraints using Python logic only — no LLM calls.
They run BEFORE the Consistency Agent to catch factual errors.
"""

from schemas import (
    ScriptAnalysis, ShotPlan, ProductionSchedule, Budget,
    ValidationIssue
)
from tools import ACTOR_AVAILABILITY, MAX_DAILY_MINUTES, time_to_minutes, minutes_to_time


def validate_scene_references(script_analysis: ScriptAnalysis, shot_plan: ShotPlan, schedule: ProductionSchedule) -> list[ValidationIssue]:
    """Check that all shots and scheduled scenes reference valid scene IDs."""
    issues = []
    valid_scene_ids = {s.id for s in script_analysis.scenes}
    
    # Check shot references
    for shot in shot_plan.shots:
        if shot.scene_id not in valid_scene_ids:
            issues.append(ValidationIssue(
                severity="ERROR",
                category="INVALID_REFERENCE",
                message=f"Shot {shot.id} references non-existent scene {shot.scene_id}",
                scene_ids=[shot.scene_id],
                suggested_fix=f"Update shot {shot.id} to reference a valid scene ID",
                responsible_agent="shot_planner"
            ))
    
    # Check scheduled scene references
    scheduled_scene_ids = set()
    for day in schedule.shoot_days:
        for sc in day.scenes:
            if sc.scene_id not in valid_scene_ids:
                issues.append(ValidationIssue(
                    severity="ERROR",
                    category="INVALID_REFERENCE",
                    message=f"Schedule Day {day.day_number} references non-existent scene {sc.scene_id}",
                    scene_ids=[sc.scene_id],
                    suggested_fix=f"Remove invalid scene from Day {day.day_number} schedule",
                    responsible_agent="production_planner"
                ))
            else:
                scheduled_scene_ids.add(sc.scene_id)
    
    # Check all scenes are scheduled
    for scene_id in valid_scene_ids:
        if scene_id not in scheduled_scene_ids:
            issues.append(ValidationIssue(
                severity="ERROR",
                category="SCENE_MISSING",
                message=f"Scene {scene_id} is not included in the production schedule",
                scene_ids=[scene_id],
                suggested_fix=f"Add scene {scene_id} to the production schedule",
                responsible_agent="production_planner"
            ))
    
    return issues


def validate_schedule_capacity(schedule: ProductionSchedule) -> list[ValidationIssue]:
    """Check that no shooting day exceeds the maximum daily minutes."""
    issues = []
    
    for day in schedule.shoot_days:
        total = day.estimated_total_minutes
        # Also calculate from individual scenes
        scene_total = sum(sc.estimated_duration_minutes for sc in day.scenes)
        actual_total = max(total, scene_total)
        
        if actual_total > MAX_DAILY_MINUTES:
            issues.append(ValidationIssue(
                severity="ERROR",
                category="SCHEDULE_OVERLOAD",
                message=f"Day {day.day_number} has {actual_total} minutes scheduled, exceeding the {MAX_DAILY_MINUTES} minute limit",
                scene_ids=[sc.scene_id for sc in day.scenes],
                suggested_fix=f"Move some scenes from Day {day.day_number} to another day or reduce durations",
                responsible_agent="production_planner"
            ))
    
    return issues


def validate_budget(budget: Budget) -> list[ValidationIssue]:
    """Check budget arithmetic: subtotal, contingency, and total must be correct."""
    issues = []
    
    # Check subtotal
    calculated_subtotal = sum(item.total_cost for item in budget.line_items)
    if abs(calculated_subtotal - budget.subtotal) > 0.01:
        issues.append(ValidationIssue(
            severity="ERROR",
            category="BUDGET_ERROR",
            message=f"Budget subtotal mismatch: items sum to {calculated_subtotal} but subtotal shows {budget.subtotal}",
            suggested_fix="Recalculate budget subtotal",
            responsible_agent="budget_agent"
        ))
    
    # Check individual line items
    for item in budget.line_items:
        expected = item.quantity * item.unit_cost
        if abs(expected - item.total_cost) > 0.01:
            issues.append(ValidationIssue(
                severity="ERROR",
                category="BUDGET_ERROR",
                message=f"Budget item '{item.description}': {item.quantity} × {item.unit_cost} = {expected}, but shows {item.total_cost}",
                suggested_fix=f"Fix arithmetic for {item.description}",
                responsible_agent="budget_agent"
            ))
    
    # Check contingency
    expected_contingency = round(budget.subtotal * budget.contingency_percent / 100, 2)
    if abs(expected_contingency - budget.contingency_amount) > 1:
        issues.append(ValidationIssue(
            severity="WARNING",
            category="BUDGET_ERROR",
            message=f"Contingency amount {budget.contingency_amount} doesn't match {budget.contingency_percent}% of {budget.subtotal}",
            suggested_fix="Recalculate contingency",
            responsible_agent="budget_agent"
        ))
    
    # Check total
    expected_total = round(budget.subtotal + budget.contingency_amount, 2)
    if abs(expected_total - budget.total) > 1:
        issues.append(ValidationIssue(
            severity="ERROR",
            category="BUDGET_ERROR",
            message=f"Budget total {budget.total} doesn't equal subtotal {budget.subtotal} + contingency {budget.contingency_amount} = {expected_total}",
            suggested_fix="Recalculate budget total",
            responsible_agent="budget_agent"
        ))
    
    return issues


def validate_actor_conflicts(script_analysis: ScriptAnalysis, schedule: ProductionSchedule) -> list[ValidationIssue]:
    """Check that actors are not scheduled when they're unavailable."""
    issues = []
    
    # Build scene -> characters map
    scene_chars = {}
    for scene in script_analysis.scenes:
        scene_chars[scene.id] = scene.character_names
    
    for day in schedule.shoot_days:
        for scheduled_scene in day.scenes:
            sid = scheduled_scene.scene_id
            if sid not in scene_chars:
                continue
            
            chars = scene_chars[sid]
            start = scheduled_scene.start_time
            duration = scheduled_scene.estimated_duration_minutes
            end_minutes = time_to_minutes(start) + duration
            end_time = minutes_to_time(end_minutes)
            
            for actor_name in chars:
                if actor_name in ACTOR_AVAILABILITY:
                    # Check this specific day
                    for slot in ACTOR_AVAILABILITY[actor_name]:
                        if slot["day"] == day.day_number:
                            avail_start = slot["available_from"]
                            avail_end = slot["available_until"]
                            
                            if start < avail_start or end_time > avail_end:
                                issues.append(ValidationIssue(
                                    severity="ERROR",
                                    category="ACTOR_CONFLICT",
                                    message=f"{actor_name} is scheduled for Scene {sid} ({start}-{end_time}) on Day {day.day_number}, but is only available {avail_start}-{avail_end}",
                                    scene_ids=[sid],
                                    suggested_fix=f"Move Scene {sid} to a time when {actor_name} is available (before {avail_end}) or to a different day",
                                    responsible_agent="production_planner"
                                ))
    
    return issues


def validate_location_conflicts(schedule: ProductionSchedule) -> list[ValidationIssue]:
    """Check for location conflicts (multiple different locations on same day shouldn't conflict)."""
    issues = []
    
    # Check for duplicate scenes across days
    scene_day_map = {}  # scene_id -> list of day numbers
    for day in schedule.shoot_days:
        for sc in day.scenes:
            if sc.scene_id not in scene_day_map:
                scene_day_map[sc.scene_id] = []
            scene_day_map[sc.scene_id].append(day.day_number)
    
    for scene_id, days in scene_day_map.items():
        if len(days) > 1:
            issues.append(ValidationIssue(
                severity="WARNING",
                category="DUPLICATE_SCENE",
                message=f"Scene {scene_id} is scheduled on multiple days: {days}",
                scene_ids=[scene_id],
                suggested_fix=f"Remove duplicate scheduling of Scene {scene_id}",
                responsible_agent="production_planner"
            ))
    
    return issues


def run_all_validators(
    script_analysis: ScriptAnalysis,
    shot_plan: ShotPlan,
    schedule: ProductionSchedule,
    budget: Budget
) -> list[ValidationIssue]:
    """Run ALL deterministic validators and return combined issues."""
    all_issues = []
    
    all_issues.extend(validate_scene_references(script_analysis, shot_plan, schedule))
    all_issues.extend(validate_schedule_capacity(schedule))
    all_issues.extend(validate_budget(budget))
    all_issues.extend(validate_actor_conflicts(script_analysis, schedule))
    all_issues.extend(validate_location_conflicts(schedule))
    
    return all_issues
