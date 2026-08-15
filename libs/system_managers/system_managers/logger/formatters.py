import datetime

from pythonjsonlogger.json import JsonFormatter


class MicrosecondJsonFormatter(JsonFormatter):
    def formatTime(self, record, datefmt=None):  # noqa: N802
        d = datetime.datetime.fromtimestamp(record.created)
        s = d.strftime(datefmt or "%d-%m-%YT%H:%M:%S")
        return f"{s}.{d.microsecond:06d}{d.strftime('%z')}"
