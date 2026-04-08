import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

class TrajectoryLogger:
    def __init__(self, log_dir: str = "data/trajectories"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_episode_id = None
        self.current_log_file = None
        self.steps = []

    def start_episode(self, task_id: str):
        self.current_episode_id = f"ep_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.current_log_file = os.path.join(self.log_dir, f"{self.current_episode_id}.jsonl")
        self.steps = []

    def log_step(self, step_idx: int, observation: Dict[str, Any], action: Dict[str, Any], reward: float, info: Dict[str, Any]):
        if not self.current_log_file:
            return

        step_record = {
            "episode_id": self.current_episode_id,
            "step": step_idx,
            "timestamp": datetime.now().isoformat(),
            "observation": observation,
            "action": action,
            "reward": reward,
            "info": info
        }
        
        with open(self.current_log_file, "a") as f:
            f.write(json.dumps(step_record) + "\n")
        
        self.steps.append(step_record)

    def end_episode(self):
        self.current_episode_id = None
        self.current_log_file = None
        self.steps = []
