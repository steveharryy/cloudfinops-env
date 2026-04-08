import uuid
from typing import Dict, List, Tuple, Any
from models import (
    Resource, ResourceType, ResourceStatus, Action, ActionType, 
    Observation, State, StepResponse, RewardComponents
)
from logger import TrajectoryLogger

# Standard Pricing/Specs
INSTANCE_TYPES = {
    "t3.nano": {"cpu": 2, "ram": 0.5, "cost": 0.0052},
    "t3.micro": {"cpu": 2, "ram": 1, "cost": 0.0104},
    "t3.small": {"cpu": 2, "ram": 2, "cost": 0.0208},
    "t3.medium": {"cpu": 2, "ram": 4, "cost": 0.0416},
    "m5.large": {"cpu": 2, "ram": 8, "cost": 0.096},
    "m5.xlarge": {"cpu": 4, "ram": 16, "cost": 0.192},
    "m5.2xlarge": {"cpu": 8, "ram": 32, "cost": 0.384},
}

class CloudFinOpsEngine:
    def __init__(self):
        self.state: State = None
        self.task_description: str = ""
        self.logger = TrajectoryLogger()

    def reset(self, task_id: str, resources: List[Resource], task_desc: str, max_steps: int = 10) -> Observation:
        self.task_description = task_desc
        initial_resources = {r.id: r for r in resources}
        initial_cost = sum(r.cost_per_hour for r in resources if r.status != ResourceStatus.TERMINATED)
        
        # Start logging a new episode
        self.logger.start_episode(task_id)
        
        self.state = State(
            resources=initial_resources,
            current_step=0,
            max_steps=max_steps,
            task_id=task_id,
            episode_id=self.logger.current_episode_id,
            initial_cost=initial_cost
        )
        
        obs = self._get_observation()
        # Log the initial state (action is None or No-op)
        self.logger.log_step(0, obs.model_dump(), {"action_type": "reset"}, 0.0, {})
        
        return obs

    def step(self, action: Action) -> StepResponse:
        self.state.current_step += 1
        info = {"logs": []}
        
        # Apply Action
        if action.action_type == ActionType.TERMINATE:
            if action.resource_id in self.state.resources:
                res = self.state.resources[action.resource_id]
                if res.status != ResourceStatus.TERMINATED:
                    res.status = ResourceStatus.TERMINATED
                    res.cost_per_hour = 0.0
                    info["logs"].append(f"Terminated resource {action.resource_id}")
                else:
                    info["logs"].append(f"Resource {action.resource_id} already terminated")
            else:
                info["logs"].append(f"Resource {action.resource_id} not found")

        elif action.action_type == ActionType.RESIZE:
            if action.resource_id in self.state.resources:
                res = self.state.resources[action.resource_id]
                if res.type == ResourceType.INSTANCE and action.new_size in INSTANCE_TYPES:
                    old_type_name = res.metadata.get("instance_type", "m5.large")
                    old_cpu_cores = INSTANCE_TYPES.get(old_type_name, {"cpu": 2})["cpu"]
                    new_specs = INSTANCE_TYPES[action.new_size]
                    new_cpu_cores = new_specs["cpu"]
                    
                    res.cpu_usage = (res.cpu_usage * old_cpu_cores) / new_cpu_cores
                    res.cost_per_hour = new_specs["cost"]
                    res.metadata["instance_type"] = action.new_size
                    info["logs"].append(f"Resized {action.resource_id} to {action.new_size}")
            else:
                info["logs"].append(f"Resource {action.resource_id} not found")

        elif action.action_type == ActionType.CLEANUP_ORPHANED:
            cleaned_count = 0
            for r in self.state.resources.values():
                if r.status == ResourceStatus.AVAILABLE and r.type == ResourceType.STORAGE:
                    r.status = ResourceStatus.TERMINATED
                    r.cost_per_hour = 0.0
                    cleaned_count += 1
            info["logs"].append(f"Cleaned up {cleaned_count} volumes")

        # Calculate Points & Penalties
        current_cost = sum(r.cost_per_hour for r in self.state.resources.values() if r.status != ResourceStatus.TERMINATED)
        reward_value, components = self._calculate_reward(current_cost)
        
        obs = self._get_observation()
        done = self.state.current_step >= self.state.max_steps
        
        # Log to Data Trajectory
        self.logger.log_step(
            self.state.current_step, 
            obs.model_dump(), 
            action.model_dump(), 
            reward_value, 
            {"components": components.model_dump(), **info}
        )
        
        if done:
            self.logger.end_episode()

        return StepResponse(
            observation=obs,
            reward=reward_value,
            reward_breakdown=components,
            done=done,
            info=info
        )

    def _calculate_reward(self, current_cost: float) -> Tuple[float, RewardComponents]:
        savings = self.state.initial_cost - current_cost
        savings_percentage = savings / self.state.initial_cost if self.state.initial_cost > 0 else 0
        
        # Points
        pts_savings = savings_percentage * 10
        pts_efficiency = 0.5 if savings > 0 else 0.0 # Small bonus for any saving
        
        # Penalties
        pen_sla = 0.0
        for res in self.state.resources.values():
            if res.status != ResourceStatus.TERMINATED and res.cpu_usage > 90:
                pen_sla += 5.0
        
        # Risk penalty (e.g., resizing production instances below 20% headroom)
        pen_risk = 0.0
        
        total = pts_savings + pts_efficiency - pen_sla - pen_risk
        
        return total, RewardComponents(
            points_savings=pts_savings,
            points_efficiency=pts_efficiency,
            penalty_sla=pen_sla,
            penalty_risk=pen_risk
        )

    def _get_observation(self) -> Observation:
        alerts = []
        for res in self.state.resources.values():
            if res.status != ResourceStatus.TERMINATED and res.cpu_usage > 85:
                alerts.append(f"HIGH LOAD: {res.id} is at {res.cpu_usage:.1f}% CPU")
        
        return Observation(
            resources=list(self.state.resources.values()),
            current_hourly_cost=sum(r.cost_per_hour for r in self.state.resources.values() if r.status != ResourceStatus.TERMINATED),
            step_count=self.state.current_step,
            max_steps=self.state.max_steps,
            task_description=self.task_description,
            alerts=alerts
        )

    def get_state(self) -> State:
        return self.state
