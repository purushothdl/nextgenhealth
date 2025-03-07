from app.repositories.notification_repository import NotificationRepository
from app.core.firebase import messaging
from datetime import datetime
from app.core.exceptions import NotificationException
from app.utils.mongo_utils import convert_objectids_to_strings

class NotificationService:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    async def create_notification(self, user_id: str,  message: str, type: str, fcm_token: str = None):
        # Store notification in the database
        notification_data = {
            "user_id": user_id,
            "message": message,
            "type": type,
            "created_at": datetime.utcnow(),
            "read": False,
        }
        await self.notification_repository.create_notification(notification_data)

        # Send push notification via FCM
        if fcm_token:
            await self.send_fcm_notification(fcm_token, message, type)

    async def send_fcm_notification(self, fcm_token: str, message: str, type: str):
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"New {type.replace('_', ' ').title()}",  # Convert type to a readable title
                    body=message,
                ),
                token=fcm_token,
            )
            response = messaging.send(message)
            print("Successfully sent message:", response)
        except Exception as e:
            raise NotificationException(f"Failed to send FCM notification: {e}")

    async def get_notifications(self, user_id: str):
        notifications = await self.notification_repository.get_notifications_by_user(user_id)
        for notification in notifications:
            convert_objectids_to_strings(notification)
        return notifications

    async def mark_all_as_read(self, user_id: str):
        await self.notification_repository.mark_all_as_read(user_id)