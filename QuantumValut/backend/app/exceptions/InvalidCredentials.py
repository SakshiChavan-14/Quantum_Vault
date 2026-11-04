from .AuthenticationError import AuthenticationError

class InvalidCredentials(AuthenticationError):
    """Exception raised when credentials do not match or are invalid."""
    pass
