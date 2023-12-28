"""Main entry point for the service."""
import os
from os import path
import logging.config
import yaml

from rest_model_service.configuration import ServiceConfiguration
from rest_model_service.helpers import create_app

try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ImportError:
    Instrumentator = None


logger = logging.getLogger(__name__)


# getting the path to the configuration file
# defaults to "rest_config.yaml" in the current directory if the path not provided
if "REST_CONFIG" in os.environ:
    file_path = os.environ["REST_CONFIG"]
else:
    file_path = "rest_config.yaml"

# loading the configuration
if path.exists(file_path) and path.isfile(file_path):
    with open(file_path) as file:
        configuration_dict = yaml.full_load(file)

    # loading configuration
    configuration = ServiceConfiguration(**configuration_dict)

    # creating app
    app = create_app(configuration, wait_for_model_creation=False)

    # instrumenting the app if metrics are enabled
    if Instrumentator is None and configuration.metrics is not None and configuration.metrics.enabled:
        logger.critical("Cannot enable metrics because optional dependency 'metrics' is not installed.")
        raise RuntimeError("Cannot start service with metrics without optional dependencies.")

    if configuration.metrics is not None and configuration.metrics.enabled:
        Instrumentator(**configuration.metrics.model_dump(exclude=["enabled"])).instrument(app).expose(
            app, include_in_schema=False)
else:
    # if there is no configuration file, or it is not found, then raise an exception
    raise ValueError("Could not find configuration file '{}', service has no models loaded.".format(file_path))
