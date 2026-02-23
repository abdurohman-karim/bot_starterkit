"""Custom exception hierarchy for backend and app errors."""


class AppError(Exception):
    """Base application error."""


class BackendError(AppError):
    """Backend returned a handled error response."""

    def __init__(self, message: str, status_code: int | None = None, payload: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class BackendAuthError(BackendError):
    """Authentication/authorization error from backend."""


class BackendUnavailable(BackendError):
    """Backend is unavailable or returned 5xx."""


class BackendTimeout(BackendError):
    """Backend request timed out."""


class BackendBadResponse(BackendError):
    """Backend returned a malformed response."""
