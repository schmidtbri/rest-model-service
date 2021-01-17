"""Schemas used by the service."""
from typing import List
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    """Metadata of a model."""

    display_name: str = Field(description="The display name of the model.")
    qualified_name: str = Field(description="The qualified name of the model.")
    description: str = Field(description="The description of the model.")
    version: str = Field(description="The version of the model.")


class ModelMetadataCollection(BaseModel):
    """Collection of model metadata."""

    models: List[ModelMetadata] = Field(description="A collection of model description.")


class Error(BaseModel):
    """Error."""

    type: str = Field(description="The type of error.")
    message: str = Field(description="The error message.")
