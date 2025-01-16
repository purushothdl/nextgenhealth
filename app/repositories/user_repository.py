from typing import Any, Dict, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.database.database import Users

class UserRepository:
    def __init__(self, collection: AsyncIOMotorCollection = Users):
        self.collection = collection

    async def create_user(self, user_data: dict):
        result = await self.collection.insert_one(user_data)
        return await self.get_user_by_id(result.inserted_id)

    async def get_user_by_username(self, username: str):
        return await self.collection.find_one({"username": username})
    
    async def get_user_by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def get_user_by_role(self, role: str):
        return await self.collection.find_one({"role": role, "status": "accepted"})

    async def get_user_by_id(self, user_id: str):
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def update_user(self, user_id: str, update_data: dict):
        await self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        return await self.get_user_by_id(user_id)
    
    async def append_to_array(self, user_id: str, field: str, items: List[Any]) -> Dict:
        """
        Append items to an array field in a user document.
        - Uses the $push operator with $each to append multiple items.
        - Works for any array field (e.g., patient_data.medications, patient_data.allergies).
        """
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {field: {"$each": items}}}  # Append items to the specified array field
        )
        return await self.get_user_by_id(user_id) 


    async def delete_user(self, user_id: str):
        result = await self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    async def get_all_users(self, skip: int = 0, limit: int = 100):
        return await self.collection.find().skip(skip).limit(limit).to_list(length=None)
    
    async def get_users_by_status(self, status: str):
        return await self.collection.find({"status": status}).to_list(length=None)

    async def user_exists(self, username: str = None, email: str = None):
        query = {} 
        if username:
            query["username"] = username
        if email:
            query["email"] = email
        return await self.collection.find_one(query) is not None

    async def get_users_by_role_and_status(self, role: str, status: str):
        return await self.collection.find({"role": role, "status": status}).to_list(length=None)
    
    async def update_fcm_token(self, user_id: str, fcm_token: str):
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"fcm_token": fcm_token}}
        )