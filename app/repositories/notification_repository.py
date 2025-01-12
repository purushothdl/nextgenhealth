from motor.motor_asyncio import AsyncIOMotorCollection
from app.database.database import Notifications

class NotificationRepository:
    def __init__(self, collection: AsyncIOMotorCollection = Notifications):
        self.collection = collection

    async def create_notification(self, notification_data: dict):
        await self.collection.insert_one(notification_data)

    async def get_notifications_by_user(self, user_id: str):
        return await self.collection.find({"user_id": user_id}).to_list(length=None)

    async def mark_all_as_read(self, user_id: str):
        await self.collection.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True}}
        )
