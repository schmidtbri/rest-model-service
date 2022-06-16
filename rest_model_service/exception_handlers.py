"""Exception handler."""
import logging
from starlette.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

from rest_model_service.schemas import Error


async def validation_exception_handler(request: Request, exception: RequestValidationError) -> JSONResponse:
    """Exception handler."""
    logger = logging.getLogger(__name__)

    messages = []
    for raw_error in exception.raw_errors:
        raw_error: ErrorWrapper
        if type(raw_error.exc) is ValidationError:
            for field_error in raw_error.exc.errors():
                message = "Field '{}' in type '{}' has error '{}', {}.".format(
                    ", ".join(field_error["loc"]),
                    raw_error.exc.model.__name__,
                    field_error["type"],
                    field_error["msg"]
                )
                messages.append(message)
        else:
            messages.append(str(raw_error.exc))

    extra = {
        "action": "predict",
        "endpoint": str(request.url),
        "status": "error",
        "error_info": ", ".join(messages)
    }
    logger.error("Request validation error.", extra=extra)

    error = Error(type="ValidationError", messages=messages).dict()
    return JSONResponse(status_code=400, content=error)
