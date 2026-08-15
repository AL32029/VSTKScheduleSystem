import logging

from service_bot.domain.context_vars import (
    message_id_var,
    request_id_var,
    update_id_var,
    user_id_var,
)


class MessageIDFilter(logging.Filter):
    def filter(self, record):
        try:
            record.message_id = message_id_var.get()
        except LookupError:
            record.message_id = "unknown"
        return True


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = request_id_var.get()
        except LookupError:
            record.request_id = "unknown"
        return True


class UpdateIDFilter(logging.Filter):
    def filter(self, record):
        try:
            record.update_id = update_id_var.get()
        except LookupError:
            record.update_id = "unknown"
        return True


class UserIDFilter(logging.Filter):
    def filter(self, record):
        try:
            record.user_id = user_id_var.get()
        except LookupError:
            record.user_id = "unknown"
        return True
