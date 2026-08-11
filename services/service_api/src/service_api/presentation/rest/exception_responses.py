from fastapi import Request
from fastapi.responses import JSONResponse

from service_api.domain.exceptions import APIServiceException


async def api_exception_handler(request: Request, exc: APIServiceException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'status': False,
            'error': exc.to_api_error()
        }
    )
