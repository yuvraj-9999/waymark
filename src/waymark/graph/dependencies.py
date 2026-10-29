import networkx as nx

from waymark.schemas.plan import ProjectPlan


def build_dependency_graph(plan: ProjectPlan) -> nx.DiGraph:
    """Build a directed graph from a project's task dependencies."""

    graph = nx.DiGraph()

    for task in plan.tasks:
        graph.add_node(task.id)

    for task in plan.tasks:
        for dependency_id in task.dependencies:
            graph.add_edge(dependency_id, task.id)

    return graph
