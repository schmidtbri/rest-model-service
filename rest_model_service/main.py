"""Service app and startup function."""
import os
import warnings
from os import path
import logging
import logging.config
import yaml
from typing import List, Dict, Optional
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from ml_base.utilities import ModelManager

from rest_model_service import __version__
from rest_model_service.configuration import Configuration, Model
from rest_model_service.helpers import load_type
from rest_model_service.routes import get_root, get_models, PredictionController  # noqa: F401,E402
from rest_model_service.exception_handlers import validation_exception_handler
from rest_model_service.schemas import Error, ModelMetadataCollection


def create_app(service_title: str, models: List[Model], logging_configuration: Optional[Dict] = None) -> FastAPI:
    """Create instance of FastAPI app and return it."""
    # setting up the logging configuration
    if logging_configuration is not None:
        logging.config.dictConfig(logging_configuration)

    logger = logging.getLogger(__name__)
    logger.info("Starting '{}'.".format(service_title))

    app: FastAPI = FastAPI(title=service_title,
                           version=__version__)

    # adding a custom exception handler for validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # adding the routes like this to avoid a circular dependency
    app.add_api_route("/", get_root, methods=["GET"])

    app.add_api_route("/api/models", get_models, methods=["GET"],
                      response_model=ModelMetadataCollection,
                      responses={
                          500: {"model": Error}
                      })

    # loading the models into the ModelManager singleton instance
    model_manager = ModelManager()

    for model in models:
        # loading the model's class
        model_class = load_type(model.class_path)

        # instantiating the model object from the class
        model_instance = model_class()

        # adding the model instance to the ModelManager
        model_manager.add_model(model_instance)

        logger.info("Loaded {} model.".format(model_instance.qualified_name))

        decorators = model.decorators if model.decorators is not None else []

        # initializing decorators for the model
        for decorator in decorators:
            # loading the decorator's class
            decorator_class = load_type(decorator.class_path)

            # instantiating the decorator object from the class
            if decorator.configuration is not None:
                decorator_instance = decorator_class(**decorator.configuration)
            else:
                decorator_instance = decorator_class()

            # adding the decorator to the model in the ModelManager
            model_manager.add_decorator(model.qualified_name, decorator_instance)

            logger.info("Added {} decorator to {} model.".format(decorator_class.__name__,
                                                                 model_instance.qualified_name))

        # creating an endpoint for each model, if the configuration allows it
        if model.create_endpoint:
            model = model_manager.get_model(model.qualified_name)

            controller = PredictionController(model=model)
            controller.__call__.__annotations__["data"] = model.input_schema

            app.add_api_route("/api/models/{}/prediction".format(model.qualified_name),
                              controller,
                              methods=["POST"],
                              response_model=model.output_schema,
                              description=model.description,
                              responses={
                                  400: {"model": Error},
                                  500: {"model": Error}
                              })
            logger.info("Created endpoint for {} model.".format(model.qualified_name))
        else:
            logger.info("Skipped creating an endpoint for model: {}".format(model.qualified_name))

    return app


# getting the path to the configuration file
# defaults to "rest_config.yaml" in the current directory if not provided
if "REST_CONFIG" in os.environ:
    file_path = os.environ["REST_CONFIG"]
else:
    file_path = "rest_config.yaml"

# loading the configuration
if path.exists(file_path) and path.isfile(file_path):
    with open(file_path) as file:
        configuration = yaml.full_load(file)
    configuration = Configuration(**configuration)
    app = create_app(configuration.service_title, configuration.models, configuration.logging)
else:
    # if there is no configuration file or it is not found, then raise a warning
    warnings.warn("Could not find configuration file '{}', service has no models loaded.".format(file_path))
