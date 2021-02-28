"""Settings models for the service."""
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings for the service."""

    service_title: str = "RESTful Model Service"
    models: List[str]
