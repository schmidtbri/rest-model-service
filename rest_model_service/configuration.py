"""Configuration for the service."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelDecorator(BaseModel):
    """Settings for a decorator for a model instance in the service."""

    class_path: str = Field(description="Class path of the decorator class.")
    configuration: Optional[Dict[Any, Any]] = Field(description="Configuration to initialize decorator instance.")


class Model(BaseModel):
    """Settings for a single model in the service."""

    qualified_name: str = Field(description="Qualified name of the model.")
    class_path: str = Field(description="Class path of the model class.")
    create_endpoint: bool = Field(description="Whether or not to create an endpoint for the model.")
    decorators: Optional[List[ModelDecorator]] = Field(description="List of decorators to attach to model.")


class Configuration(BaseModel):
    """Configuration for the service."""

    service_title: str = "RESTful Model Service"
    version: str = "0.1.0"
    description: str = ""
    models: List[Model] = Field([], description="Model configuration.")
    logging: Optional[Dict] = Field(description="Logging configuration.")
