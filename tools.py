import fitz  # PyMuPDF
from schemas import *
from datetime import datetime

# ─── Rate Card ────────────────────────────────────────────────
RATE_CARD = {
    "camera_per_day": 5000,
    "lighting_per_day": 2500,
    "sound_per_day": 3000,
    "location_per_day": 3000,
    "transport_per_day": 2000,
    "catering_per_person_per_day": 300,
    "crew_per_day": 8000,
    "dolly_per_day": 1500,
    "crane_per_day": 4000,
    "steadicam_per_day": 2000,
    "drone_per_day": 3500,
    "tripod_per_day": 500,
    "props_budget": 2000,
    "makeup_per_day": 1500,
    "contingency_percent": 10,
}

# Average crew size for budget calculation
DEFAULT_CREW_SIZE = 15

# ─── Actor Availability ──────────────────────────────────────
# Demo availability: actor name -> list of (day_number, available_from, available_until)
# This is used for the demo conflict. In a real system this would be configurable.
ACTOR_AVAILABILITY = {
    "Sarah": [
        {"day": 1, "available_from": "09:00", "available_until": "17:00"},
        {"day": 2, "available_from": "09:00", "available_until": "20:00"},
        {"day": 3, "available_from": "09:00", "available_until": "20:00"},
        {"day": 4, "available_from": "09:00", "available_until": "20:00"},
    ],
    # Other actors are available all day by default
}

MAX_DAILY_MINUTES = 600  # 10 hours

def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page_num, page in enumerate(doc):
            text += f"\n--- PAGE {page_num + 1} ---\n"
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {e}")

def get_page_count(file_bytes: bytes) -> int:
    """Get the number of pages in a PDF."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 0

def calculate_budget(schedule: ProductionSchedule, shot_plan: ShotPlan, script_analysis: ScriptAnalysis, rate_card: dict = None) -> Budget:
    """Calculate budget deterministically from schedule, shots, and rate card.
    
    The LLM identifies resources; this function does ALL arithmetic.
    """
    if rate_card is None:
        rate_card = RATE_CARD
    
    num_days = len(schedule.shoot_days)
    items = []
    
    # Camera equipment - every day
    items.append(BudgetItem(
        category="Equipment",
        description="Camera Package",
        quantity=num_days,
        unit_cost=rate_card["camera_per_day"],
        total_cost=num_days * rate_card["camera_per_day"]
    ))
    
    # Lighting - every day
    items.append(BudgetItem(
        category="Equipment",
        description="Lighting Package",
        quantity=num_days,
        unit_cost=rate_card["lighting_per_day"],
        total_cost=num_days * rate_card["lighting_per_day"]
    ))
    
    # Sound - every day
    items.append(BudgetItem(
        category="Equipment",
        description="Sound Package",
        quantity=num_days,
        unit_cost=rate_card["sound_per_day"],
        total_cost=num_days * rate_card["sound_per_day"]
    ))
    
    # Check if any shots need special equipment
    all_equipment = set()
    for shot in shot_plan.shots:
        for eq in shot.equipment:
            all_equipment.add(eq.lower())
    
    if any("dolly" in eq for eq in all_equipment):
        dolly_days = num_days  # simplification
        items.append(BudgetItem(
            category="Equipment",
            description="Dolly",
            quantity=dolly_days,
            unit_cost=rate_card["dolly_per_day"],
            total_cost=dolly_days * rate_card["dolly_per_day"]
        ))
    
    if any("steadicam" in eq for eq in all_equipment):
        items.append(BudgetItem(
            category="Equipment",
            description="Steadicam",
            quantity=num_days,
            unit_cost=rate_card["steadicam_per_day"],
            total_cost=num_days * rate_card["steadicam_per_day"]
        ))
    
    if any("drone" in eq for eq in all_equipment):
        items.append(BudgetItem(
            category="Equipment",
            description="Drone",
            quantity=num_days,
            unit_cost=rate_card["drone_per_day"],
            total_cost=num_days * rate_card["drone_per_day"]
        ))
    
    # Tripod - every day
    items.append(BudgetItem(
        category="Equipment",
        description="Tripod",
        quantity=num_days,
        unit_cost=rate_card["tripod_per_day"],
        total_cost=num_days * rate_card["tripod_per_day"]
    ))
    
    # Locations - unique locations
    unique_locations = set()
    for day in schedule.shoot_days:
        unique_locations.add(day.location_name)
    loc_days = num_days  # each day has a location cost
    items.append(BudgetItem(
        category="Locations",
        description=f"Location Fees ({len(unique_locations)} locations)",
        quantity=loc_days,
        unit_cost=rate_card["location_per_day"],
        total_cost=loc_days * rate_card["location_per_day"]
    ))
    
    # Crew
    items.append(BudgetItem(
        category="Crew",
        description=f"Crew ({DEFAULT_CREW_SIZE} members)",
        quantity=num_days,
        unit_cost=rate_card["crew_per_day"],
        total_cost=num_days * rate_card["crew_per_day"]
    ))
    
    # Transport
    items.append(BudgetItem(
        category="Transport",
        description="Transport & Logistics",
        quantity=num_days,
        unit_cost=rate_card["transport_per_day"],
        total_cost=num_days * rate_card["transport_per_day"]
    ))
    
    # Catering
    num_cast = len(script_analysis.characters)
    total_people = DEFAULT_CREW_SIZE + num_cast
    items.append(BudgetItem(
        category="Catering",
        description=f"Catering ({total_people} people)",
        quantity=num_days * total_people,
        unit_cost=rate_card["catering_per_person_per_day"],
        total_cost=num_days * total_people * rate_card["catering_per_person_per_day"]
    ))
    
    # Makeup
    items.append(BudgetItem(
        category="Crew",
        description="Makeup & Hair",
        quantity=num_days,
        unit_cost=rate_card["makeup_per_day"],
        total_cost=num_days * rate_card["makeup_per_day"]
    ))
    
    # Props
    num_props = len(script_analysis.props)
    items.append(BudgetItem(
        category="Props",
        description=f"Props ({num_props} items)",
        quantity=1,
        unit_cost=rate_card["props_budget"] * max(1, num_props),
        total_cost=rate_card["props_budget"] * max(1, num_props)
    ))
    
    # Calculate totals
    subtotal = sum(item.total_cost for item in items)
    contingency_pct = rate_card["contingency_percent"]
    contingency_amt = round(subtotal * contingency_pct / 100, 2)
    total = round(subtotal + contingency_amt, 2)
    
    return Budget(
        line_items=items,
        subtotal=subtotal,
        contingency_percent=contingency_pct,
        contingency_amount=contingency_amt,
        total=total,
        currency="INR"
    )

def check_actor_availability(actor_name: str, day_number: int, start_time: str, end_time: str) -> bool:
    """Check if an actor is available during a time window.
    
    Returns True if available, False if not.
    Actors not in ACTOR_AVAILABILITY are assumed available all day.
    """
    if actor_name not in ACTOR_AVAILABILITY:
        return True
    
    for slot in ACTOR_AVAILABILITY[actor_name]:
        if slot["day"] == day_number:
            return start_time >= slot["available_from"] and end_time <= slot["available_until"]
    
    return True  # day not listed means available

def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes from midnight."""
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def minutes_to_time(minutes: int) -> str:
    """Convert minutes from midnight to HH:MM."""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def generate_report(state) -> str:
    """Generate a Markdown production report from the pipeline state."""
    lines = []
    lines.append("# 🎬 CineForge Production Package\n")
    
    # Project info
    if state.script_analysis:
        sa = state.script_analysis
        lines.append(f"## Project: {sa.title}\n")
        lines.append(f"- **Total Pages:** {sa.total_pages}")
        lines.append(f"- **Scenes:** {len(sa.scenes)}")
        lines.append(f"- **Characters:** {len(sa.characters)}")
        lines.append(f"- **Locations:** {len(sa.locations)}")
        lines.append(f"- **Props:** {len(sa.props)}")
        lines.append("")
        
        # Characters
        lines.append("## Characters\n")
        for c in sa.characters:
            lines.append(f"- **{c.name}** ({c.id}): {c.description}")
        lines.append("")
        
        # Locations
        lines.append("## Locations\n")
        for loc in sa.locations:
            lines.append(f"- **{loc.name}** ({loc.id}): {loc.int_ext} — {loc.description}")
        lines.append("")
        
        # Scene Breakdown
        lines.append("## Scene Breakdown\n")
        lines.append("| Scene | Heading | Characters | Pages |")
        lines.append("|-------|---------|------------|-------|")
        for s in sa.scenes:
            chars = ", ".join(s.character_names)
            lines.append(f"| {s.id} | {s.heading} | {chars} | {s.page_start}–{s.page_end} |")
        lines.append("")
    
    # Shot List
    if state.shot_plan:
        lines.append("## Shot List\n")
        lines.append(f"**Total Shots:** {len(state.shot_plan.shots)}\n")
        for shot in state.shot_plan.shots:
            lines.append(f"### {shot.id} (Scene {shot.scene_id})\n")
            lines.append(f"- **Type:** {shot.shot_type}")
            lines.append(f"- **Angle:** {shot.camera_angle}")
            lines.append(f"- **Movement:** {shot.camera_movement}")
            lines.append(f"- **Subjects:** {', '.join(shot.subjects)}")
            lines.append(f"- **Equipment:** {', '.join(shot.equipment)}")
            lines.append(f"- **Setup Time:** {shot.estimated_setup_minutes} min")
            lines.append(f"- **Rationale:** {shot.rationale}")
            lines.append("")
    
    # Schedule
    if state.production_schedule:
        lines.append("## Production Schedule\n")
        for day in state.production_schedule.shoot_days:
            lines.append(f"### Day {day.day_number} — {day.location_name}\n")
            for sc in day.scenes:
                lines.append(f"- **{sc.start_time}** — Scene {sc.scene_id} ({sc.estimated_duration_minutes} min)")
            lines.append(f"\n**Estimated Total:** {day.estimated_total_minutes} min\n")
    
    # Budget
    if state.budget:
        lines.append("## Budget\n")
        lines.append(f"**Currency:** {state.budget.currency}\n")
        lines.append("| Category | Description | Qty | Unit Cost | Total |")
        lines.append("|----------|-------------|-----|-----------|-------|")
        for item in state.budget.line_items:
            lines.append(f"| {item.category} | {item.description} | {item.quantity} | ₹{item.unit_cost:,.0f} | ₹{item.total_cost:,.0f} |")
        lines.append(f"\n**Subtotal:** ₹{state.budget.subtotal:,.0f}")
        lines.append(f"**Contingency ({state.budget.contingency_percent}%):** ₹{state.budget.contingency_amount:,.0f}")
        lines.append(f"**TOTAL:** ₹{state.budget.total:,.0f}\n")
    
    # Validation
    if state.validation_result:
        lines.append("## Consistency Report\n")
        lines.append(f"**Status:** {state.validation_result.status}\n")
        if state.validation_result.issues:
            for issue in state.validation_result.issues:
                lines.append(f"- [{issue.severity}] {issue.category}: {issue.message}")
        else:
            lines.append("✅ All checks passed. No issues detected.\n")
    
    # Repair History
    if state.repair_history:
        lines.append("## Repair History\n")
        for entry in state.repair_history:
            lines.append(f"- {entry}")
        lines.append("")
    
    # Execution Log
    lines.append("## Execution Log\n")
    for entry in state.execution_log:
        lines.append(f"- {entry}")
    
    lines.append("\n---\n*Generated by CineForge — AI Film Pre-Production Factory*")
    
    return "\n".join(lines)
