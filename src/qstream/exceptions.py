"""Exceptions for QStream library."""


class QStreamError(Exception):
    """Base exception for all QStream errors."""


class QStreamConnectionError(QStreamError):
    """Cannot connect to device (network/host unreachable)."""


class QStreamTimeoutError(QStreamError):
    """Request timed out."""


class QStreamResponseError(QStreamError):
    """Unexpected or invalid response format."""

    def __init__(self, message: str, raw_response: str | None = None) -> None:
        """Initialize with message and optional raw response.

        Args:
            message: Error description
            raw_response: The raw response that caused the error (for debugging)
        """
        super().__init__(message)
        self.raw_response = raw_response
