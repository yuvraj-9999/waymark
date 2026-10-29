import pytest
from pydantic import ValidationError

from waymark.schemas.task import Task


def test_task_accepts_valid_data():
    task = Task(
        id="book_venue",
        name="Book venue",
        duration_days=1,
    )

    assert task.id == "book_venue"
    assert task.duration_days == 1
    assert task.dependencies == []


def test_task_rejects_zero_duration():
    with pytest.raises(ValidationError):
        Task(
            id="book_venue",
            name="Book venue",
            duration_days=0,
        )


def test_task_rejects_self_dependency():
    with pytest.raises(ValidationError):
        Task(
            id="book_venue",
            name="Book venue",
            duration_days=1,
            dependencies=["book_venue"],
        )


def test_task_rejects_duplicate_dependencies():
    with pytest.raises(ValidationError, match="Duplicate dependencies"):
        Task(
            id="publish",
            name="Publish schedule",
            duration_days=1,
            dependencies=["venue", "venue"],
        )


def test_task_rejects_blank_name():
    with pytest.raises(ValidationError):
        Task(
            id="book_venue",
            name="   ",
            duration_days=1,
        )


def test_task_rejects_blank_id():
    with pytest.raises(ValidationError):
        Task(
            id=" ",
            name="Book venue",
            duration_days=1,
        )


def test_task_preserves_surrounding_spaces_in_valid_name():
    task = Task(
        id="book_venue",
        name=" Book venue ",
        duration_days=1,
    )

    assert task.name == " Book venue "
