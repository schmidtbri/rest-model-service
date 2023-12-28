"""Exception handler."""
import logging
from starlette.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError

from rest_model_service.schemas import Error


async def validation_exception_handler(request: Request, exception: RequestValidationError) -> JSONResponse:
    """Exception handler."""
    logger = logging.getLogger(__name__)

    messages = []
    for error in exception.errors():
        if type(error) is dict:
            message = "Field '{}' has error '{}', {}.".format(", ".join(error["loc"]),
                                                              error["type"],
                                                              error["msg"])
            messages.append(message)
        else:
            messages.append(str(error))

    extra = {
        "action": "predict",
        "endpoint": str(request.url),
        "status": "error",
        "error_info": ", ".join(messages)
    }
    logger.error(msg="Request validation error.", extra=extra)

    error = Error(type="ValidationError", messages=messages).model_dump()
    return JSONResponse(status_code=400, content=error)
