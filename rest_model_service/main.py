"""Main entry point for the service."""
import os
from os import path
import logging.config
import yaml

from rest_model_service.configuration import Configuration
from rest_model_service.helpers import create_app


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
    configuration = Configuration(**configuration_dict)
    app = create_app(configuration, wait_for_model_creation=False)
else:
    # if there is no configuration file, or it is not found, then raise a warning
    raise ValueError("Could not find configuration file '{}', service has no models loaded.".format(file_path))
