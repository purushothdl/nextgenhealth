from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from bson import ObjectId
from app.services.report_service import ReportService
from app.services.ticket_service import TicketService
from app.dependencies.service_dependencies import get_report_service, get_ticket_service, get_user_service
from app.dependencies.auth_dependencies import get_current_user, get_current_doctor, get_current_admin
from app.core.exceptions import TicketNotFoundException, UnauthorizedAccessException
from app.services.user_service import UserService

# Initialize the router
ticket_router = APIRouter(prefix="/tickets", tags=["tickets"])

@ticket_router.get("/")
async def get_tickets(
    status: Optional[str] = Query(None, description="Filter tickets by status (e.g., 'resolved' or 'pending')"),
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Get tickets based on the user's role and optional status filter.
    - Admin: All tickets
    - Doctor: Assigned tickets
    - Patient: Own tickets
    """
    try:
        return await ticket_service.get_tickets(current_user, status)
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
    bp: Optional[str] = Form(None),  
    sugar_level: Optional[str] = Form(None),  
    weight: Optional[float] = Form(None),  
    symptoms: Optional[str] = Form(None),  
    image: UploadFile = File(default=None),  
    document: UploadFile = File(default=None),  
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Create a new ticket (patient only) with optional health data and file uploads.
    """
    try:
        
        ticket_data = {
            "title": title,
            "description": description,
            "patient_id": current_user["_id"],
            "bp": bp,  
            "sugar_level": sugar_level,  
            "weight": weight,  
            "symptoms": symptoms,
            "status": "pending"  
        }
        
        ticket = await ticket_service.create_ticket(ticket_data)
        if image:
            ticket_data["image_url"] = await ticket_service.upload_file(image, ticket["_id"], "images")
        if document:
            ticket_data["docs_url"] = await ticket_service.upload_file(document, ticket["_id"], "docs")
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


@ticket_router.post("/{ticket_id}/report", status_code=status.HTTP_201_CREATED)
async def submit_report(
    ticket_id: str,
    diagnosis: str = Form(...),
    recommendations: str = Form(...),
    medications: List[str] = Form(...),  # List of medications to append
    image: Optional[UploadFile] = File(None),
    document: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_doctor),
    report_service: ReportService = Depends(get_report_service),
    ticket_service: TicketService = Depends(get_ticket_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Submit a report for a specific ticket (doctor only).
    - Appends medications to the patient's profile.
    """
    try:
        ticket = await ticket_service.get_ticket_by_id(ticket_id, current_user)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found.",
            )
        
        existing_report = await report_service.get_report_by_ticket_id(ticket_id)
        if existing_report:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A report already exists for this ticket.",
            )

        image_url = None
        if image:
            image_url = await ticket_service.upload_report_file(image, ticket_id, "images")

        docs_url = None
        if document:
            docs_url = await ticket_service.upload_report_file(document, ticket_id, "docs")

        report_data = {
            "ticket_id": ticket_id,
            "doctor_id": current_user["_id"],
            "diagnosis": diagnosis,
            "recommendations": recommendations,
            "medications": medications,  
            "image_url": image_url,
            "docs_url": docs_url,
        }
        report = await report_service.create_report(report_data, current_user)

        # Append medications to the patient's profile
        patient_id = ticket["patient_id"]
        await user_service.update_user_profile(
            patient_id,
            {"patient_data.medications": medications} 
        )

        return report

    except TicketNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    except UnauthorizedAccessException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to submit a report for this ticket.",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An unexpected error occurred while submitting the report: {e}.",
        )
    
@ticket_router.get("/{ticket_id}/report", response_model=Dict)
async def get_ticket_report(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Retrieve a report for a specific ticket (patient only).
    """
    try:
        ticket = await ticket_service.get_ticket_by_id(ticket_id, current_user)

        report = await report_service.get_report_by_ticket_id(ticket_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )

        return report
    except TicketNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    except UnauthorizedAccessException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to submit a report for this ticket.",
        )
    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An unexpected error occurred while submitting the report.",
        )