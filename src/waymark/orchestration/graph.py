from langgraph.graph import END, START, StateGraph

from waymark.orchestration.nodes import (
    analyst_node,
    artifact_node,
    execution_node,
    impact_node,
    repair_planner_node,
    replanning_node,
    resource_scout_node,
    reviewer_node,
    validation_node,
)
from waymark.orchestration.state import WaymarkState


def route_after_review(state: WaymarkState) -> str:
    """Route the workflow based on the reviewer's approval and retry limit."""
    if state["approved"]:
        return "execution"

    if state.get("revision_count", 0) < 2:
        return "retry"

    return "end"


def build_graph():
    """Build and compile the Waymark worlflow."""

    graph = StateGraph(WaymarkState)

    graph.add_node("analyst", analyst_node)
    graph.add_node("impact", impact_node)
    graph.add_node("replan", replanning_node)
    graph.add_node("validate", validation_node)
    graph.add_node("resource_scout", resource_scout_node)
    graph.add_node("repair_planner", repair_planner_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("execution", execution_node)
    graph.add_node("artifacts", artifact_node)

    graph.add_edge(START, "analyst")
    graph.add_edge("analyst", "impact")
    graph.add_edge("impact", "replan")
    graph.add_edge("replan", "validate")
    graph.add_edge("validate", "resource_scout")
    graph.add_edge("resource_scout", "repair_planner")
    graph.add_edge("repair_planner", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "execution": "execution",
            "retry": "repair_planner",
            "end": END,
        },
    )

    graph.add_edge("execution", "artifacts")
    graph.add_edge("artifacts", END)

    return graph.compile()


waymark_graph = build_graph()
