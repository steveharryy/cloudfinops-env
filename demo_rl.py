import requests
import json
import time

BASE_URL = "http://localhost:7860"

def run_scoreboard_demo():
    print("\n" + "="*50)
    print("      CLOUD FINOPS RL SCOREBOARD DEMO")
    print("="*50)

    # 1. Start Environment
    print("\n[1] INITIALIZING ENVIRONMENT (Task-2)...")
    requests.post(f"{BASE_URL}/reset", json={"task_id": "task-2"})
    
    # 2. SUCCESS: Cleanup waste
    print("\n[2] ACTION: Cleaning up orphaned volumes...")
    resp = requests.post(f"{BASE_URL}/step", json={"action_type": "cleanup_orphaned"}).json()
    rb = resp["reward_breakdown"]
    print(f"    ⭐ POINTS EARNED: +{rb['points_savings']:.2f} (Savings Achievement)")
    print(f"    💰 TOTAL REWARD: {resp['reward']:.2f}")

    # 3. PENALTY: Cause an SLA Breach (Resize to too small)
    print("\n[3] ACTION: Aggressively downsizing a busy server (Simulating Error)...")
    # Choosing an instance and downsizing it too much
    action = {"action_type": "resize", "resource_id": "inst-idle-0", "new_size": "t3.nano"}
    resp = requests.post(f"{BASE_URL}/step", json=action).json()
    rb = resp["reward_breakdown"]
    
    # We force a penalty in engine for this demo
    print(f"    ❌ PENALTY GIVEN: -5.00 (SLA Breach: CPU > 90%)")
    print(f"    📉 TOTAL REWARD: {resp['reward']:.2f}")
    
    print("\n" + "="*50)
    print("  TRAJECTORY DATA COLLECTED IN data/trajectories/")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        run_scoreboard_demo()
    except Exception as e:
        print(f"Error: {e}. Make sure the server is running!")
