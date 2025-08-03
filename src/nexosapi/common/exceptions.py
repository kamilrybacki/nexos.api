from pydantic import ValidationError


class UndefinedEndpointModelError(AttributeError):
    """
    Error raised when one or both endpoint models are undefined
    """


class InvalidControllerEndpointError(ValueError):
    """
    Raise when the endpoint defined for a controller fails a regexp match
    """


class InvalidWebSearchMCPSettingsError(ValidationError):
    """
    Raise when the WebSearchMCP settings are invalid
    """
