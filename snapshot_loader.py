import json
import os
from typing import List, Dict, Any
from models import Resource, ResourceType, ResourceStatus

class SnapshotLoader:
    def __init__(self, snapshot_dir: str = "data/snapshots"):
        self.snapshot_dir = snapshot_dir

    def load_snapshot(self, filename: str) -> List[Resource]:
        """Loads a list of resources from a JSON snapshot file."""
        filepath = os.path.join(self.snapshot_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Snapshot {filename} not found in {self.snapshot_dir}")
        
        with open(filepath, "r") as f:
            data = json.load(f)
            
        resources = []
        # Support both flat list or dict with 'resources' key
        raw_resources = data.get("resources", data) if isinstance(data, dict) else data
        
        for r_data in raw_resources:
            resources.append(Resource(
                id=r_data.get("id", "res-" + os.urandom(4).hex()),
                name=r_data.get("name", "Unnamed Resource"),
                type=ResourceType(r_data.get("type", "instance")),
                status=ResourceStatus(r_data.get("status", "running")),
                cost_per_hour=float(r_data.get("cost_per_hour", 0.1)),
                cpu_usage=float(r_data.get("cpu_usage", 5.0)),
                ram_usage=float(r_data.get("ram_usage", 5.0)),
                metadata=r_data.get("metadata", {})
            ))
        return resources

    def list_snapshots(self) -> List[str]:
        return [f for f in os.listdir(self.snapshot_dir) if f.endswith(".json")]
