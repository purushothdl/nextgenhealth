from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException
from app.services.feedback_service import FeedbackService
from app.schemas.feedback_schemas import Feedback
from app.dependencies.service_dependencies import get_feedback_service
from app.dependencies.auth_dependencies import get_current_user, get_current_admin

feedback_router = APIRouter(prefix="/feedback", tags=["feedback"])

@feedback_router.post("/", response_model=Feedback)
async def add_feedback(
    rating: int = Form(..., description="Rating provided by the user (e.g., 1-5)"),
    comment: str = Form(..., description="Feedback comment provided by the user"),
    current_user: dict = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    """
    Submit general feedback about the app.
    """
    return await feedback_service.add_feedback(
        rating=rating,
        comment=comment,
        user_id=str(current_user["_id"]),
        user_role=current_user["role"],
    )

@feedback_router.get("/user", response_model=List[Feedback])
async def get_feedback_by_user(
    current_user: dict = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    """
    Retrieve all feedback submitted by the current user.
    """
    return await feedback_service.get_feedback_by_user(str(current_user["_id"]))

@feedback_router.get("/all", response_model=List[Feedback])
async def get_all_feedback(
    feedback_service: FeedbackService = Depends(get_feedback_service),
    current_user: dict = Depends(get_current_admin)
):
    """
    Retrieve all feedback submitted by all users.
    """
    return await feedback_service.get_all_feedback()

@feedback_router.get("/user/{user_id}", response_model=List[Feedback])
async def get_feedback_for_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),  # Only admins can access this
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    """
    Retrieve all feedback for a specific user.
    - Only accessible by admins.
    """
    return await feedback_service.get_feedback_by_user(user_id)