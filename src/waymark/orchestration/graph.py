from networkx.algorithms.connectivity.kcomponents import build_k_number_dict
from langgraph.graph import END, START, StateGraph

from waymark.orchestration.nodes import analyst_node,impact_node,replanning_node,validation_node,resource_scout_node,repair_planner_node,reviewer_node
from waymark.orchestration.state import WaymarkState

def build_graph():
    """Build and compile the Waymark worlflow."""

    graph = StateGraph(WaymarkState)

    graph.add_node("analyst",analyst_node)
    graph.add_node("impact",impact_node)
    graph.add_node("replan", replanning_node)
    graph.add_node("validate", validation_node)
    graph.add_node("resource_scout", resource_scout_node)
    graph.add_node("repair_planner", repair_planner_node)
    graph.add_node("reviewer", reviewer_node)

    graph.add_edge(START, "analyst")
    graph.add_edge("analyst", "impact")
    graph.add_edge("impact", "replan")
    graph.add_edge("replan", "validate")
    graph.add_edge("validate", "resource_scout")
    graph.add_edge("resource_scout", "repair_planner")
    graph.add_edge("repair_planner", "reviewer")
    graph.add_edge("reviewer", END)

    return graph.compile()

waymark_graph = build_graph()