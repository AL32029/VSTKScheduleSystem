import contextlib
import logging

from service_bot.domain.context_vars import (
    message_id_var,
    request_id_var,
    update_id_var,
    user_id_var,
)


class MessageIDFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.message_id = message_id_var.get()
        return True


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.request_id = request_id_var.get()
        return True


class UpdateIDFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.update_id = update_id_var.get()
        return True


class UserIDFilter(logging.Filter):
    def filter(self, record):
        with contextlib.suppress(LookupError):
            record.user_id = user_id_var.get()
        return True
