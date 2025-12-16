class AIServiceError(Exception):
    """Base class for AI service errors."""


class AIProviderError(AIServiceError):
    """Raised when the upstream provider fails (network, auth, etc.)."""


class AIValidationError(AIServiceError):
    """Raised when the provider returns an unexpected payload."""
