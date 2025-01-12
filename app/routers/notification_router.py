from fastapi import APIRouter, Depends, HTTPException, status
from app.services.notification_service import NotificationService
from app.dependencies.service_dependencies import get_notification_service
from app.dependencies.auth_dependencies import get_current_user

notification_router = APIRouter(prefix="/notifications", tags=["notifications"])

@notification_router.get("/")
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    Get all notifications for the current user.
    """
    try:
        return await notification_service.get_notifications(current_user["_id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@notification_router.post("/mark-read")
async def mark_notifications_as_read(
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    Mark all notifications as read for the current user.
    """
    try:
        await notification_service.mark_all_as_read(current_user["_id"])
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )