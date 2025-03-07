from typing import Optional
from bson import ObjectId
from fastapi import UploadFile
from app.core.google_cloud import download_file_from_gcs, upload_report_file_to_gcs, upload_ticket_to_gcs
from app.repositories.ticket_repository import TicketRepository
from app.services.notification_service import NotificationService
from app.repositories.user_repository import UserRepository
from app.core.exceptions import TicketNotFoundException, UnauthorizedAccessException
from app.utils.mongo_utils import convert_objectids_to_strings
from app.core.config import settings

class TicketService:
    def __init__(self, ticket_repository: TicketRepository, notification_service: NotificationService, user_repository: UserRepository):
        self.ticket_repository = ticket_repository
        self.notification_service = notification_service
        self.user_repository = user_repository

    async def get_tickets(self, current_user: dict, status: Optional[str] = None):
        """
        Get tickets based on the user's role and optional status filter.
        - Admin: All tickets
        - Doctor: Assigned tickets
        - Patient: Own tickets
        """
        if current_user["role"] == "admin":
            tickets = await self.ticket_repository.get_all_tickets()
        elif current_user["role"] == "doctor":
            tickets = await self.ticket_repository.get_tickets_by_doctor(current_user["_id"])
        elif current_user["role"] == "patient":
            tickets = await self.ticket_repository.get_tickets_by_patient(current_user["_id"])
        else:
            raise UnauthorizedAccessException("Unauthorized access")

        if status:
            tickets = [ticket for ticket in tickets if ticket.get("status") == status]
            
        return convert_objectids_to_strings(tickets)

    async def get_ticket_by_id(self, ticket_id: str, current_user: dict):
        """
        Get a specific ticket with role-based access.
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException("Ticket not found")

        # Role-based access control
        if current_user["role"] == "admin":
            return convert_objectids_to_strings(ticket)
        elif current_user["role"] == "doctor" and ticket["assigned_doctor_id"] == current_user["_id"]:
            return convert_objectids_to_strings(ticket)
        elif current_user["role"] == "patient" and ticket["patient_id"] == current_user["_id"]:
            return convert_objectids_to_strings(ticket)
        else:
            raise UnauthorizedAccessException("Unauthorized access")

    async def upload_file(self, file: UploadFile, ticket_id: str, file_type: str):
        """
        Upload a file to Google Cloud Storage and return the public URL.
        """
        try:
            # Upload file to GCS
            file_url = await upload_ticket_to_gcs(
                bucket_name=settings.GOOGLE_CLOUD_BUCKET_NAME,
                file=file,
                ticket_id=ticket_id,  # Use ticket_id for folder structure
                file_type=file_type,
            )
            return file_url
        except Exception as e:
            raise Exception(f"Failed to upload file: {e}")

    async def upload_report_file(self, file: UploadFile, ticket_id: str, file_type: str):
        """
        Upload a report file (image or document) to Google Cloud Storage and return the public URL.
        """
        try:
            # Upload file to GCS
            file_url = await upload_report_file_to_gcs(
                bucket_name=settings.GOOGLE_CLOUD_BUCKET_NAME,
                file=file,
                ticket_id=ticket_id,  # Use ticket_id for folder structure
                file_type=file_type,
            )
            return file_url
        except Exception as e:
            raise Exception(f"Failed to upload report file: {e}")

    async def create_ticket(self, ticket_data: dict):
        """
        Create a new ticket and notify the admin in real time.
        """
        # Create the ticket
        ticket = await self.ticket_repository.create_ticket(ticket_data)

        # Patient name
        patient = await self.user_repository.get_user_by_id(ticket["patient_id"])

        # Notify admin
        admins = await self.user_repository.get_users_by_role_and_status("admin", "accepted")
        for admin in admins:
            if admin["fcm_token"]:
                await self.notification_service.create_notification(
                    user_id=admin["_id"],
                    message=f"New ticket created by {patient['username']}",
                    type="ticket_created",
                    fcm_token=admin["fcm_token"],
                )
        return convert_objectids_to_strings(ticket)

    async def update_ticket(self, ticket_id: str, update_data: dict, current_user: dict):
        """
        Update a ticket (patient only).
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException("Ticket not found")
        if current_user["role"] != "patient" or ticket["patient_id"] != current_user["_id"]:
            raise UnauthorizedAccessException("Unauthorized access")

        updated_ticket = await self.ticket_repository.update_ticket(ticket_id, update_data)
        return convert_objectids_to_strings(updated_ticket)

    async def delete_ticket(self, ticket_id: str, current_user: dict):
        """
        Delete a ticket (patient only).
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException("Ticket not found")
        if current_user["role"] != "patient" or ticket["patient_id"] != current_user["_id"]:
            raise UnauthorizedAccessException("Unauthorized access")

        await self.ticket_repository.delete_ticket(ticket_id)
        return {"message": "Ticket deleted successfully"}

    async def assign_doctor(self, ticket_id: str, doctor_id: str):
        """
        Assign a doctor to a ticket and notify the doctor.
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException("Ticket not found")

        # Assign the doctor
        updated_ticket = await self.ticket_repository.update_ticket(
            ticket_id, {"assigned_doctor_id": ObjectId(doctor_id)}
        )

        # Notify the doctor
        doctor = await self.user_repository.get_user_by_id(doctor_id)
        if doctor and doctor.get("fcm_token"):
            await self.notification_service.create_notification(
                user_id=doctor["_id"],
                message = f"A new ticket titled '{ticket['title']}' has been assigned to you.",
                type="ticket_assigned",
                fcm_token=doctor["fcm_token"],
            )

        return convert_objectids_to_strings(updated_ticket)

    async def submit_report(self, ticket_id: str, report_data: dict, current_user: dict):
        """
        Submit a report for a ticket and notify the patient.
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException("Ticket not found")
        if current_user["role"] != "doctor" or ticket["assigned_doctor_id"] != current_user["_id"]:
            raise UnauthorizedAccessException("Unauthorized access")

        # Submit the report
        updated_ticket = await self.ticket_repository.update_ticket(ticket_id, {"report": report_data})

        # Notify the patient
        patient = await self.user_repository.get_user_by_id(ticket["patient_id"])
        if patient and patient.get("fcm_token"):
            await self.notification_service.create_notification(
                user_id=patient["_id"],
                message = f"A report has been submitted for your ticket titled '{ticket['title']}.'",
                type="report_submitted",
                fcm_token=patient["fcm_token"],
            )

        return convert_objectids_to_strings(updated_ticket)
    
    async def get_ticket_with_files(self, ticket_id: str) -> dict:
        """
        Fetch ticket details and download files from GCS.
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException("Ticket not found")

        # Download files from GCS
        ticket["image"] = download_file_from_gcs(ticket["image_url"]) if ticket.get("image_url") else None
        ticket["document"] = download_file_from_gcs(ticket["docs_url"]) if ticket.get("docs_url") else None

        return ticket