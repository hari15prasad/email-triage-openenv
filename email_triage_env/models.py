"""
Typed Pydantic models for the Email Triage OpenEnv environment.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Email data structures
# ---------------------------------------------------------------------------

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    priority_label: Optional[str] = None  # ground-truth, hidden from agent
    category_label: Optional[str] = None  # ground-truth, hidden from agent


# ---------------------------------------------------------------------------
# OpenEnv: Observation
# ---------------------------------------------------------------------------

class EmailTriageObservation(BaseModel):
    """What the agent sees at each step."""
    current_email: Optional[Email] = None
    inbox_size: int = Field(description="Total emails remaining in inbox")
    processed_count: int = Field(description="Emails processed so far")
    last_action_feedback: str = Field(
        default="", description="Feedback from the last action taken"
    )
    task_name: str = Field(default="", description="Active task identifier")
    task_description: str = Field(default="", description="Human-readable task goal")
    step_number: int = Field(default=0)


# ---------------------------------------------------------------------------
# OpenEnv: Action
# ---------------------------------------------------------------------------

class EmailTriageAction(BaseModel):
    """Action the agent submits each step."""
    priority: str = Field(
        description="Assigned priority: 'urgent', 'high', 'normal', or 'low'"
    )
    category: str = Field(
        description=(
            "Email category: 'bug_report', 'feature_request', 'billing', "
            "'general_inquiry', 'spam', 'internal', or 'security'"
        )
    )
    response_draft: str = Field(
        default="",
        description=(
            "Optional: a short draft reply (1-3 sentences). "
            "Required for hard task."
        ),
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of why this priority/category was chosen.",
    )


# ---------------------------------------------------------------------------
# OpenEnv: Reward
# ---------------------------------------------------------------------------

class EmailTriageReward(BaseModel):
    """Per-step reward breakdown."""
    priority_score: float = Field(
        ge=0.0, le=1.0, description="Score for priority assignment"
    )
    category_score: float = Field(
        ge=0.0, le=1.0, description="Score for category assignment"
    )
    response_score: float = Field(
        ge=0.0, le=1.0, description="Score for response draft quality"
    )
    total: float = Field(ge=0.0, le=1.0, description="Weighted total reward")
    feedback: str = Field(default="", description="Human-readable feedback")


# ---------------------------------------------------------------------------
# Step result
# ---------------------------------------------------------------------------

class StepResult(BaseModel):
    observation: EmailTriageObservation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)
