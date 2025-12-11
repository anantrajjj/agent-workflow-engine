import time
from fastapi.testclient import TestClient
from agent_engine.main import app

client = TestClient(app)

def test_code_review_workflow():
    print("\n--- Starting End-to-End Test ---")
    
    # 1. Start a run for the pre-registered 'code_review_v1' graph
    print("1. Triggering 'code_review_v1' workflow...")
    response = client.post("/graph/run", json={
        "graph_id": "code_review_v1",
        "initial_state": {"filename": "test.py"}
    })
    
    if response.status_code != 200:
        print(f"FAILED to start run: {response.text}")
        return
    
    run_data = response.json()
    run_id = run_data["run_id"]
    print(f"   -> Started Run ID: {run_id}")
    
    # 2. Poll for completion
    print("2. Polling for completion...")
    status = "running"
    while status in ["pending", "running"]:
        time.sleep(0.5)
        resp = client.get(f"/graph/state/{run_id}")
        data = resp.json()
        status = data["status"]
        print(f"   -> Status: {status}, Current State: {data.get('state')}")
        
        if status == "failed":
            print(f"FAILED Run: {data.get('error')}")
            return
            
    # 3. Verify History and Logic
    print("3. Verifying Execution History...")
    final_data = client.get(f"/graph/state/{run_id}").json()
    history = final_data["history"]
    state = final_data["state"]
    
    print(f"   -> Final History: {history}")
    print(f"   -> Final State: {state}")
    
    # Expected: Extract -> Analyze -> CheckStyle -> AutoFix -> CheckStyle -> End (roughly)
    # The loop happens because initial score is 65 (<80), AutoFix adds +20 -> 85, then CheckStyle passes.
    
    assert "Extract" in history
    assert "Analyze" in history
    assert "CheckStyle" in history
    assert "AutoFix" in history
    
    # Check looping: CheckStyle should appear at least twice
    check_style_count = history.count("CheckStyle")
    if check_style_count >= 2:
        print("   [SUCCESS] Looping verified (CheckStyle visited multiple times).")
    else:
        print("   [FAILURE] Loop not detected.")
    
    if state["quality_score"] >= 80:
         print("   [SUCCESS] Final quality score met criteria.")
    else:
         print("   [FAILURE] Final quality score too low.")

if __name__ == "__main__":
    test_code_review_workflow()
