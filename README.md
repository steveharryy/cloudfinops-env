# CloudFinOps-Env

A real-world OpenEnv environment for training AI agents to optimize cloud infrastructure costs.

## 🚀 Overview
**CloudFinOps-Env** simulates a cloud environment where an agent acts as a FinOps Engineer. The agent is tasked with reducing hourly infrastructure costs by terminating unused resources and rightsizing over-provisioned instances while maintaining performance SLAs.

## ⚙️ Action & Observation Spaces

### Observation Space
The observation is a JSON object containing:
- `resources`: A list of all cloud resources (Instances, Storage, Buckets) with their current status, cost, and CPU/RAM usage.
- `current_hourly_cost`: Total cost per hour for all running resources.
- `alerts`: List of critical alerts (e.g., high CPU usage warnings).
- `task_description`: The objective for the current episode.

### Action Space
Discrete actions represented as JSON:
- `{"action_type": "terminate", "resource_id": "ID"}`: Completely remove a resource.
- `{"action_type": "resize", "resource_id": "ID", "new_size": "t3.medium"}`: Change the instance type.
- `{"action_type": "cleanup_orphaned"}`: Batch delete all storage volumes with status 'available'.
- `{"action_type": "no_op"}`: Do nothing for one step.

## 🎯 Tasks & Difficulty
1. **The Spring Clean (Easy)**: Identify and delete specific orphaned storage volumes.
2. **Rightsize Architect (Medium)**: Analyze metrics and downsize over-provisioned VMs.
3. **Strategic Portfolio (Hard)**: Mixed environment audit requiring both cleanup and rightsizing while preserving production stability.

## 🏆 Reward Function
- **Positive Reward**: Proportional to the cost savings achieved.
- **Negative Penalty**: Heavy penalty for SLA breaches (CPU > 90%) or terminating critical production servers.
- **Efficiency Penalty**: Small penalty per step to encourage fast decision-making.

## 🛠️ Setup & Usage

### Running with Docker
```bash
docker build -t cloudfinops-env .
docker run -p 7860:7860 cloudfinops-env
```

### Running Locally
```bash
pip install -r requirements.txt
python app.py
```

### Baseline Inference
Ensure `API_BASE_URL` is set:
```bash
python inference.py
```
