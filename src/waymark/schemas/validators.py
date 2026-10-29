def reject_blank_string(value: str) -> str:
    """Reject strings that are empty or contain only whitespace."""

    if not value.strip():
        raise ValueError("Value cannot be empty or whitespace.")

    return value
