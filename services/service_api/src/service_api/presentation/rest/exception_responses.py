from starlette.responses import JSONResponse


async def not_found_exception(request, exc):
    return JSONResponse(
        status_code=404,
        content={'detail': str(exc)}
    )