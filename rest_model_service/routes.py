"""Routes for the service."""
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse

from ml_base import MLModel
from ml_base.ml_model import MLModelSchemaValidationException
from ml_base.utilities import ModelManager

from rest_model_service.schemas import ModelDetailsCollection, ModelMetadata, Error
from rest_model_service.status_manager import StatusManager
from rest_model_service.schemas import HealthStatus, ReadinessStatus, StartupStatus, HealthStatusResponse, \
    ReadinessStatusResponse, StartupStatusResponse

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/")
async def get_root():   # noqa: ANN201
    """Root of API, redirects to the /docs endpoint."""
    response = RedirectResponse(url='/docs')
    return response


@router.get("/api/health",
            response_model=HealthStatusResponse,
            responses={
                200: {"model": HealthStatusResponse},
                503: {"model": HealthStatusResponse}
            })
async def health_check() -> JSONResponse:   # noqa: ANN201
    """Check on service health.

    Indicates whether the service process is running. This endpoint will return a 200 status once the service
    has started.

    """
    health_status_manager = StatusManager()
    health_status = health_status_manager.get_health_status()
    health_status_response = HealthStatusResponse(health_status=health_status)

    if health_status == HealthStatus.HEALTHY:
        return JSONResponse(health_status_response.dict(), 200)
    else:
        return JSONResponse(health_status_response.dict(), 503)


@router.get("/api/health/ready",
            response_model=ReadinessStatusResponse,
            responses={
                200: {"model": ReadinessStatusResponse},
                503: {"model": ReadinessStatusResponse}
            })
async def readiness_check() -> JSONResponse:   # noqa: ANN201
    """Check on service readiness.

    Indicates whether the service is ready to respond to requests. This endpoint will return a 200 status only if
    all the models and decorators have finished being instantiated without errors. Once the models and decorators
    are loaded, the readiness check will always return a ACCEPTING_TRAFFIC state.

    """
    health_status_manager = StatusManager()
    readiness_status = health_status_manager.get_readiness_status()
    readiness_status_response = ReadinessStatusResponse(readiness_status=readiness_status)

    if readiness_status == ReadinessStatus.ACCEPTING_TRAFFIC:
        return JSONResponse(readiness_status_response.dict(), 200)
    else:
        return JSONResponse(readiness_status_response.dict(), 503)


@router.get("/api/health/startup",
            response_model=StartupStatusResponse,
            responses={
                200: {"model": StartupStatusResponse},
                503: {"model": StartupStatusResponse}
            })
async def startup_check() -> JSONResponse:   # noqa: ANN201
    """Check on service startup.

    Indicates whether the service is started. This endpoint will return a 200 status only if all the models
    and decorators have finished being instantiated without errors.

    """
    health_status_manager = StatusManager()
    startup_status = health_status_manager.get_startup_status()
    startup_status_response = StartupStatusResponse(startup_status=startup_status)

    if startup_status == StartupStatus.STARTED:
        return JSONResponse(startup_status_response.dict(), 200)
    else:
        return JSONResponse(startup_status_response.dict(), 503)


@router.get("/api/models",
            response_model=ModelDetailsCollection,
            responses={
                200: {"model": ModelDetailsCollection},
                500: {"model": Error}
            })
async def get_models() -> JSONResponse:   # noqa: ANN201
    """List of models available.

    This endpoint returns details about all the models currently loaded in the service, however not all models
    necessarily have an endpoint created for them.

    """
    try:
        model_manager = ModelManager()
        model_details_collection = model_manager.get_models()
        model_details_collection = ModelDetailsCollection(**{"models": model_details_collection}).dict()
        return JSONResponse(status_code=200, content=model_details_collection)
    except Exception as e:
        error = Error(type="ServiceError", messages=[str(e)]).dict()
        return JSONResponse(status_code=500, content=error)


@router.get("/api/models/{model_qualified_name}/metadata",
            response_model=ModelMetadata,
            responses={
                200: {"model": ModelMetadata},
                500: {"model": Error}
            })
async def get_model_metadata(model_qualified_name: str) -> JSONResponse:   # noqa: ANN201
    """Return metadata about a single model.

    This endpoint returns metadata about any of the models currently loaded in the service, however not all models
    necessarily have an endpoint created for them.

    """
    try:
        model_manager = ModelManager()
        model_metadata = model_manager.get_model_metadata(qualified_name=model_qualified_name)
        model_metadata = ModelMetadata(**model_metadata).dict()
        return JSONResponse(status_code=200, content=model_metadata)
    except Exception as e:
        error = Error(type="ServiceError", messages=[str(e)]).dict()
        return JSONResponse(status_code=500, content=error)


class PredictionController(object):
    """Callable class that hosts an instance of a model.

    .. note::
       This class is designed to be used as a route in the FastAPI application.

    """

    def __init__(self, model: MLModel) -> None:  # noqa: ANN101
        """Initialize the controller."""
        self._model = model

    def __call__(self, data) -> JSONResponse:  # noqa: ANN001,ANN204,ANN101
        """Make a prediction with a model."""
        try:
            prediction = self._model.predict(data).dict()
            logger.debug("Made a prediction with model '{}'.".format(self._model.qualified_name))
            return JSONResponse(status_code=200, content=prediction)
        except MLModelSchemaValidationException as e:
            logger.exception("Error when making a prediction  prediction with model '{}'.".
                             format(self._model.qualified_name), exc_info=e)
            error = Error(type="SchemaValidationError", messages=[str(e)]).dict()
            return JSONResponse(status_code=400, content=error)
        except Exception as e:
            logger.exception("Error when making a prediction  prediction with model '{}'.".
                             format(self._model.qualified_name), exc_info=e)
            error = Error(type="ServiceError", messages=[str(e)]).dict()
            return JSONResponse(status_code=500, content=error)
