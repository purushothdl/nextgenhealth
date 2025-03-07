from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserCreate, UserResponse
from app.schemas.token_schemas import Token
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.dependencies.service_dependencies import get_user_repository, get_user_service, get_auth_service
from app.dependencies.auth_dependencies import get_current_user
from app.core.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Register a new user.
    """
    try:
        return await user_service.register_user(user_data.dict())
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@auth_router.post("/login", response_model=Token)
async def login(
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate a user and return an access token.
    """
    try:
        return await auth_service.authenticate_user(email, password)
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@auth_router.get("/get_user/{user_id}", response_model=UserResponse)
async def get_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get profile of a user
    """
    try:
        return await user_service.get_user_by_id(user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@auth_router.get("/status")
async def get_user_status(
    email: str,
    user_service: UserService = Depends(get_user_service),
):
    """
    Get the status of the given email
    """

    try:
        user = await user_service.get_user_by_email(email)
        return{
            "status": user['status']
        }
    
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )