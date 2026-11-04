from .AuthenticationError import AuthenticationError

class UserNotFound(AuthenticationError):
    """Exception raised when a requested user cannot be found in the system."""
    pass
