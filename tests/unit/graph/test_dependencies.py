from datetime import date

from waymark.graph.dependencies import build_dependency_graph
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.task import Task


def test_graph_contains_all_tasks():
    plan = ProjectPlan(
        id="tech_fest",
        name="College Tech Fest",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="venue", name="Book venue", duration_days=1),
            Task(id="posters", name="Design posters", duration_days=2),
        ],
    )

    graph = build_dependency_graph(plan)

    assert set(graph.nodes) == {"venue", "posters"}


def test_graph_edges_follow_dependency_direction():
    plan = ProjectPlan(
        id="tech_fest",
        name="College Tech Fest",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="venue", name="Book venue", duration_days=1),
            Task(
                id="setup",
                name="Set up equipment",
                duration_days=2,
                dependencies=["venue"],
            ),
        ],
    )

    graph = build_dependency_graph(plan)

    assert graph.has_edge("venue", "setup")
    assert not graph.has_edge("setup", "venue")


def test_graph_preserves_multiple_dependencies():
    plan = ProjectPlan(
        id="tech_fest",
        name="College Tech Fest",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="venue", name="Book venue", duration_days=1),
            Task(id="speakers", name="Confirm speakers", duration_days=2),
            Task(
                id="publish",
                name="Publish schedule",
                duration_days=1,
                dependencies=["venue", "speakers"],
            ),
        ],
    )

    graph = build_dependency_graph(plan)

    assert graph.has_edge("venue", "publish")
    assert graph.has_edge("speakers", "publish")
