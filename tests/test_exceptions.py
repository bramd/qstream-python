"""Tests for QStream exceptions."""

import pytest
from qstream.exceptions import (
    QStreamError,
    QStreamConnectionError,
    QStreamTimeoutError,
    QStreamResponseError,
)


def test_qstream_error_is_base_exception():
    """QStreamError should be base for all exceptions."""
    error = QStreamError("test")
    assert isinstance(error, Exception)
    assert str(error) == "test"


def test_connection_error_inherits_from_base():
    """QStreamConnectionError should inherit from QStreamError."""
    error = QStreamConnectionError("connection failed")
    assert isinstance(error, QStreamError)


def test_timeout_error_inherits_from_base():
    """QStreamTimeoutError should inherit from QStreamError."""
    error = QStreamTimeoutError("timeout")
    assert isinstance(error, QStreamError)


def test_response_error_inherits_from_base():
    """QStreamResponseError should inherit from QStreamError."""
    error = QStreamResponseError("bad response")
    assert isinstance(error, QStreamError)


def test_response_error_stores_raw_response():
    """QStreamResponseError should store raw response data."""
    raw = '{"invalid": "data"}'
    error = QStreamResponseError("parsing failed", raw_response=raw)
    assert error.raw_response == raw
    assert "parsing failed" in str(error)


def test_response_error_allows_none_raw_response():
    """QStreamResponseError should allow None for raw_response."""
    error = QStreamResponseError("error", raw_response=None)
    assert error.raw_response is None
