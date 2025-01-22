from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from app.services.chat_service import ChatService
from app.dependencies.service_dependencies import get_chat_service, get_ticket_service
from app.dependencies.auth_dependencies import get_current_user
from app.schemas.chat_schemas import ChatSession
from app.services.ticket_service import TicketService

chat_router = APIRouter(prefix="/chats", tags=["chats"])

@chat_router.post("/start", response_model=ChatSession)
async def start_chat(
    ticket_id: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    document: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Start a new chat session.
    - If `ticket_id` is provided, the chat is tied to a ticket.
    - If `ticket_id` is not provided, it's a general chat.
    """
    try:
        image_data = None
        document_data = None

        # Debug logs
        print(f"Received ticket_id: {ticket_id}")
        print(f"Received message: {message}")
        print(f"Received image: {image}")
        print(f"Received document: {document}")

        # If files are uploaded manually, read them as bytes
        if image:
            print(f"Reading image file: {image.filename}")
            image_data = await image.read()
            print(f"Image file size: {len(image_data)} bytes")

        if document:
            print(f"Reading document file: {document.filename}")
            document_data = await document.read()
            print(f"Document file size: {len(document_data)} bytes")

        # Start the chat session
        print("Starting chat session...")
        return await chat_service.start_chat(
            current_user=current_user,
            user_id=str(current_user["_id"]),
            ticket_id=ticket_id,
            message=message,
            image=image_data,
            document=document_data,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in start_chat: {e}")  # Debug log for errors
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/continue", response_model=ChatSession)
async def continue_chat(
    session_id: str = Form(...),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = Form(None),
    document: Optional[UploadFile] = Form(None),
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Continue an existing chat session.
    """
    try:
        # Read file contents if provided
        image_bytes = await image.read() if image else None
        document_bytes = await document.read() if document else None

        # Continue the chat session
        return await chat_service.continue_chat(
            session_id=session_id,
            message=message,
            image=image_bytes,
            document=document_bytes,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.delete("/end/{session_id}")
async def end_chat(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    End a chat session.
    """
    try:
        await chat_service.end_chat(session_id)
        return {"message": "Chat session ended successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@chat_router.get("/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Retrieve a specific chat session by session_id.
    """
    try:
        chat_session = await chat_service.get_chat_session(session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return chat_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.get("/user/{user_id}", response_model=List[ChatSession])
async def get_chats_by_user_and_ticket(
    user_id: str,
    ticket_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Retrieve all chat sessions for a specific user.
    - If `ticket_id` is provided, filter chats by both `user_id` and `ticket_id`.
    - If `ticket_id` is not provided, return all chats for the `user_id`.
    """
    try:
        chats = await chat_service.get_chats_by_user_and_ticket(user_id, ticket_id)
        if not chats:
            raise HTTPException(status_code=404, detail="No chats found for the given user and ticket")
        return chats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")