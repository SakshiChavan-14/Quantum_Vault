from fastapi import Response
from app.core.config import settings

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Securely set authentication cookies on the HTTP Response."""
    domain_val = settings.COOKIE_DOMAIN if settings.COOKIE_DOMAIN and settings.COOKIE_DOMAIN != "localhost" else None
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=domain_val,
        path=settings.COOKIE_PATH,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=domain_val,
        path=settings.COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

def clear_auth_cookies(response: Response):
    """Securely clear authentication cookies from the HTTP Response."""
    domain_val = settings.COOKIE_DOMAIN if settings.COOKIE_DOMAIN and settings.COOKIE_DOMAIN != "localhost" else None
    
    response.delete_cookie(
        key="access_token",
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=domain_val,
        path=settings.COOKIE_PATH,
    )
    response.delete_cookie(
        key="refresh_token",
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=domain_val,
        path=settings.COOKIE_PATH,
    )
