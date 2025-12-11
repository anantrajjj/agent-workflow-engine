from fastapi import FastAPI, HTTPException, BackgroundTasks
from agent_engine.schemas import GraphDefinition, RunRequest, WorkflowRun
from agent_engine.engine import WorkflowEngine
from agent_engine.workflow import register_sample_workflow

app = FastAPI(title="Agent Workflow Engine", version="0.1.0")

# Initialize Engine
engine = WorkflowEngine()

# Register the sample "Code Review" workflow on startup
register_sample_workflow(engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agent Workflow Engine. Docs at /docs"}

@app.post("/graph/create")
def create_graph(graph: GraphDefinition):
    """
    Register a new workflow graph structure.
    """
    try:
        engine.register_graph(graph)
        return {"status": "success", "graph_id": graph.id, "message": "Graph registered."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/graph/run", response_model=WorkflowRun)
def run_workflow(request: RunRequest, background_tasks: BackgroundTasks):
    """
    Trigger a workflow execution.
    Runs in the background (async logic simulated via BackgroundTasks) to keep the API responsive.
    """
    try:
        run_id = engine.create_run(request.graph_id, request.initial_state)
        
        # Schedule the actual execution in the background
        background_tasks.add_task(engine.execute_run_sync, run_id)
        
        # Return the initial pending state immediately
        run = engine.get_run(run_id)
        return run
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/state/{run_id}", response_model=WorkflowRun)
def get_run_state(run_id: str):
    """
    Fetch the current state and history of a specific workflow run.
    """
    run = engine.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return run
