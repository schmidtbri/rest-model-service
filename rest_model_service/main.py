"""Service app and startup function."""
from typing import List
import uvicorn
from fastapi import FastAPI
from pydantic import BaseSettings
from ml_base.utilities import ModelManager

from rest_model_service.schemas import Error


class Settings(BaseSettings):
    """Settings for the service."""

    service_title: str = "RESTful Model Service"
    models: List[str]


settings = Settings()
app: FastAPI = FastAPI(title=settings.service_title)

from rest_model_service import routes                        # noqa: F401,E402
from rest_model_service.routes import PredictionController   # noqa: E402


@app.on_event("startup")
async def startup_event():  # noqa: ANN201
    """Startup the service."""
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

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')
