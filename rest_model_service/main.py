"""Service app and startup function."""
from fastapi import FastAPI

from ml_base.utilities import ModelManager

from rest_model_service import __version__
from rest_model_service.settings import Settings
from rest_model_service.schemas import Error, ModelMetadataCollection
from rest_model_service.routes import get_root, get_models, PredictionController     # noqa: F401,E402


def create_app() -> FastAPI:
    """Create instance of FastAPI app and return it."""
    settings = Settings()
    app: FastAPI = FastAPI(title=settings.service_title,
                           version=__version__)

    # adding the routes like this to avoid a circular dependency
    app.add_api_route("/",
                      get_root,
                      methods=["GET"])

    app.add_api_route("/api/models",
                      get_models,
                      methods=["GET"],
                      response_model=ModelMetadataCollection,
                      responses={
                          500: {"model": Error}
                      })

    # loading the models into the ModelManager singleton instance
    model_manager = ModelManager()

    for model_class_path in settings.models:
        model_manager.load_model(model_class_path)

    # creating an endpoint for each model
    for model in model_manager.get_models():
        model = model_manager.get_model(model["qualified_name"])
        controller = PredictionController(model=model)
        controller.__call__.__annotations__["data"] = model.input_schema

        app.add_api_route("/api/models/{}/predict".format(model.qualified_name),
                          controller,
                          methods=["POST"],
                          response_model=model.output_schema,
                          description=model.description,
                          responses={
                              400: {"model": Error},
                              500: {"model": Error}
                          })

    return app


app = create_app()
