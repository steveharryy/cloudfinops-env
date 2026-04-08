import requests
import os
import json

BASE_URL = "http://localhost:7860"

def test_data_expansion():
    print("Testing Snapshot Loading...")
    # 1. Reset from snapshot
    reset_resp = requests.post(f"{BASE_URL}/reset", json={"task_id": "snapshot:sample_infra.json"})
    if reset_resp.status_code != 200:
        print(f"FAILED reset: {reset_resp.text}")
        return
    
    try:
        obs = reset_resp.json()
    except Exception as e:
        print(f"FAILED to parse JSON reset_resp: {e}")
        print(f"Response text: {reset_resp.text}")
        return
    print(f"Loaded snapshot. Current cost: ${obs['current_hourly_cost']:.2f}")
    
    # 2. Take a step
    print("\nTesting Step & Points/Penalties...")
    action = {"action_type": "cleanup_orphaned"}
    step_resp = requests.post(f"{BASE_URL}/step", json=action)
    step_data = step_resp.json()
    
    rb = step_data["reward_breakdown"]
    print(f"Reward Breakdown: Points={rb['points_savings']} | Penalties={rb['penalty_sla']}")
    
    # 3. Check Trajectory Logs
    print("\nVerifying Data Collection (Logs)...")
    log_dir = "data/trajectories"
    logs = os.listdir(log_dir)
    if logs:
        print(f"Success! Found {len(logs)} trajectory logs.")
        latest_log = os.path.join(log_dir, sorted(logs)[-1])
        with open(latest_log, "r") as f:
            first_line = json.loads(f.readline())
            print(f"Log Sample (Step 0 Episode ID): {first_line['episode_id']}")
    else:
        print("FAILED: No logs found in data/trajectories")

if __name__ == "__main__":
    test_data_expansion()
