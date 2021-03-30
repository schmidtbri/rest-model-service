"""Configuration for the service."""
from typing import List
from pydantic import BaseModel, Field


class Model(BaseModel):
    """Settings for a single model in the service."""

    qualified_name: str = Field(description="Qualified name of the model.")
    class_path: str = Field(description="Class path of the model class.")
    create_endpoint: bool = Field(description="Whether or not to create an endpoint for the model.")


class Configuration(BaseModel):
    """Configuration for the service."""

    service_title: str = "RESTful Model Service"
    models: List[Model]
