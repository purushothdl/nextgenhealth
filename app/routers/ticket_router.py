from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from bson import ObjectId
from app.services.ticket_service import TicketService
from app.dependencies.service_dependencies import get_ticket_service
from app.dependencies.auth_dependencies import get_current_user, get_current_doctor, get_current_admin
from app.core.exceptions import TicketNotFoundException, UnauthorizedAccessException

# Initialize the router
ticket_router = APIRouter(prefix="/tickets", tags=["tickets"])

@ticket_router.get("/")
async def get_tickets(
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Get tickets based on the user's role.
    - Admin: All tickets
    - Doctor: Assigned tickets
    - Patient: Own tickets
    """
    try:
        return await ticket_service.get_tickets(current_user)
    except UnauthorizedAccessException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@ticket_router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Get a specific ticket with role-based access.
    """
    try:
        return await ticket_service.get_ticket_by_id(ticket_id, current_user)
    except (TicketNotFoundException, UnauthorizedAccessException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, TicketNotFoundException) else status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@ticket_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    title: str = Form(...),
    description: str = Form(...),
    bp: Optional[str] = Form(None),  # Blood pressure (optional)
    sugar_level: Optional[str] = Form(None),  # Sugar level (optional)
    weight: Optional[float] = Form(None),  # Weight (optional)
    symptoms: Optional[str] = Form(None),  # Symptoms (optional)
    image: UploadFile = File(default=None),  # Optional image upload
    document: UploadFile = File(default=None),  # Optional document upload
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Create a new ticket (patient only) with optional health data and file uploads.
    """
    try:
        # Prepare ticket data
        ticket_data = {
            "title": title,
            "description": description,
            "patient_id": current_user["_id"],
            "bp": bp,  # Add blood pressure
            "sugar_level": sugar_level,  # Add sugar level
            "weight": weight,  # Add weight
            "symptoms": symptoms,  # Add symptoms
        }

        # Create the ticket first to get the ticket_id
        ticket = await ticket_service.create_ticket(ticket_data)

        # Upload image and store its URL
        if image:
            ticket_data["image_url"] = await ticket_service.upload_file(image, ticket["_id"], "images")

        # Upload document and store its URL
        if document:
            ticket_data["docs_url"] = await ticket_service.upload_file(document, ticket["_id"], "docs")

        # Update the ticket with file URLs
        updated_ticket = await ticket_service.update_ticket(ticket["_id"], ticket_data, current_user)
        return updated_ticket
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
@ticket_router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Update a ticket (patient only).
    """
    try:
        return await ticket_service.update_ticket(ticket_id, update_data, current_user)
    except (TicketNotFoundException, UnauthorizedAccessException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, TicketNotFoundException) else status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@ticket_router.delete("/{ticket_id}", status_code=status.HTTP_200_OK)
async def delete_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Delete a ticket (patient only).
    """
    try:
        return await ticket_service.delete_ticket(ticket_id, current_user)
    except (TicketNotFoundException, UnauthorizedAccessException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, TicketNotFoundException) else status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@ticket_router.post("/{ticket_id}/assign")
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

@ticket_router.post("/{ticket_id}/report")
async def submit_report(
    ticket_id: str,
    report_data: dict,
    current_user: dict = Depends(get_current_doctor),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Submit a report for a ticket (doctor only).
    """
    try:
        return await ticket_service.submit_report(ticket_id, report_data, current_user)
    except (TicketNotFoundException, UnauthorizedAccessException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, TicketNotFoundException) else status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )