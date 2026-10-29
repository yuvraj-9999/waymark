import pytest
from pydantic import ValidationError

from waymark.schemas.disruption import Disruption


def test_disruption_accepts_valid_data():
    disruption = Disruption(
        task_id="book_venue",
        delay_days=2,
        reason="Original venue became unavailable",
    )

    assert disruption.task_id == "book_venue"
    assert disruption.delay_days == 2


def test_disruption_rejects_zero_delay():
    with pytest.raises(ValidationError):
        Disruption(
            task_id="book_venue",
            delay_days=0,
            reason="Venue unavailable",
        )


def test_disruption_rejects_negative_delay():
    with pytest.raises(ValidationError):
        Disruption(
            task_id="book_venue",
            delay_days=-1,
            reason="Venue unavailable",
        )


def test_disruption_rejects_blank_task_id():
    with pytest.raises(ValidationError):
        Disruption(
            task_id="   ",
            delay_days=2,
            reason="Venue unavailable",
        )


def test_disruption_rejects_blank_reason():
    with pytest.raises(ValidationError):
        Disruption(
            task_id="book_venue",
            delay_days=2,
            reason="   ",
        )


def test_disruption_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        Disruption(
            task_id="book_venue",
            delay_days=2,
            reason="Venue unavailable",
            severity="high",
        )
