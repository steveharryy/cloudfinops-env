import os
import json
import time
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # No default to stay compliant
HF_TOKEN = os.getenv("HF_TOKEN") # Added for compliance

client = OpenAI(api_key=OPENAI_API_KEY)

def log_start(task_id: str, metadata: Dict[str, Any]):
    print(f"[START] {json.dumps({'task_id': task_id, 'metadata': metadata})}")

def log_step(step_idx: int, action: Dict[str, Any], observation: Dict[str, Any], reward: float):
    print(f"[STEP] {json.dumps({'step': step_idx, 'action': action, 'observation': observation, 'reward': reward})}")

def log_end(task_id: str, final_score: float, total_reward: float):
    print(f"[END] {json.dumps({'task_id': task_id, 'final_score': final_score, 'total_reward': total_reward})}")

def solve_task(task_id: str):
    # 1. Reset Env
    import requests
    resp = requests.post(f"{API_BASE_URL}/reset", json={"task_id": task_id})
    obs = resp.json()
    
    log_start(task_id, {"description": obs["task_description"]})
    
    total_reward = 0
    done = False
    step_count = 0
    
    while not done:
        # Prompt construction
        prompt = f"""
        System: You are an expert Cloud FinOps Engineer.
        Task: {obs['task_description']}
        
        Current Resources:
        {json.dumps(obs['resources'], indent=2)}
        
        Current Hourly Cost: ${obs['current_hourly_cost']:.4f}
        Alerts: {obs['alerts']}
        
        Choose an action to optimize cost without violating SLAs (CPU > 90%).
        Action must be one of:
        1. {{"action_type": "terminate", "resource_id": "ID"}}
        2. {{"action_type": "resize", "resource_id": "ID", "new_size": "t3.medium"}}
        3. {{"action_type": "cleanup_orphaned"}}
        4. {{"action_type": "no_op"}}
        
        Return ONLY the JSON action.
        """
        
        # LLM Call
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        action = json.loads(response.choices[0].message.content)
        
        # Step
        resp = requests.post(f"{API_BASE_URL}/step", json=action)
        step_data = resp.json()
        
        obs = step_data["observation"]
        reward = step_data["reward"]
        done = step_data["done"]
        total_reward += reward
        
        log_step(step_count, action, obs, reward)
        step_count += 1
        
        if done:
            final_score = step_data["info"].get("final_score", 0.0)
            log_end(task_id, final_score, total_reward)

if __name__ == "__main__":
    # Run all tasks as baseline
    tasks = ["task-1", "task-2", "task-3"]
    for tid in tasks:
        try:
            solve_task(tid)
        except Exception as e:
            print(f"Error solved {tid}: {e}")
