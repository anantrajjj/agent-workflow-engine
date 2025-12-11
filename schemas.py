from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field

# -------------------------------------------------------------------------
# State Management
# -------------------------------------------------------------------------
class WorkflowState(BaseModel):
    """
    Represents the state of a workflow run.
    It wraps a flexible dictionary that holds all data.
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="The dynamic state data of the workflow.")

# -------------------------------------------------------------------------
# Graph Components
# -------------------------------------------------------------------------
class Node(BaseModel):
    """
    A single step in the workflow.
    """
    id: str = Field(..., description="Unique identifier for the node.")
    function_name: str = Field(..., description="Name of the function to execute for this node. Must be registered.")

class Condition(BaseModel):
    """
    A condition to evaluate for branching.
    """
    variable: str = Field(..., description="State variable to check.")
    operator: Literal[">", "<", ">=", "<=", "==", "!="] = Field(..., description="Comparison operator.")
    value: Any = Field(..., description="Value to compare against.")

class Edge(BaseModel):
    """
    A transition between nodes.
    """
    from_node: str = Field(..., description="Source node ID.")
    to_node: str = Field(..., description="Destination node ID.")
    condition: Optional[Condition] = Field(None, description="Optional condition for this transition.")

class GraphDefinition(BaseModel):
    """
    Complete definition of a workflow graph.
    """
    id: str = Field(..., description="Unique identifier for the graph.")
    start_node: str = Field(..., description="The ID of the starting node.")
    nodes: List[Node] = Field(..., description="List of all nodes in the graph.")
    edges: List[Edge] = Field(..., description="List of all edges (transitions).")

# -------------------------------------------------------------------------
# API Response Models
# -------------------------------------------------------------------------
class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)

class WorkflowRun(BaseModel):
    run_id: str
    graph_id: str
    status: Literal["pending", "running", "completed", "failed"]
    state: Dict[str, Any]
    history: List[str] = Field(default_factory=list, description="Sequence of nodes visited.")
    error: Optional[str] = None
