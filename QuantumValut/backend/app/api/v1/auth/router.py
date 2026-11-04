from fastapi import APIRouter, Depends, Response, Request, status
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from app.services.auth_service import AuthService
from app.dependencies.auth import get_auth_service, get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Registers a new user. 
    Passwords are hashed and user is created.
    """
    user = auth_service.register_user(payload)
    return user

@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest, 
    response: Response, 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticates a user and sets HttpOnly cookies containing the JWTs.
    Returns the authenticated user details without exposing tokens in the JSON response.
    """
    user, _, _ = auth_service.authenticate_user(payload, response)
    return user

@router.post("/refresh", response_model=UserResponse)
def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Reads the refresh token from HttpOnly cookies, validates it, and issues a new access token.
    Rotates the refresh token securely.
    """
    refresh_token = request.cookies.get("refresh_token")
    user, _, _ = auth_service.refresh_session(refresh_token, response)
    return user

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logs out the user by revoking the refresh token in the database and clearing all cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    auth_service.logout_user(refresh_token, response)
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Retrieves the currently authenticated user based on the Access Token in the HttpOnly cookie.
    """
    return current_user
