from typing import Optional, Dict, List
from datetime import datetime
from app.utils.mongo_utils import convert_objectids_to_strings
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository
from app.core.security import hash_password
from app.core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidUserDataException,
)

class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        self.user_repository = user_repository
        self.notification_service = notification_service

    async def register_user(self, user_data: Dict) -> Dict:
        """
        Register a new user and notify admins.
        """
        if await self.user_repository.user_exists(email=user_data.get("email")):
            raise UserAlreadyExistsException("Email already exists")

        # Hash the password before saving
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
        user_data["created_at"] = datetime.utcnow()

        # Create the user
        user = await self.user_repository.create_user(user_data)

        # Notify admins
        admins = await self.user_repository.get_users_by_role_and_status("admin", "accepted")
        for admin in admins:
            if admin.get("fcm_token"):
                await self.notification_service.create_notification(
                    user_id=admin["_id"],
                    message = f"A new user has registered with the username {user_data['username']}.",
                    type="user_registered",
                    fcm_token=admin["fcm_token"],
                )
        convert_objectids_to_strings(user)
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve a user by their ID.
        - Raises an exception if the user is not found.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")
        return user

    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Retrieve a user by their username.
        - Raises an exception if the user is not found.
        """
        user = await self.user_repository.get_user_by_username(username)
        if not user:
            raise UserNotFoundException("User not found")
        return user

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Retrieve a user by their email.
        - Raises an exception if the user is not found.
        """
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise UserNotFoundException("User not found")
        return user

    async def update_user_profile(self, user_id: str, update_data: Dict) -> Dict:
        """
        Update a user's profile.
        - Validates the update data.
        - Raises an exception if the user is not found.
        - Returns the final updated user document.
        """
        if not update_data:
            raise InvalidUserDataException("No data provided for update")

        update_data.pop("hashed_password", None)
        update_data.pop("role", None)

        # Flatten the update data for nested fields
        def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
            """
            Flattens a nested dictionary into a single-level dictionary with keys
            concatenated by a separator (e.g., "patient_data.age").
            """
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        # Flatten the update data
        flattened_update_data = flatten_dict(update_data)

        # Remove None values from update_data to avoid setting fields to null
        flattened_update_data = {k: v for k, v in flattened_update_data.items() if v is not None}

        await self.user_repository.update_user(user_id, flattened_update_data)

        updated_user = await self.user_repository.get_user_by_id(user_id)
        if not updated_user:
            raise UserNotFoundException("User not found after update")

        return updated_user

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user by their ID.
        - Raises an exception if the user is not found.
        """
        if not await self.user_repository.delete_user(user_id):
            raise UserNotFoundException("User not found")
        return True

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Retrieve a list of all users (for admin purposes).
        - Supports pagination.
        """
        return await self.user_repository.get_all_users(skip=skip, limit=limit)

    async def update_user_role(self, user_id: str, new_role: str) -> Dict:
        """
        Update a user's role (admin only).
        - Validates the new role.
        - Raises an exception if the user is not found.
        """
        valid_roles = ["admin", "doctor", "patient"]
        if new_role not in valid_roles:
            raise InvalidUserDataException(f"Invalid role. Must be one of: {valid_roles}")

        user = await self.user_repository.update_user_role(user_id, new_role)
        if not user:
            raise UserNotFoundException("User not found")
        return user
    
    async def update_fcm_token(self, user_id: str, fcm_token: str):
        """
        Update the FCM token for a user.
        """
        await self.user_repository.update_fcm_token(user_id, fcm_token)