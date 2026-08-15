from fastapi import Request
from fastapi.responses import JSONResponse

from service_api.domain.exceptions import APIServiceError


async def api_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    if not isinstance(exc, APIServiceError):
        raise exc

    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "error": exc.to_api_error()},
    )
