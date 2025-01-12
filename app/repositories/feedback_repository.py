from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from app.schemas.feedback_schemas import Feedback

class FeedbackRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def add_feedback(self, feedback: Feedback):
        await self.collection.insert_one(feedback.dict())

    async def get_feedback_by_user(self, user_id: str) -> List[Feedback]:
        cursor = self.collection.find({"user_id": user_id})
        feedback_list = []
        async for feedback_data in cursor:
            feedback_list.append(Feedback(**feedback_data))
        return feedback_list

    async def get_all_feedback(self) -> List[Feedback]:
        cursor = self.collection.find()
        feedback_list = []
        async for feedback_data in cursor:
            feedback_list.append(Feedback(**feedback_data))
        return feedback_list