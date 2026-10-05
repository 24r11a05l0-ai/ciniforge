"""Unit test for CineForge validators and offline simulation.
"""

from schemas import (
    ScriptAnalysis, Scene, Character, Location, Prop,
    ShotPlan, Shot, ScheduledScene, ShootDay, ProductionSchedule, Budget, BudgetItem
)
from validators import (
    validate_actor_conflicts, validate_scene_references,
    validate_schedule_capacity, validate_budget, run_all_validators
)
from tools import ACTOR_AVAILABILITY

def test_actor_conflict():
    print("Testing actor conflict validator...")
    
    # Create scene with Sarah
    scene7 = Scene(
        id="SC007",
        scene_number=7,
        heading="INT. SERVER ROOM - NIGHT",
        int_ext="INT",
        location_id="LOC003",
        location_name="Server Room",
        time_of_day="NIGHT",
        characters=["CHAR002"],
        character_names=["Sarah"],
        description="Sarah hacks the system.",
        page_start=6,
        page_end=7,
        estimated_duration_minutes=45
    )
    
    script_analysis = ScriptAnalysis(
        title="Demo Screenplay",
        total_pages=10,
        scenes=[scene7],
        characters=[Character(id="CHAR002", name="Sarah")],
        locations=[Location(id="LOC003", name="Server Room", int_ext="INT")],
        props=[]
    )
    
    # Schedule Scene 7 late on Day 1 (17:30 to 18:15) -> Sarah only available until 17:00 on Day 1!
    day1 = ShootDay(
        day_number=1,
        location_id="LOC003",
        location_name="Server Room",
        scenes=[
            ScheduledScene(
                scene_id="SC007",
                start_time="17:30",
                estimated_duration_minutes=45
            )
        ],
        estimated_total_minutes=45
    )
    
    schedule = ProductionSchedule(shoot_days=[day1], total_shoot_days=1)
    
    # Run validator
    issues = validate_actor_conflicts(script_analysis, schedule)
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  [{issue.severity}] {issue.category}: {issue.message}")
        print(f"  Fix: {issue.suggested_fix}")
    
    assert len(issues) > 0, "Should have detected Sarah availability conflict!"
    assert issues[0].responsible_agent == "production_planner"
    print("[OK] Actor conflict test PASSED!")

if __name__ == "__main__":
    test_actor_conflict()
