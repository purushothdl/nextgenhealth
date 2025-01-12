from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DATABASE_NAME]

Users = db.users
Tickets = db.tickets
Notifications = db.notifications
Chats = db.chats
Feedback = db.feedback
Reports = db.reports