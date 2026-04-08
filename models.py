from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class ResourceType(str, Enum):
    INSTANCE = "instance"
    STORAGE = "storage"
    BUCKET = "bucket"

class ResourceStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    ATTACHED = "attached"
    AVAILABLE = "available"  # For orphaned storage

class Resource(BaseModel):
    id: str
    name: str
    type: ResourceType
    status: ResourceStatus
    cost_per_hour: float
    cpu_usage: float = 0.0  # Percentage
    ram_usage: float = 0.0  # Percentage
    metadata: Dict[str, Any] = {}

class ActionType(str, Enum):
    TERMINATE = "terminate"
    RESIZE = "resize"
    CLEANUP_ORPHANED = "cleanup_orphaned"
    NO_OP = "no_op"

class Action(BaseModel):
    action_type: ActionType
    resource_id: Optional[str] = None
    new_size: Optional[str] = None  # e.g., "t3.medium"

class Observation(BaseModel):
    resources: List[Resource]
    current_hourly_cost: float
    step_count: int
    max_steps: int
    task_description: str
    alerts: List[str] = []

class RewardComponents(BaseModel):
    points_savings: float = 0.0
    points_efficiency: float = 0.0
    penalty_sla: float = 0.0
    penalty_risk: float = 0.0

class Reward(BaseModel):
    value: float
    components: RewardComponents

class StepResponse(BaseModel):
    observation: Observation
    reward: float  # Total sum
    reward_breakdown: RewardComponents
    done: bool
    info: Dict[str, Any]

class State(BaseModel):
    resources: Dict[str, Resource]
    current_step: int
    max_steps: int
    task_id: str
    episode_id: str
    initial_cost: float
