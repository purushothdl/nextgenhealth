from fastapi import HTTPException, status
from app.core.exceptions import TicketNotFoundException, UnauthorizedAccessException
from app.repositories.report_repository import ReportRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from typing import Optional, Dict
from app.utils.mongo_utils import convert_objectids_to_strings

class ReportService:
    def __init__(
        self,
        report_repository: ReportRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
        ticket_repository: TicketRepository,
    ):
        self.report_repository = report_repository
        self.user_repository = user_repository
        self.notification_service = notification_service
        self.ticket_repository = ticket_repository
        
    async def create_report(self, report_data: dict, current_user: dict) -> dict:
        """
        Submit a report for a ticket and notify the patient.
        - Ensures only one report can be created per ticket.
        - Updates the ticket status to 'resolved'.
        """
        ticket_id = report_data["ticket_id"]

        # Validate the ticket and doctor's access
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException("Ticket not found")
        if current_user["role"] != "doctor" or ticket["assigned_doctor_id"] != current_user["_id"]:
            raise UnauthorizedAccessException("Unauthorized access")

        # Check if a report already exists for this ticket
        existing_report = await self.report_repository.get_report_by_ticket_id(ticket_id)
        if existing_report:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A report already exists for this ticket.",
            )

        # Submit the report
        report = await self.report_repository.create_report(report_data)

        # Update the ticket status to 'resolved'
        await self.ticket_repository.update_ticket(ticket_id, {"status": "resolved"})

        # Notify the patient
        patient = await self.user_repository.get_user_by_id(ticket["patient_id"])
        if patient and patient.get("fcm_token"):
            await self.notification_service.create_notification(
                user_id=patient["_id"],
                message=f"A report has been submitted for your ticket titled '{ticket['title']}.'",
                type="report_submitted",
                fcm_token=patient["fcm_token"],
            )

        return convert_objectids_to_strings(report)

    async def get_report_by_ticket_id(self, ticket_id: str) -> Optional[Dict]:
        """
        Retrieve a report by ticket_id.
        """
        report = await self.report_repository.get_report_by_ticket_id(ticket_id)
        if report:
            report = convert_objectids_to_strings(report)  
        return report