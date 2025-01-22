from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_schemas import UserResponse
from app.services.admin_service import AdminService
from app.dependencies.service_dependencies import get_admin_service, get_ticket_service, get_user_service
from app.dependencies.auth_dependencies import get_current_admin
from app.core.exceptions import TicketNotFoundException, UserNotFoundException, UnauthorizedAccessException
from app.services.ticket_service import TicketService
from app.services.user_service import UserService

# Initialize the router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/approvals")
async def get_pending_approvals(
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_admin),
):
    """ 
    Get a list of users with status 'pending'.
    """
    try:
        return await user_service.get_users_by_status(status="pending")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
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
    
@admin_router.get("/get_user/{user_id}", response_model=UserResponse)
async def get_profile(
    user_id: str,
    current_user: dict = Depends(get_current_admin),
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
    

@admin_router.post("/{ticket_id}/assign")
async def assign_doctor(
    ticket_id: str,
    doctor_id: str,
    current_user: dict = Depends(get_current_admin),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Assign a doctor to a ticket (admin only).
    """
    try:
        return await ticket_service.assign_doctor(ticket_id, doctor_id)
    except TicketNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )