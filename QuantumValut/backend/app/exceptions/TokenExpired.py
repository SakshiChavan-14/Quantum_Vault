from .AuthenticationError import AuthenticationError

class TokenExpired(AuthenticationError):
    """Exception raised when a JWT or Refresh Token has expired."""
    pass
