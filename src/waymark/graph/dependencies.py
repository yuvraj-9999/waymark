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


def has_circular_dependencies(plan: ProjectPlan) -> bool:
    """Return whether the project's dependency graph contains a cycle."""

    graph = build_dependency_graph(plan)

    return not nx.is_directed_acyclic_graph(graph)


def get_downstream_tasks(plan: ProjectPlan, task_id: str) -> set[str]:
    """Return all tasks downstream of the specified task."""

    graph = build_dependency_graph(plan)

    if task_id not in graph:
        raise ValueError(f"Unknown task ID: {task_id}")

    return nx.descendants(graph, task_id)
