from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_schemas import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.dependencies.service_dependencies import get_user_service
from app.dependencies.auth_dependencies import get_current_user
from app.core.exceptions import UserNotFoundException, InvalidUserDataException

# Initialize the router
user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/me", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get the current user's profile.
    """
    try:
        return await user_service.get_user_by_id(current_user["_id"])
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@user_router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update the current user's profile.
    """
    try:
        return await user_service.update_user_profile(current_user["_id"], update_data.dict())
    except (UserNotFoundException, InvalidUserDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
@user_router.post("/update-fcm-token")
async def update_fcm_token(
    fcm_token: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update the FCM token for the current user.
    """
    try:
        await user_service.update_fcm_token(current_user["_id"], fcm_token)
        return {"message": "FCM token updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

