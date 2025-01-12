from fastapi import APIRouter, Depends, HTTPException, status
from app.services.admin_service import AdminService
from app.dependencies.service_dependencies import get_admin_service
from app.dependencies.auth_dependencies import get_current_admin
from app.core.exceptions import UserNotFoundException, UnauthorizedAccessException

# Initialize the router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/approvals")
async def get_pending_approvals(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: dict = Depends(get_current_admin),
):
    """
    Get a list of users with status 'pending'.
    """
    try:
        return await admin_service.get_pending_approvals()
    except UnauthorizedAccessException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@admin_router.post("/approvals/{user_id}/approve")
async def approve_user(
    user_id: str,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: dict = Depends(get_current_admin),
):
    """
    Approve a user by updating their status to 'accepted'.
    """
    try:
        return await admin_service.update_user_status(user_id, "accepted")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@admin_router.post("/approvals/{user_id}/reject")
async def reject_user(
    user_id: str,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: dict = Depends(get_current_admin),
):
    """
    Reject a user by updating their status to 'rejected'.
    """
    try:
        return await admin_service.update_user_status(user_id, "rejected")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
@admin_router.get("/patients")
async def get_all_patients(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: dict = Depends(get_current_admin),
):
    """
    Get all patients with status 'accepted'.
    """
    try:
        return await admin_service.get_all_patients()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@admin_router.get("/doctors")
async def get_all_doctors(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: dict = Depends(get_current_admin),
):
    """
    Get all doctors with status 'accepted'.
    """
    try:
        return await admin_service.get_all_doctors()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )