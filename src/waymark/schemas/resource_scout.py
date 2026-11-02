from pydantic import BaseModel, ConfigDict, Field, field_validator

from waymark.schemas.validators import reject_blank_string


class ResourceSearchRequest(BaseModel):
    """Structured decision about whether resource discovery is needed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    search_required: bool
    resource_type: str = Field(default="")
    search_query: str = Field(default="")
    location: str = Field(default="")
    explanation: str = Field(min_length=1)

    _validate_strings = field_validator(
        "explanation",
    )(reject_blank_string)


class ResourceCandidate(BaseModel):
    """A resource candidate discovered through web search."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    snippet: str = Field(default="")
    source: str = Field(default="")
    availability_confirmed: bool = False


class ResourceScoutResult(BaseModel):
    """Final result of resource discovery."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    search_performed: bool
    search_query: str = ""
    explanation: str = Field(min_length=1)
    candidates: list[ResourceCandidate] = Field(default_factory=list)
