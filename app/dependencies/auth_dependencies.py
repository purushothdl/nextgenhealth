from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.schemas.token_schemas import TokenData
from app.core.config import SECRET_KEY, ALGORITHM
from app.services.user_service import UserService
from app.dependencies.service_dependencies import get_user_service

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Get the current user from db using the token (protected)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # Extract user_id from the token
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)  # Use user_id in TokenData
    except JWTError:
        raise credentials_exception

    # Fetch user by user_id
    user = await user_service.get_user_by_id(user_id)
    if user is None or user['status'] != 'accepted':
        raise credentials_exception
    return user

# Get the current admin user (protected)
async def get_current_admin(user: dict = Depends(get_current_user)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You are not authorized to perform this action",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user.get("role") != "admin":
        raise credentials_exception
    return user

# Get the current doctor user (protected)
async def get_current_doctor(user: dict = Depends(get_current_user)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You are not authorized to perform this action",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user.get("role") != "doctor":
        raise credentials_exception
    return user