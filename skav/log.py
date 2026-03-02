#!/usr/bin/env python3
"""
System logger configurations

This module provides structured logging configuration for Skav services.
It supports both JSON logging (default) and plain text logging (debug mode).

Features:
    - JSON structured logging with timestamp, service name, process ID, level, and location
    - Service name injection via custom filter
    - Exception traceback handling
    - ISO 8601 timestamp formatting with timezone

Usage:
    >>> from skav.log import config_logging
    >>> config_logging(service_name="my-service", debug=True)
    >>> import logging
    >>> logging.info("Application started")
"""

import copy
import datetime
import json
from collections import OrderedDict
from collections.abc import Sequence
from logging import Filter, Formatter, LogRecord
from logging.config import dictConfig

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
        "json": {"()": "skav.log.JsonFormatter"},
    },
    "filters": {"service_name_filter": {"()": "skav.log.ServiceNameFilter"}},
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
    """Logging filter that injects service name into log records.

    The service name is added as a `service_name` attribute to each LogRecord,
    which can then be used in formatters.

    :ivar _service_name: Name of the service to inject, or "unknown" if not provided
    """

    def __init__(self, service_name: str | None = None):
        """
        Initialize the service name filter.

        :param service_name: Name of the service for log identification
        :type service_name: str or None
        """
        super().__init__()
        self._service_name: str | None = service_name

    def filter(self, record: LogRecord) -> bool:
        """
        Inject service name into the log record.

        :param record: The log record to modify
        :type record: LogRecord
        :return: Always returns True to allow the record
        :rtype: bool
        """
        record.service_name = self._service_name if self._service_name else "unknown"
        return True


class JsonFormatter(Formatter):
    """JSON formatter for structured log output.

    Formats log records as JSON objects with a predefined set of fields.
    Supports custom field selection and ISO 8601 timestamp formatting.

    Example Output::

        {
            "asctime": "2025-03-02T10:30:45.123+08:00",
            "service_name": "skav",
            "process": 12345,
            "levelname": "INFO",
            "lineno": 42,
            "name": "skav.core",
            "message": "Processing complete"
        }

    :ivar fmt_fields: Default fields to include in JSON output
    :type fmt_fields: Sequence[str]
    """

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
        """
        Initialize the JSON formatter.

        :param fmt: Optional list of field names to include in output
        :type fmt: Sequence[str] or None
        :param datefmt: Optional strftime format string for timestamps
        :type datefmt: str or None
        :raises TypeError: If fmt is provided but not a tuple or list
        """
        if fmt and not isinstance(fmt, (tuple, list)):
            raise TypeError(
                f"fmt param must be tuple or list type, current type: {type(fmt)}",
            )
        self._fmt: Sequence[str] = fmt or self.fmt_fields  # type: ignore[assignment]
        self._datefmt: str | None = datefmt

    def _get_exception_text(self, record: LogRecord) -> str:
        """
        Extract exception text from a log record.

        :param record: Log record that may contain exception info
        :type record: LogRecord
        :return: Formatted exception text, or empty string if no exception
        :rtype: str
        """
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

        :return: True if "asctime" is in the field list
        :rtype: bool
        """
        return "asctime" in self._fmt

    def format(self, record: LogRecord) -> str:
        """
        Format a log record as JSON.

        :param record: The log record to format
        :type record: LogRecord
        :return: JSON-formatted log entry
        :rtype: str
        """
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
        """
        Format the log record's creation time as ISO 8601 timestamp.

        :param record: The log record containing timestamp
        :type record: LogRecord
        :param datefmt: Optional custom format string
        :type datefmt: str or None
        :return: Formatted timestamp in ISO 8601 format (e.g., "2025-03-02T10:30:45.123+08:00")
        :rtype: str
        """
        ct = datetime.datetime.fromtimestamp(record.created, None)
        if datefmt:
            return ct.strftime(datefmt)
        time_zone = ct.strftime("%z")
        time_zone = time_zone[:-2] + ":" + time_zone[-2:]
        time_str = ct.strftime("%Y-%m-%dT%H:%M:%S")
        return f"{time_str}.{int(record.msecs):03d}{time_zone}"


def config_logging(
    service_name: str | None = None,
    debug: bool = False,
) -> None:
    """
    Configure logging for the application.

    Sets up structured logging with JSON output by default, or plain text in debug mode.

    :param service_name: Optional service name for log identification (recommended)
    :type service_name: str or None
    :param debug: When True, uses plain text format instead of JSON
    :type debug: bool

    .. note::
       This function modifies the global logging configuration and should be called
       once at application startup.
    """
    dict_config = copy.deepcopy(DEFAULT_LOG_CONFIG_DICT)
    if service_name:
        dict_config["filters"]["service_name_filter"]["service_name"] = service_name  # type: ignore[index]
    if debug:
        dict_config["loggers"][""]["handlers"] = ["plain"]  # type: ignore[index]
    dictConfig(dict_config)
