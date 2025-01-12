from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.core.exceptions import UserNotFoundException
from app.utils.mongo_utils import convert_objectids_to_strings

class AdminService:
    def __init__(
        self,
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        self.user_repository = user_repository
        self.notification_service = notification_service

    async def update_user_status(self, user_id: str, status: str):
        """
        Update a user's status to 'accepted' or 'rejected' and notify the user.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")

        # Update the user's status
        updated_user = await self.user_repository.update_user(user_id, {"status": status})
        if not updated_user:
            raise UserNotFoundException("Failed to update user status")

        # Notify the user
        if user.get("fcm_token"):
            message = f"Your registration has been {status}."
            await self.notification_service.create_notification(
                user_id=user["_id"],
                message=message,
                type=f"registration_{status}",  # e.g., "registration_accepted"
                fcm_token=user["fcm_token"],
            )

        return convert_objectids_to_strings(updated_user)

    async def get_all_patients(self):
        """
        Fetch all users with role 'patient' and status 'accepted'.
        """
        patients = await self.user_repository.get_users_by_role_and_status("patient", "accepted")
        return convert_objectids_to_strings(patients)

    async def get_all_doctors(self):
        """
        Fetch all users with role 'doctor' and status 'accepted'.
        """
        doctors = await self.user_repository.get_users_by_role_and_status("doctor", "accepted")
        return convert_objectids_to_strings(doctors)