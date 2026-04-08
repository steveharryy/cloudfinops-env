from .models import State, ResourceStatus, ResourceType

def grade_task_1(final_state: State) -> float:
    """Check if all orphaned volumes are terminated."""
    orphaned_vols = [r for r in final_state.resources.values() if r.name.startswith("Backup-Vol")]
    if not orphaned_vols: return 0.0
    terminated_count = sum(1 for r in orphaned_vols if r.status == ResourceStatus.TERMINATED)
    return terminated_count / len(orphaned_vols)

def grade_task_2(final_state: State) -> float:
    """Check if all idle instances are downsized and no SLA breach."""
    idle_instances = [r for r in final_state.resources.values() if r.id.startswith("inst-idle")]
    if not idle_instances: return 0.0
    
    rightsized_count = 0
    sla_breach = False
    
    for r in final_state.resources.values():
        if r.status != ResourceStatus.TERMINATED and r.cpu_usage > 90:
            sla_breach = True
        if r.id.startswith("inst-idle") and r.metadata.get("instance_type") == "t3.medium":
            rightsized_count += 1
            
    score = rightsized_count / len(idle_instances)
    return score if not sla_breach else score * 0.2 # Heavy penalty for SLA breach

def grade_task_3(final_state: State) -> float:
    """Check mixed goals and prod stability."""
    stg_instances = [r for r in final_state.resources.values() if "staging" in r.id]
    orph_vols = [r for r in final_state.resources.values() if "vol-orph" in r.id]
    prod_instances = [r for r in final_state.resources.values() if "prod" in r.id]
    
    # 1. Staging rightsized?
    rightsized = sum(1 for r in stg_instances if r.metadata.get("instance_type") == "t3.medium") / len(stg_instances)
    # 2. Volumes cleaned?
    cleaned = sum(1 for r in orph_vols if r.status == ResourceStatus.TERMINATED) / len(orph_vols)
    # 3. Prod stability?
    prod_ok = all(r.status == ResourceStatus.RUNNING for r in prod_instances)
    # 4. Global SLA?
    no_sla_breach = all(r.cpu_usage <= 90 for r in final_state.resources.values() if r.status != ResourceStatus.TERMINATED)
    
    base_score = (rightsized + cleaned) / 2
    if not prod_ok: return 0.0
    return base_score if no_sla_breach else base_score * 0.5

GRADERS = {
    "task-1": grade_task_1,
    "task-2": grade_task_2,
    "task-3": grade_task_3
}
