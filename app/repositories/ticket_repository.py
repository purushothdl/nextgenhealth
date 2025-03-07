from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.database.database import Tickets

class TicketRepository:
    def __init__(self, collection: AsyncIOMotorCollection = Tickets):
        self.collection = collection

    async def get_all_tickets(self):
        return await self.collection.find().to_list(length=None)

    async def get_tickets_by_doctor(self, doctor_id: str):
        return await self.collection.find({"assigned_doctor_id": ObjectId(doctor_id)}).to_list(length=None)

    async def get_tickets_by_patient(self, patient_id: str):
        return await self.collection.find({"patient_id": ObjectId(patient_id)}).to_list(length=None)

    async def get_ticket_by_id(self, ticket_id: str):
        return await self.collection.find_one({"_id": ObjectId(ticket_id)})

    async def create_ticket(self, ticket_data: dict):
        result = await self.collection.insert_one(ticket_data)
        return await self.get_ticket_by_id(ObjectId(result.inserted_id))

    async def update_ticket(self, ticket_id: str, update_data: dict):
        await self.collection.update_one({"_id": ObjectId(ticket_id)}, {"$set": update_data})
        return await self.get_ticket_by_id(ticket_id)

    async def delete_ticket(self, ticket_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(ticket_id)})
        return result.deleted_count > 0
    
    async def get_tickets_by_status(self, status: str):
        return await self.collection.find({"status": status}).to_list(length=None)