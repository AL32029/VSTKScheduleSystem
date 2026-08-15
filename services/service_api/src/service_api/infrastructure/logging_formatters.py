import datetime

from pythonjsonlogger.json import JsonFormatter

from service_api.infrastructure.config import SystemSettings


class MicrosecondJsonFormatter(JsonFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.timezone = SystemSettings().TIMEZONE

    def formatTime(self, record, datefmt=None):
        d = datetime.datetime.fromtimestamp(record.created, tz=self.timezone)
        s = d.strftime(datefmt or "%d-%m-%YT%H:%M:%S")
        return f"{s}.{d.microsecond:06d}{d.strftime('%z')}"
