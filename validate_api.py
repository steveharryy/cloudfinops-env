import requests
import json

BASE_URL = "http://localhost:7860"

def test_workflow():
    print("Testing /tasks...")
    tasks = requests.get(f"{BASE_URL}/tasks").json()
    print(f"Available tasks: {list(tasks.keys())}")
    
    print("\nTesting /reset for task-1...")
    reset_resp = requests.post(f"{BASE_URL}/reset", json={"task_id": "task-1"})
    print(f"Reset response status: {reset_resp.status_code}")
    obs = reset_resp.json()
    print(f"Initial Hourly Cost: ${obs['current_hourly_cost']:.2f}")
    
    print("\nTesting /step with cleanup_orphaned...")
    action = {"action_type": "cleanup_orphaned"}
    step_resp = requests.post(f"{BASE_URL}/step", json=action)
    print(f"Step response status: {step_resp.status_code}")
    step_data = step_resp.json()
    print(f"New Hourly Cost: ${step_data['observation']['current_hourly_cost']:.2f}")
    print(f"Reward: {step_data['reward']}")
    print(f"Done: {step_data['done']}")
    
    print("\nTesting /state...")
    state_resp = requests.get(f"{BASE_URL}/state")
    print(f"State response status: {state_resp.status_code}")
    # print(json.dumps(state_resp.json(), indent=2))

if __name__ == "__main__":
    try:
        test_workflow()
        print("\n✅ API Validation Passed!")
    except Exception as e:
        print(f"\n❌ API Validation Failed: {e}")
