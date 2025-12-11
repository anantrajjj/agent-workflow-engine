# Agent Workflow Engine

A minimalist, Python-based workflow engine designed to execute state-driven agent behaviors. It supports defined graphs, conditional branching, and looping.

## How to Run

1.  **Install Dependencies**
    ```bash
    pip install fastapi uvicorn
    ```

2.  **Start the Server**
    Run the following from the parent directory:
    ```bash
    uvicorn agent_engine.main:app --reload
    ```

3.  **Access API**
    - API Documentation: `http://127.0.0.1:8000/docs`
    - Verify Status: `GET /`

## Features

- **Graph-Based Execution**: Define workflows as Nodes (functions) and Edges (transitions).
- **Conditional Branching**: Dynamic path selection based on state variables (e.g., `score < 80`).
- **Looping Support**: Native support for cyclic graphs to enable retry/refinement loops.
- **State Management**: Pydantic-validated state passed between nodes.
- **Non-Blocking API**: Workflow runs are offloaded to background tasks.

## Improvements (With More Time)

- **Persistence**: Database integration (Postgres/Redis) for state durability beyond server restarts.
- **Async Execution**: Fully `async/await` compatible engine for better concurrency.
- **Distributed Workers**: Decouple the API from the execution engine using a message queue (e.g., Celery/RabbitMQ).
- **Validation**: Stricter schema validation for input/output of individual nodes.
