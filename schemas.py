from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Character(BaseModel):
    id: str = Field(description="Unique character ID, e.g. CHAR001")
    name: str
    description: str = ""

class Location(BaseModel):
    id: str = Field(description="Unique location ID, e.g. LOC001")
    name: str
    int_ext: str = Field(description="INT or EXT")
    description: str = ""

class Prop(BaseModel):
    id: str = Field(description="Unique prop ID, e.g. PROP001")
    name: str
    description: str = ""

class Scene(BaseModel):
    id: str = Field(description="Unique scene ID, e.g. SC001")
    scene_number: int
    heading: str = Field(description="Full scene heading, e.g. INT. COFFEE SHOP - MORNING")
    int_ext: str = Field(description="INT or EXT")
    location_id: str
    location_name: str
    time_of_day: str
    characters: list[str] = Field(description="List of character IDs")
    character_names: list[str] = Field(description="List of character names")
    props: list[str] = Field(default_factory=list, description="List of prop IDs")
    prop_names: list[str] = Field(default_factory=list, description="List of prop names")
    description: str
    page_start: int
    page_end: int
    estimated_duration_minutes: int = Field(default=30, description="Estimated shooting duration")

class ScriptAnalysis(BaseModel):
    title: str
    total_pages: int
    scenes: list[Scene]
    characters: list[Character]
    locations: list[Location]
    props: list[Prop]
    summary: str = ""

class Shot(BaseModel):
    id: str = Field(description="Unique shot ID, e.g. SHOT001")
    scene_id: str
    shot_type: str = Field(description="Wide, Medium, Close-up, Over-the-shoulder, etc.")
    camera_angle: str = Field(description="Eye Level, Low Angle, High Angle, Dutch, etc.")
    camera_movement: str = Field(description="Static, Pan, Tilt, Dolly, Tracking, Handheld, etc.")
    subjects: list[str] = Field(description="Character names or objects in the shot")
    equipment: list[str] = Field(description="Required equipment: Camera, Tripod, Dolly, etc.")
    estimated_setup_minutes: int = Field(default=15)
    rationale: str = Field(description="Why this shot is needed")
    is_screenplay_fact: bool = Field(default=False, description="True if explicitly described in screenplay")

class ShotPlan(BaseModel):
    shots: list[Shot]
    total_shots: int = 0
    notes: str = ""

class ScheduledScene(BaseModel):
    scene_id: str
    start_time: str = Field(description="HH:MM format")
    estimated_duration_minutes: int
    shots: list[str] = Field(default_factory=list, description="Shot IDs for this scene")

class ShootDay(BaseModel):
    day_number: int
    date: str = Field(default="", description="Optional date")
    location_id: str
    location_name: str
    scenes: list[ScheduledScene]
    estimated_total_minutes: int
    notes: str = ""

class ProductionSchedule(BaseModel):
    shoot_days: list[ShootDay]
    total_shoot_days: int = 0
    notes: str = ""

class BudgetItem(BaseModel):
    category: str
    description: str
    quantity: int = 1
    unit_cost: float
    total_cost: float

class Budget(BaseModel):
    line_items: list[BudgetItem]
    subtotal: float
    contingency_percent: float = Field(default=10.0)
    contingency_amount: float
    total: float
    currency: str = "INR"
    notes: str = ""

class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class ValidationIssue(BaseModel):
    severity: str = Field(description="ERROR, WARNING, or INFO")
    category: str = Field(description="ACTOR_CONFLICT, SCENE_MISSING, SCHEDULE_OVERLOAD, BUDGET_ERROR, LOCATION_CONFLICT, etc.")
    message: str
    scene_ids: list[str] = Field(default_factory=list)
    suggested_fix: str = ""
    responsible_agent: str = Field(default="", description="Which agent should fix this: script_analyst, shot_planner, production_planner, budget_agent")

class ValidationResult(BaseModel):
    status: str = Field(description="PASS or FAIL")
    issues: list[ValidationIssue] = Field(default_factory=list)
    summary: str = ""

class AgentStatus(str, Enum):
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETE = "complete"
    NEEDS_REPAIR = "needs_repair"
    ERROR = "error"

class PipelineState(BaseModel):
    screenplay_text: str = ""
    script_analysis: Optional[ScriptAnalysis] = None
    shot_plan: Optional[ShotPlan] = None
    production_schedule: Optional[ProductionSchedule] = None
    budget: Optional[Budget] = None
    validation_result: Optional[ValidationResult] = None
    agent_statuses: dict[str, str] = Field(default_factory=lambda: {
        "script_analyst": "waiting",
        "shot_planner": "waiting",
        "production_planner": "waiting",
        "budget_agent": "waiting",
        "consistency_agent": "waiting",
    })
    execution_log: list[str] = Field(default_factory=list)
    repair_history: list[str] = Field(default_factory=list)
    repair_count: int = 0
    max_repairs: int = 3
    final_status: str = ""  # PASS, FAIL, HUMAN_REVIEW_REQUIRED
