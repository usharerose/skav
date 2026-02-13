#!/usr/bin/env python3
"""
System logger configurations
User only needs to call "config_logging" before logging
"""

import copy
import datetime
import json
from collections import OrderedDict
from collections.abc import Sequence
from logging import Filter, Formatter, LogRecord
from logging.config import dictConfig

__all__ = ["config_logging"]


DEFAULT_LOG_CONFIG_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": (
                "%(asctime)s | %(service_name)s | %(process)d | %(levelname)s "
                "| +%(lineno)d %(name)s |> %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {"()": "vibehist.log.JsonFormatter"},
    },
    "filters": {"service_name_filter": {"()": "vibehist.log.ServiceNameFilter"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
            "filters": ["service_name_filter"],
        },
        "plain": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
            "filters": ["service_name_filter"],
        },
    },
    "loggers": {"": {"handlers": ["console"], "level": "INFO"}},
}


class ServiceNameFilter(Filter):
    def __init__(self, service_name: str | None = None):
        super().__init__()
        self._service_name: str | None = service_name

    def filter(self, record: LogRecord) -> bool:
        record.service_name = self._service_name if self._service_name else "unknown"
        return True


class JsonFormatter(Formatter):
    fmt_fields: Sequence[str] = (
        "asctime",
        "service_name",
        "process",
        "levelname",
        "lineno",
        "name",
        "message",
    )

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        fmt: Sequence[str] | None = None,
        datefmt: str | None = None,
    ):
        if fmt and not isinstance(fmt, (tuple, list)):
            raise TypeError(
                f"fmt param must be tuple or list type, current type: {type(fmt)}",
            )
        self._fmt: Sequence[str] = fmt or self.fmt_fields  # type: ignore[assignment]
        self._datefmt: str | None = datefmt

    def _get_exception_text(self, record: LogRecord) -> str:
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it"s constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        result = f"{record.exc_text}" if record.exc_text else ""
        return result

    def usesTime(self) -> bool:
        """
        Check if the format uses the creation time of the record.
        """
        return "asctime" in self._fmt

    def format(self, record: LogRecord) -> str:
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self._datefmt)

        result = OrderedDict()
        for field in self._fmt:
            result[field] = record.__dict__.get(field, "")

        if record.exc_info:
            result["exc"] = self._get_exception_text(record)

        return json.dumps(result, ensure_ascii=False)

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        ct = datetime.datetime.fromtimestamp(record.created, None)
        if datefmt:
            return ct.strftime(datefmt)
        time_zone = ct.strftime("%z")
        time_zone = time_zone[:-2] + ":" + time_zone[-2:]
        time_str = ct.strftime("%Y-%m-%dT%H:%M:%S")
        return f"{time_str}.{record.msecs:03d}{time_zone}"


def config_logging(
    service_name: str | None = None,
    debug: bool = False,
) -> None:
    """
    Config logging
    :param service_name: recommend providing a service name to distinguish source
    :type service_name: Optional[str]
    :param debug: When true, logger would use plain log format
    :type debug: bool
    """
    dict_config = copy.deepcopy(DEFAULT_LOG_CONFIG_DICT)
    if service_name:
        dict_config["filters"]["service_name_filter"]["service_name"] = service_name  # type: ignore[index]
    if debug:
        dict_config["loggers"][""]["handlers"] = ["plain"]  # type: ignore[index]
    dictConfig(dict_config)
