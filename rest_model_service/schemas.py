"""Schemas used by the service."""
from typing import List, Dict
from enum import Enum
from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status of the service."""

    HEALTHY = "HEALTHY"
    NOT_HEALTHY = "NOT_HEALTHY"
    UNKNOWN = "UNKNOWN"


class ReadinessStatus(str, Enum):
    """Readiness status of the service."""

    ACCEPTING_TRAFFIC = "ACCEPTING_TRAFFIC"
    REFUSING_TRAFFIC = "REFUSING_TRAFFIC"
    UNKNOWN = "UNKNOWN"


class StartupStatus(str, Enum):
    """Startup status of the service."""

    STARTED = "STARTED"
    NOT_STARTED = "NOT_STARTED"
    UNKNOWN = "UNKNOWN"


class HealthStatusResponse(BaseModel):
    """Health status response."""

    health_status: HealthStatus = Field(description="Health status of the service.")


class ReadinessStatusResponse(BaseModel):
    """Readiness status response."""

    readiness_status: ReadinessStatus = Field(description="Readiness status of the service.")


class StartupStatusResponse(BaseModel):
    """Startup status response."""

    startup_status: StartupStatus = Field(description="Startup status of the service.")


class ModelDetails(BaseModel):
    """Metadata of a model."""

    display_name: str = Field(description="The display name of the model.")
    qualified_name: str = Field(description="The qualified name of the model.")
    description: str = Field(description="The description of the model.")
    version: str = Field(description="The version of the model.")


class ModelDetailsCollection(BaseModel):
    """Collection of model details."""

    models: List[ModelDetails] = Field(description="Collection of model details.")


class ModelMetadata(ModelDetails):
    """Metadata of a model, includes all information in ModelDetails plus input and output schemas of the model."""

    input_schema: Dict = Field(description="Input schema of a model, as a JSON Schema object.")
    output_schema: Dict = Field(description="Output schema of a model, as a JSON Schema object.")


class Error(BaseModel):
    """Error details."""

    type: str = Field(description="The type of error.")
    messages: List[str] = Field(description="List of error messages.")
