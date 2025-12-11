import time
import uuid
import logging
from typing import Callable, Dict, Any, Optional

from agent_engine.schemas import GraphDefinition, WorkflowRun, Condition, Node, Edge

# Configure simpler logging for clarity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self, max_steps: int = 50):
        self._graphs: Dict[str, GraphDefinition] = {}
        self._functions: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._runs: Dict[str, WorkflowRun] = {}
        self.max_steps = max_steps

    def register_graph(self, graph: GraphDefinition):
        """Register a new graph definition."""
        self._graphs[graph.id] = graph
        logger.info(f"Registered graph: {graph.id}")

    def register_function(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Register a python function to be used as a node action."""
        self._functions[name] = func
        logger.info(f"Registered function: {name}")

    def create_run(self, graph_id: str, initial_state: Dict[str, Any]) -> str:
        """Initialize a new workflow run."""
        if graph_id not in self._graphs:
            raise ValueError(f"Graph '{graph_id}' not found.")
        
        run_id = str(uuid.uuid4())
        run = WorkflowRun(
            run_id=run_id,
            graph_id=graph_id,
            status="pending",
            state=initial_state
        )
        self._runs[run_id] = run
        return run_id

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        return self._runs.get(run_id)

    def _evaluate_condition(self, state: Dict[str, Any], condition: Condition) -> bool:
        """Evaluate a branching condition against the current state."""
        val = state.get(condition.variable)
        target = condition.value
        op = condition.operator

        if val is None:
            return False

        if op == "==": return val == target
        if op == "!=": return val != target
        if op == ">": return val > target
        if op == "<": return val < target
        if op == ">=": return val >= target
        if op == "<=": return val <= target
        return False

    def _find_next_node(self, graph: GraphDefinition, current_node_id: str, state: Dict[str, Any]) -> Optional[str]:
        """Determine the next node based on edges and conditions."""
        possible_edges = [e for e in graph.edges if e.from_node == current_node_id]
        
        # Priority 1: Check conditional edges
        for edge in possible_edges:
            if edge.condition:
                if self._evaluate_condition(state, edge.condition):
                    return edge.to_node
        
        # Priority 2: Check unconditional edges (default path)
        for edge in possible_edges:
            if not edge.condition:
                return edge.to_node
                
        # No valid transition found -> End of workflow
        return None

    def execute_run_sync(self, run_id: str):
        """
        Synchronously execute the workflow run.
        In a real production system, this logic would likely be decoupled from the HTTP request,
        but for this assignment, it demonstrates the state machine loop clearly.
        """
        run = self._runs.get(run_id)
        if not run:
            logger.error(f"Run {run_id} not found.")
            return

        run.status = "running"
        graph = self._graphs[run.graph_id]
        current_node_id = graph.start_node

        try:
            steps_executed = 0
            while current_node_id:
                if steps_executed >= self.max_steps:
                    raise RuntimeError(f"Max steps ({self.max_steps}) exceeded. Possible infinite loop.")

                run.history.append(current_node_id)
                logger.info(f"Run {run_id} - Step {steps_executed + 1} - Executing Node: {current_node_id}")

                # 1. Find the node definition
                node_def = next((n for n in graph.nodes if n.id == current_node_id), None)
                if not node_def:
                    raise ValueError(f"Node {current_node_id} definition missing in graph {graph.id}")

                # 2. Execute the node's function
                func = self._functions.get(node_def.function_name)
                if not func:
                    raise ValueError(f"Function {node_def.function_name} not registered.")
                
                # Update state with function result
                # Ideally, we pass a copy or immutable view if we wanted strict purity, 
                # but for this MVP, we pass the ref.
                new_state_updates = func(run.state)
                run.state.update(new_state_updates)

                # 3. Determine transition
                next_node_id = self._find_next_node(graph, current_node_id, run.state)
                
                # Check for explicit "End" node convention or just no edges
                if next_node_id == "End":
                    current_node_id = None
                else:
                    current_node_id = next_node_id
                
                steps_executed += 1
            
            run.status = "completed"
            logger.info(f"Run {run_id} completed successfully in {steps_executed} steps.")

        except Exception as e:
            run.status = "failed"
            run.error = str(e)
            logger.exception(f"Run {run_id} failed: {e}")
