import random
from agent_engine.schemas import GraphDefinition, Node, Edge, Condition

# -------------------------------------------------------------------------
# Dummy Data Processing Functions
# -------------------------------------------------------------------------
def extract_code(state: dict) -> dict:
    """Simulate code extraction."""
    print("  [Action] Extracting code...")
    return {"code": "def foo():\n    print('hello')\n    pass", "lines": 3}

def analyze_complexity(state: dict) -> dict:
    """Simulate complexity analysis."""
    print("  [Action] Analyzing complexity...")
    # Simulate a dummy complexity score
    return {"complexity": 5}

def check_style(state: dict) -> dict:
    """Simulate style checking with a random score."""
    print("  [Action] Checking style...")
    # Random score to demonstrate looping behavior eventually passing
    current_score = state.get("quality_score", 0)
    
    # If we are fixing, improve the score
    if state.get("fix_attempts", 0) > 0:
        new_score = min(100, current_score + 20)
    else:
        new_score = 65  # Initial failing score to force at least one loop
        
    print(f"    -> Style Score: {new_score}")
    return {"quality_score": new_score}

def auto_fix(state: dict) -> dict:
    """Simulate auto-fixing the code."""
    print("  [Action] Auto-fixing code modules...")
    attempts = state.get("fix_attempts", 0) + 1
    return {"fix_attempts": attempts, "status": "fixing"}

# -------------------------------------------------------------------------
# Graph Definition
# -------------------------------------------------------------------------
nodes = [
    Node(id="Extract", function_name="extract_code"),
    Node(id="Analyze", function_name="analyze_complexity"),
    Node(id="CheckStyle", function_name="check_style"),
    Node(id="AutoFix", function_name="auto_fix"),
]

edges = [
    # Linear flow
    Edge(from_node="Extract", to_node="Analyze"),
    Edge(from_node="Analyze", to_node="CheckStyle"),
    
    # Conditional Branching / Looping
    # If score < 80, go to AutoFix (Loop start)
    Edge(
        from_node="CheckStyle",
        to_node="AutoFix",
        condition=Condition(variable="quality_score", operator="<", value=80)
    ),
    # Else (implicitly >= 80 owing to priority), go to End
    Edge(from_node="CheckStyle", to_node="End"),
    
    # Loop back
    Edge(from_node="AutoFix", to_node="CheckStyle"),
]

code_review_graph = GraphDefinition(
    id="code_review_v1",
    start_node="Extract",
    nodes=nodes,
    edges=edges
)

# Registry helper
def register_sample_workflow(engine):
    engine.register_function("extract_code", extract_code)
    engine.register_function("analyze_complexity", analyze_complexity)
    engine.register_function("check_style", check_style)
    engine.register_function("auto_fix", auto_fix)
    engine.register_graph(code_review_graph)
