import os
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from models import Action, StepResponse, Observation, State
from engine import CloudFinOpsEngine
from tasks import TASKS
from graders import GRADERS
from snapshot_loader import SnapshotLoader

app = FastAPI(title="CloudFinOps-Env", description="Data-Driven OpenEnv for Cost Optimization")
engine = CloudFinOpsEngine()
snapshot_loader = SnapshotLoader()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to CloudFinOps OpenEnv",
        "status": "online",
        "endpoints": ["/reset", "/step", "/tasks", "/state"]
    }

@app.get("/tasks")
async def list_tasks():
    descriptions = {tid: t["description"] for tid, t in TASKS.items()}
    # Add snapshots as dynamic tasks
    snapshots = snapshot_loader.list_snapshots()
    for s in snapshots:
        descriptions[f"snapshot:{s}"] = f"Optimize custom footprint from snapshot: {s}"
    return descriptions

@app.post("/reset", response_model=Observation)
async def reset(data: Dict[str, Any] = Body(default={})):
    task_id = data.get("task_id", "task-1")
    
    if task_id.startswith("snapshot:"):
        filename = task_id.replace("snapshot:", "")
        try:
            resources = snapshot_loader.load_snapshot(filename)
            desc = f"Optimize cost for resources loaded from {filename}"
            obs = engine.reset(task_id=task_id, resources=resources, task_desc=desc, max_steps=20)
            return obs
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_cfg = TASKS[task_id]
    resources = task_cfg["factory"]()
    obs = engine.reset(
        task_id=task_id,
        resources=resources,
        task_desc=task_cfg["description"],
        max_steps=task_cfg["max_steps"]
    )
    return obs

@app.post("/step", response_model=StepResponse)
async def step(action: Action):
    if not engine.get_state():
        raise HTTPException(status_code=400, detail="Environment not reset")
    
    response = engine.step(action)
    
    if response.done:
        task_id = engine.get_state().task_id
        if not task_id.startswith("snapshot:"):
            graders_func = GRADERS.get(task_id)
            if graders_func:
                response.info["final_score"] = graders_func(engine.get_state())
            
    return response

@app.post("/upload_snapshot")
async def upload_snapshot(file: UploadFile = File(...)):
    """Upload a real-world infrastructure JSON snapshot."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON snapshots allowed")
    
    file_path = os.path.join("data/snapshots", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    return {"message": f"Snapshot {file.filename} uploaded successfully", "task_id": f"snapshot:{file.filename}"}

@app.get("/state", response_model=State)
async def get_state():
    state = engine.get_state()
    if not state:
        raise HTTPException(status_code=400, detail="Environment not reset")
    return state

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
