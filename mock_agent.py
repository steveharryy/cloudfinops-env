import os
import json
import time
import requests
import random

BASE_URL = "http://localhost:7860"

def solve_mock_task(task_id: str):
    # 1. Reset Env
    resp = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})
    obs = resp.json()
    
    print(f"[START] {json.dumps({'task_id': task_id, 'description': obs['task_description']})}")
    
    total_reward = 0
    done = False
    step_count = 0
    
    while not done:
        # Mock Decision Logic
        if "available" in [r["status"] for r in obs["resources"]]:
            action = {"action_type": "cleanup_orphaned"}
        else:
            # Pick a random instance to resize
            instances = [r for r in obs["resources"] if r["type"] == "instance" and r["status"] != "terminated"]
            if instances:
                res_id = random.choice(instances)["id"]
                action = {"action_type": "resize", "resource_id": res_id, "new_size": "t3.medium"}
            else:
                action = {"action_type": "no_op"}
        
        # Step
        resp = requests.post(f"{BASE_URL}/step", json=action)
        step_data = resp.json()
        
        obs = step_data["observation"]
        reward = step_data["reward"]
        done = step_data["done"]
        total_reward += reward
        
        # LOG FORMAT [STEP]
        print(f"[STEP] {json.dumps({'step': step_count, 'action': action, 'reward': reward})}")
        step_count += 1
        time.sleep(0.5) # Simulate thinking
        
        if done:
            final_score = step_data["info"].get("final_score", 0.0)
            print(f"[END] {json.dumps({'task_id': task_id, 'final_score': final_score, 'total_reward': total_reward})}")

if __name__ == "__main__":
    for tid in ["task-1", "task-2"]:
        solve_mock_task(tid)
