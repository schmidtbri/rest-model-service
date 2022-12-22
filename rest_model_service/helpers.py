"""Helper functions."""
import logging
from typing import Type
import importlib
from concurrent.futures import ThreadPoolExecutor, Future
import logging.config
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from ml_base.utilities import ModelManager

from rest_model_service.status_manager import StatusManager, HealthStatus, StartupStatus, ReadinessStatus
from rest_model_service.configuration import Configuration
from rest_model_service.routes import PredictionController  # noqa: F401,E402
from rest_model_service.exception_handlers import validation_exception_handler
from rest_model_service.schemas import Error
from rest_model_service.routes import router

logger = logging.getLogger(__name__)


def load_type(class_path: str) -> Type:
    """Load a type.

    Args:
        class_path: Path of the type.

    Returns:
        Type

    """
    # splitting the class_path into module path and class name
    module_path = ".".join(class_path.split(".")[:-1])
    class_name = class_path.split(".")[-1]

    # importing the model class
    _module = importlib.import_module(module_path)
    _class = getattr(_module, class_name)
    return _class


def create_app(configuration: Configuration, wait_for_model_creation: bool = False) -> FastAPI:
    """Create instance of FastAPI app and return it.

    Args:
        configuration: Configuration used to create application
        wait_for_model_creation: Whether to wait for models to finish instantiating before returning. Defaults to false
            to allow for asynchronous model creation in a separate thread.

    Returns:
        FastAPI application object.

    .. note::
        This function creates a FastAPI application object using the options in a Configuration object. The application
        scaffolding is created by this function. The models are added to the application asynchronously by calling the
        build_models function in a separate thread.

    """
    logger.info("Creating FastAPI app for: '{}'.".format(configuration.service_title))

    app: FastAPI = FastAPI(title=configuration.service_title,
                           description=configuration.description,
                           version=configuration.version)

    # adding a custom exception handler for validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # adding common endpoints to the app
    app.include_router(router)

    # setting the health, startup, and readiness status of the application, the app remains in the "HEALTHY",
    # "REFUSING_TRAFFIC", and "NOT_STARTED" state until all models and decorators are initialized.
    health_status_manager = StatusManager()
    health_status_manager.set_health_status(HealthStatus.HEALTHY)
    health_status_manager.set_readiness_status(ReadinessStatus.REFUSING_TRAFFIC)
    health_status_manager.set_startup_status(StartupStatus.NOT_STARTED)

    # creating models and decorators in a separate thread
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(build_models, app, configuration)

    # add the set_service_status callback
    future.add_done_callback(set_service_status)
    executor.shutdown(wait=False)  # shutting down the executor asynchronously after the task finishes

    # if waiting for model creation, then wait for result here instead of returning app object immediately
    # this is useful for creating the app object for tests and for getting the full OpenAPI spec from the app
    if wait_for_model_creation:
        _ = future.result()
    return app


def set_service_status(future: Future) -> None:
    """Set the status of the service according to the results of the build_models thread.

    Args:
        future: Future for the build_models task.

    Returns:
        None

    .. note::
        If the models or decorators created in the build_models function raise an exception, the status of the service
        will be "NOT_HEALTHY", "REFUSING_TRAFFIC", and "STARTED".

    """
    health_status_manager = StatusManager()

    if future.exception() is not None:
        health_status_manager.set_health_status(HealthStatus.NOT_HEALTHY)
        health_status_manager.set_readiness_status(ReadinessStatus.REFUSING_TRAFFIC)
        health_status_manager.set_startup_status(StartupStatus.STARTED)
        logger.error("Exception raised in service initialization.", exc_info=future.exception())
    else:
        health_status_manager.set_health_status(HealthStatus.HEALTHY)
        health_status_manager.set_readiness_status(ReadinessStatus.ACCEPTING_TRAFFIC)
        health_status_manager.set_startup_status(StartupStatus.STARTED)


def build_models(app: FastAPI, configuration: Configuration) -> None:
    """Instantiate models and decorators, adding endpoints if necessary.

    Args:
        app: FastAPI app to modify by adding model endpoints.
        configuration: Configuration to use to instantiate models and decorators.

    Returns:
        Optional exception object, if an exception is raised it is returned to the caller.

    .. note::
        This function is designed to execute as a separate thread from the main server thread. This allows the FastAPI
        server to start up and return status information through the health endpoints before all the models and
        decorators have finished being instantiated.

    """
    # setting up the logging configuration
    if configuration.logging is not None:
        logging.config.dictConfig(configuration.logging)

    # loading the models into the ModelManager singleton instance
    model_manager = ModelManager()

    for model in configuration.models:
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
