class WeatherAgentError(Exception):
    """Base exception for the weather agent."""


class ExternalServiceError(WeatherAgentError):
    """Raised when an external API is unavailable."""


class InvalidLocationError(WeatherAgentError):
    """Raised when the user location cannot be resolved."""

# except httpx.TimeoutException as exc:
#     raise ExternalServiceError(
#         "The weather provider timed out."
#     ) from exc

# except httpx.HTTPStatusError as exc:
#     raise ExternalServiceError(
#         "The weather provider returned an error."
#     ) from exc