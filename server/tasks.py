from typing import List
from .models import Resource, ResourceType, ResourceStatus
from .engine import INSTANCE_TYPES

def get_task_1_resources() -> List[Resource]:
    """Task 1: The Spring Clean (Easy) - Delete 5 orphaned volumes."""
    resources = []
    # 5 Orphaned Volumes
    for i in range(5):
        resources.append(Resource(
            id=f"vol-{i}",
            name=f"Backup-Vol-{i}",
            type=ResourceType.STORAGE,
            status=ResourceStatus.AVAILABLE,
            cost_per_hour=0.08,  # $0.08/hr
            metadata={"size_gb": 100}
        ))
    # 2 Active Instances (Keep these)
    resources.append(Resource(
        id="inst-active-1",
        name="Web-Server-1",
        type=ResourceType.INSTANCE,
        status=ResourceStatus.RUNNING,
        cost_per_hour=0.096,
        cpu_usage=45.0,
        metadata={"instance_type": "m5.large"}
    ))
    return resources

def get_task_2_resources() -> List[Resource]:
    """Task 2: Rightsize Architect (Medium) - Downsize 5 over-provisioned VMs."""
    resources = []
    # 5 Idle but Large Instances
    for i in range(5):
        resources.append(Resource(
            id=f"inst-idle-{i}",
            name=f"Dev-Workstation-{i}",
            type=ResourceType.INSTANCE,
            status=ResourceStatus.RUNNING,
            cost_per_hour=0.384, # m5.2xlarge
            cpu_usage=2.0,       # 2% CPU
            metadata={"instance_type": "m5.2xlarge"}
        ))
    return resources

def get_task_3_resources() -> List[Resource]:
    """Task 3: Strategic Portfolio (Hard) - Mixed environment."""
    resources = []
    # 3 High Load (Don't touch)
    for i in range(3):
        resources.append(Resource(
            id=f"inst-prod-{i}",
            name=f"Prod-DB-{i}",
            type=ResourceType.INSTANCE,
            status=ResourceStatus.RUNNING,
            cost_per_hour=0.384,
            cpu_usage=80.0,
            metadata={"instance_type": "m5.2xlarge"}
        ))
    # 3 Over-provisioned
    for i in range(3):
        resources.append(Resource(
            id=f"inst-staging-{i}",
            name=f"Staging-Server-{i}",
            type=ResourceType.INSTANCE,
            status=ResourceStatus.RUNNING,
            cost_per_hour=0.192,
            cpu_usage=1.0,
            metadata={"instance_type": "m5.xlarge"}
        ))
    # 3 Orphaned volumes
    for i in range(3):
        resources.append(Resource(
            id=f"vol-orph-{i}",
            name=f"Draft-Volume-{i}",
            type=ResourceType.STORAGE,
            status=ResourceStatus.AVAILABLE,
            cost_per_hour=0.05
        ))
    return resources

TASKS = {
    "task-1": {
        "description": "Delete all orphaned storage volumes (status: 'available') to reduce waste.",
        "factory": get_task_1_resources,
        "max_steps": 5
    },
    "task-2": {
        "description": "Identify instances with <10% CPU usage and downsize them to 't3.medium' to save costs without overloading them.",
        "factory": get_task_2_resources,
        "max_steps": 10
    },
    "task-3": {
        "description": "Comprehensive Audit: Clean up orphaned volumes AND downsize underutilized instances while ensuring production high-load servers remain stable.",
        "factory": get_task_3_resources,
        "max_steps": 15
    }
}
