"""Service app and startup function."""
import os
import warnings
from os import path
import logging
import yaml
from typing import List
from fastapi import FastAPI
from ml_base.utilities import ModelManager

from rest_model_service import __version__
from rest_model_service.configuration import Configuration, Model
from rest_model_service.helpers import load_type
from rest_model_service.routes import get_root, get_models, PredictionController  # noqa: F401,E402
from rest_model_service.schemas import Error, ModelMetadataCollection

logger = logging.getLogger(__name__)


def create_app(service_title: str,  models: List[Model]) -> FastAPI:
    """Create instance of FastAPI app and return it."""
    app: FastAPI = FastAPI(title=service_title,
                           version=__version__)

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
        else:
            logger.info("Skipped creating an endpoint for model: {}".format(model.qualified_name))

    return app


# getting the path to the configuration file
# defaults to "rest_config.yaml" in the current directory if not provided
if os.environ.get("REST_CONFIG") is not None:
    file_path = os.environ["REST_CONFIG"]
else:
    file_path = "rest_config.yaml"

# loading the configuration
if path.exists(file_path) and path.isfile(file_path):
    with open(file_path) as file:
        configuration = yaml.full_load(file)
    configuration = Configuration(**configuration)
    app = create_app(configuration.service_title, configuration.models)
else:
    # if there is no configuration file or it is not found, then create an empty app and raise a warning
    app = create_app("REST Model Service", [])
    warnings.warn("Could not find configuration file '{}', service has no models loaded.".format(file_path))
