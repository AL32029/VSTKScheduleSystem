import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.routing import Match

from service_api.application.ports import MetricsCollector
from service_api.domain.context_vars import (
    client_ip_var,
    method_var,
    path_var,
    request_id_var,
    user_agent_var,
)

logger = logging.getLogger(__name__)


class InitRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        metrics: MetricsCollector = await request.app.state.dishka_container.get(
            MetricsCollector
        )

        route_path = (
            self._match_route(request.app.routes, request.scope, request.url.path)
            or "unknown"
        )

        metrics.inc_counter(
            "http_requests_total", method=request.method, path=route_path
        )

        request_id_var.set(request.headers.get("X-Request-ID", str(uuid4())))

        forwarded = request.headers.get("X-Forwarded-For")
        client_ip_var.set(
            forwarded.split(",")[0].strip() if forwarded else request.client.host
        )

        if user_agent := request.headers.get("User-Agent"):
            user_agent_var.set(user_agent)

        method_var.set(request.method)
        path_var.set(request.url.path)

        start = time.perf_counter()

        logger.debug("Request %s %s received", request.method, request.url.path)

        status_code = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            logger.exception("Request processing failed")
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000

            metrics.observe_histogram(
                "http_request_duration_s",
                duration_ms / 1000,
                method=request.method,
                path=route_path,
            )

            logger.info(
                "Request completed",
                extra={
                    "duration_ms": duration_ms,
                    "status_code": status_code if status_code is not None else 500,
                },
            )

    @staticmethod
    def _match_route(routes, scope, url_path: str) -> str | None:
        for route in routes:
            match, _ = route.matches(scope)
            if match != Match.FULL:
                continue

            if hasattr(route, "endpoint"):
                return getattr(route, "path", None) or url_path

            original_router = getattr(route, "original_router", None)
            if original_router:
                result = InitRequestMiddleware._match_route(
                    original_router.routes, scope, url_path
                )
                if result is not None:
                    return result

            sub_routes = getattr(route, "routes", None)
            if sub_routes:
                result = InitRequestMiddleware._match_route(sub_routes, scope, url_path)
                if result is not None:
                    return result

            return url_path

        return None
