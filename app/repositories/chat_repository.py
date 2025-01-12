from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from app.database.database import Chats
from app.schemas.chat_schemas import ChatSession, ChatResponse, ChatList, ChatView

class ChatRepository:
    def __init__(self, collection: AsyncIOMotorCollection = Chats):
        self.collection = collection

    async def save_chat_session(self, chat_session: ChatSession):
        await self.collection.insert_one(chat_session.dict())

    async def get_chat_session(self, session_id: str) -> Optional[ChatResponse]:
        session_data = await self.collection.find_one({"session_id": session_id})
        return ChatResponse(**session_data) if session_data else None

    async def update_chat_session(self, chat_session: ChatSession):
        await self.collection.update_one(
            {"session_id": chat_session.session_id},
            {"$set": chat_session.dict()},
        )

    async def delete_chat_session(self, session_id: str):
        await self.collection.delete_one({"session_id": session_id})


    async def get_chats_by_user_and_ticket(
        self, user_id: str, ticket_id: Optional[str] = None
    ) -> List[ChatList]:
        query = {"user_id": user_id}
        if ticket_id:
            query["ticket_id"] = ticket_id

        cursor = self.collection.find(query)
        chat_list = []
        async for chat_data in cursor:
            chat_list.append(ChatList(**chat_data))
        return chat_list