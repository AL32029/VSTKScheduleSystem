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
        try:
            record.request_id = request_id_var.get()
        except LookupError:
            return True
        return True


class ClientIPFilter(logging.Filter):
    def filter(self, record):
        try:
            record.client_ip = client_ip_var.get()
        except LookupError:
            return True
        return True


class UserAgentFilter(logging.Filter):
    def filter(self, record):
        try:
            record.user_agent = user_agent_var.get()
        except LookupError:
            return True
        return True


class PathFilter(logging.Filter):
    def filter(self, record):
        try:
            record.path = path_var.get()
        except LookupError:
            return True
        return True

class MethodFilter(logging.Filter):
    def filter(self, record):
        try:
            record.method = method_var.get()
        except LookupError:
            return True
        return True
