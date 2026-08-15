import contextlib
import logging

from service_api.domain.context_vars import (
    client_ip_var,
    method_var,
    path_var,
    request_id_var,
    user_agent_var,
)


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.request_id = request_id_var.get()
        return True


class ClientIPFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.client_ip = client_ip_var.get()
        return True


class UserAgentFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.user_agent = user_agent_var.get()
        return True


class PathFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.path = path_var.get()
        return True


class MethodFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.method = method_var.get()
        return True
