"""Configuration for the service."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelDecorator(BaseModel):
    """Settings for a decorator for a model instance in the service."""

    class_path: str = Field(description="Class path of the decorator class.")
    configuration: Optional[Dict[str, Any]] = Field(default=None, description="Configuration to initialize decorator "
                                                                              "instance.")


class MetricsConfiguration(BaseModel):
    """Configuration for metrics."""

    enabled: bool = Field(default=False, description="Enable metrics.")
    should_group_status_codes: bool = Field(default=True, description="Should status codes be grouped into `2xx`, "
                                                                      "`3xx` and so on?")
    should_ignore_untemplated: bool = Field(default=False, description="Should requests without a matching template be "
                                                                       "ignored?")
    should_group_untemplated: bool = Field(default=True, description="Should requests without a matching template "
                                                                     "be grouped to handler `none`?")
    should_round_latency_decimals: bool = Field(default=False, description="Should recorded latencies be rounded to a "
                                                                           "certain number of decimals?")
    should_respect_env_var: bool = Field(default=False, description="Should the instrumentator only work if a certain "
                                                                    "environment variable is set to `true`?")
    should_instrument_requests_inprogress: bool = Field(default=False, description="Enables a gauge that shows the "
                                                                                   "inprogress requests.")
    excluded_handlers: List[str] = Field(default=[], description="List of strings that will be compiled to regex "
                                                                 "patterns. All matches will be skipped and not "
                                                                 "instrumented.")
    body_handlers: List[str] = Field(default=[], description="List of strings that will be compiled to regex patterns. "
                                                             "All matches will be instrumented and the body will be "
                                                             "parsed.")
    round_latency_decimals: int = Field(default=4, description="Number of decimals latencies should be rounded to.")

    env_var_name: str = Field(default="ENABLE_METRICS", description="Any valid os environment variable name that will "
                                                                    "be checked for existence before instrumentation.")
    inprogress_name: str = Field(default="http_requests_inprogress",
                                 description="Name of the gauge. Defaults to "
                                             "`http_requests_inprogress`. Ignored unless "
                                             "`should_instrument_requests_inprogress` is `True`.")
    inprogress_labels: bool = Field(default=False, description="Should labels `method` and `handler` be part of the "
                                                               "inprogress label? Ignored unless "
                                                               "`should_instrument_requests_inprogress` is `True`. "
                                                               "Defaults to `False`.")


class Model(BaseModel):
    """Settings for a single model in the service."""

    class_path: str = Field(description="Class path of the model class.")
    create_endpoint: bool = Field(description="Whether or not to create an endpoint for the model.")
    decorators: Optional[List[ModelDecorator]] = Field(default=None, description="List of decorators to attach to "
                                                                                 "model.")
    configuration: Optional[Dict[str, Any]] = Field(default=None, description="Configuration to initialize model "
                                                                              "instance.")


class ServiceConfiguration(BaseModel):
    """Configuration for the service."""

    service_title: str = "RESTful Model Service"
    version: str = "0.1.0"
    description: str = ""
    models: List[Model] = Field(default=[], description="Model configuration.")
    logging: Optional[Dict] = Field(default=None, description="Logging configuration.")
    metrics: Optional[MetricsConfiguration] = Field(default=None, description="Metrics configuration.")
