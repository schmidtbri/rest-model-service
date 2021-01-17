"""Routes for the service."""
from fastapi.responses import JSONResponse
from ml_base import MLModel
from ml_base.ml_model import MLModelSchemaValidationException
from ml_base.utilities import ModelManager

from rest_model_service.main import app
from rest_model_service.schemas import ModelMetadataCollection, Error


@app.get("/api/models",
         response_model=ModelMetadataCollection,
         responses={
             500: {"model": Error}
         })
async def get_models():
    """List of models available."""
    try:
        # instantiating ModelManager singleton
        model_manager = ModelManager()

        # retrieving the model metadata from the model manager
        models_metadata_collection = model_manager.get_models()
        models_metadata_collection = ModelMetadataCollection(**{"models": models_metadata_collection}).dict()
        return JSONResponse(status_code=200, content=models_metadata_collection)
    except Exception as e:
        error = Error(type="ServiceError", message=str(e)).dict()
        return JSONResponse(status_code=500, content=error)


class PredictionController(object):
    """Callable class that hosts an instance of a model.

    .. note::
       This class is designed to be used as a route in the FastAPI application.

    """

    def __init__(self, model: MLModel):
        """Initialize the controller."""
        self._model = model

    def __call__(self, data):
        """Make a prediction with a model."""
        try:
            prediction = self._model.predict(data).dict()
            return JSONResponse(status_code=200, content=prediction)
        except MLModelSchemaValidationException as e:
            error = Error(type="SchemaValidationError", message=str(e)).dict()
            return JSONResponse(status_code=400, content=error)
        except Exception as e:
            error = Error(type="ServiceError", message=str(e)).dict()
            return JSONResponse(status_code=500, content=error)
