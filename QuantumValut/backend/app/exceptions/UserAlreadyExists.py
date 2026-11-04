from .AuthenticationError import AuthenticationError

class UserAlreadyExists(AuthenticationError):
    """Exception raised when attempting to register an existing user."""
    pass
