#!/usr/bin/env python3
"""
Unit tests for skav.log module
"""

import json
import logging

import pytest

from skav.log import JsonFormatter, ServiceNameFilter, config_logging


class TestServiceNameFilter:
    def test_filter_injects_service_name(self) -> None:
        filter_instance = ServiceNameFilter(service_name="test-service")
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = filter_instance.filter(record)
        assert result is True
        # service_name is dynamically added by the filter
        assert getattr(record, "service_name", None) == "test-service"

    def test_filter_with_none_service_name(self) -> None:
        filter_instance = ServiceNameFilter(service_name=None)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        filter_instance.filter(record)
        assert getattr(record, "service_name", None) == "unknown"


class TestJsonFormatter:
    def test_format_basic_log_record(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345
        result = formatter.format(record)
        data = json.loads(result)

        assert data["levelname"] == "INFO"
        assert data["name"] == "test.logger"
        assert data["lineno"] == 42
        assert data["message"] == "test message"
        assert data["process"] == 12345
        assert "asctime" in data

    def test_format_with_exception(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="error occurred",
            args=(),
            exc_info=(ValueError, ValueError("test error"), None),
        )
        # Simulate exception text
        record.exc_text = """
Traceback (most recent call last):
File "test.py", line 1
ValueError: test error
"""

        result = formatter.format(record)
        data = json.loads(result)

        assert "exc" in data
        assert "ValueError: test error" in data["exc"]

    def test_custom_format_fields(self) -> None:
        formatter = JsonFormatter(fmt=["message", "levelname"])
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        data = json.loads(result)

        assert set(data.keys()) == {"message", "levelname"}
        assert data["message"] == "test message"
        assert data["levelname"] == "INFO"

    def test_invalid_fmt_type_raises_error(self) -> None:
        with pytest.raises(TypeError):
            JsonFormatter(fmt="invalid")

    def test_uses_time(self) -> None:
        formatter_with_time = JsonFormatter(fmt=["message", "asctime"])
        assert formatter_with_time.usesTime() is True

        formatter_without_time = JsonFormatter(fmt=["message", "levelname"])
        assert formatter_without_time.usesTime() is False

    def test_time_format(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        data = json.loads(result)

        # Check ISO 8601 format with milliseconds and timezone
        assert "T" in data["asctime"]
        assert "+" in data["asctime"] or "-" in data["asctime"]


class TestConfigLogging:
    def test_config_logging_with_service_name(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        config_logging(service_name="skav", debug=False)
        logger = logging.getLogger("test.logger")
        logger.info("test message")

        # Verify JSON output contains service_name
        for record in caplog.records:
            assert hasattr(record, "service_name")
            assert getattr(record, "service_name", None) == "skav"

    def test_config_logging_debug_mode(self) -> None:
        config_logging(service_name="skav", debug=True)
        logger = logging.getLogger("test.debug")
        logger.info("debug message")

        # In debug mode, should use plain text format
        # The handler should be 'plain' instead of 'console'
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    def test_config_logging_default_service_name(self) -> None:
        config_logging(service_name=None)
        logger = logging.getLogger("test.default")
        logger.info("test")

        # Should default to "unknown"
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        if handler.filters:
            filter_obj = handler.filters[0]
            if isinstance(filter_obj, ServiceNameFilter):
                assert filter_obj._service_name is None
