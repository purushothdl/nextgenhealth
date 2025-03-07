from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime
from typing import Optional, Dict
from bson import ObjectId

class ReportRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_report(self, report_data: Dict) -> Optional[Dict]:
        """
        Save the report in the 'reports' collection.
        """
        report_data["created_at"] = datetime.utcnow()
        result = await self.collection.insert_one(report_data)
        if result.inserted_id:
            report_data["report_id"] = str(result.inserted_id)
            return report_data
        return None

    async def get_report_by_ticket_id(self, ticket_id: str) -> Optional[Dict]:
        """
        Retrieve a report by ticket_id.
        """
        report = await self.collection.find_one({"ticket_id": ticket_id})
        return report if report else None