import aiohttp
from io import BytesIO
import PIL.Image
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from fastapi import HTTPException
import google.generativeai as genai
import fitz  
from app.core.config import settings
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat_schemas import ChatSession, ChatMessage
from app.services.ticket_service import TicketService
from app.services.user_service import UserService

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def fetch_file_from_url(url: str) -> bytes:
    """
    Fetch a file from a public URL and return its bytes.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            raise HTTPException(status_code=404, detail=f"Could not fetch file from {url}")

class ChatService:
    def __init__(self, chat_repository: ChatRepository, user_service: UserService, ticket_service: TicketService):
        self.chat_repository = chat_repository
        self.user_service = user_service
        self.ticket_service = ticket_service

    async def _format_context_prompt(self, current_user: dict, user_id: str, ticket_id: Optional[str] = None) -> str:
        """
        Format a clear context prompt combining ticket and patient data when appropriate.
        """
        # Initialize the prompt parts
        prompt_parts = []
        
        if ticket_id:
            # Doctor analyzing a ticket
            prompt_parts.append("CONTEXT: Doctor analyzing patient ticket\n")
            prompt_parts.append("INSTRUCTIONS: Refer to the patient in third person. Don't use 'you'.\n")
            
            # Get ticket data
            ticket = await self.ticket_service.get_ticket_by_id(ticket_id, current_user)
            if ticket:
                prompt_parts.append("\nTICKET DETAILS:")
                prompt_parts.append(f"Title: {ticket['title']}")
                prompt_parts.append(f"Description: {ticket['description']}")
                prompt_parts.append(f"Vital Signs:")
                prompt_parts.append(f"- Blood Pressure: {ticket.get('bp', 'Not provided')}")
                prompt_parts.append(f"- Sugar Level: {ticket.get('sugar_level', 'Not provided')}")
                prompt_parts.append(f"- Weight: {ticket.get('weight', 'Not provided')} kg")
                if ticket.get('symptoms'):
                    prompt_parts.append(f"Symptoms: {ticket.get('symptoms')}")
                
                # Get patient data using patient_id from ticket
                patient_id = ticket.get("patient_id")
                if patient_id:
                    user = await self.user_service.get_user_by_id(patient_id)
                    if user and user.get("patient_data"):
                        patient_data = user["patient_data"]
                        prompt_parts.append("\nPATIENT HISTORY:")
                        prompt_parts.append(f"Age: {patient_data.get('age', 'Not provided')} years")
                        prompt_parts.append(f"Height: {patient_data.get('height', 'Not provided')} cm")
                        prompt_parts.append(f"Weight: {patient_data.get('weight', 'Not provided')} kg")
                        prompt_parts.append(f"Blood Group: {patient_data.get('blood_group', 'Not provided')}")
                        if patient_data.get('medical_conditions'):
                            prompt_parts.append(f"Medical Conditions: {', '.join(patient_data['medical_conditions'])}")
                        if patient_data.get('medical_history'):
                            prompt_parts.append(f"Medical History: {', '.join(patient_data['medical_history'])}")
                        if patient_data.get('medications'):
                            prompt_parts.append(f"Current Medications: {', '.join(patient_data['medications'])}")
                        if patient_data.get('allergies'):
                            prompt_parts.append(f"Allergies: {', '.join(patient_data['allergies'])}")
        else:
            # Regular user/patient chat
            prompt_parts.append("CONTEXT: Direct patient conversation\n")
            prompt_parts.append("INSTRUCTIONS: Address the user directly using 'you'.\n")
            
            # Get patient data
            user = await self.user_service.get_user_by_id(user_id)
            if user and user.get("patient_data"):
                patient_data = user["patient_data"]
                prompt_parts.append("\nYOUR MEDICAL PROFILE:")
                prompt_parts.append(f"Age: {patient_data.get('age', 'Not provided')} years")
                prompt_parts.append(f"Height: {patient_data.get('height', 'Not provided')} cm")
                prompt_parts.append(f"Weight: {patient_data.get('weight', 'Not provided')} kg")
                prompt_parts.append(f"Blood Group: {patient_data.get('blood_group', 'Not provided')}")
                if patient_data.get('medical_conditions'):
                    prompt_parts.append(f"Medical Conditions: {', '.join(patient_data['medical_conditions'])}")
                if patient_data.get('medical_history'):
                    prompt_parts.append(f"Medical History: {', '.join(patient_data['medical_history'])}")
                if patient_data.get('medications'):
                    prompt_parts.append(f"Current Medications: {', '.join(patient_data['medications'])}")
                if patient_data.get('allergies'):
                    prompt_parts.append(f"Allergies: {', '.join(patient_data['allergies'])}")

        return "\n".join(prompt_parts)

    async def _process_image(self, image: Optional[bytes]) -> Optional[PIL.Image.Image]:
        """
        Process an image from bytes.
        """
        if not image:
            return None

        try:
            img = PIL.Image.open(BytesIO(image))
            return img
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None

    async def _process_document(self, document: Optional[bytes]) -> Optional[str]:
        """
        Process a document from bytes.
        """
        if not document:
            return None

        try:
            if isinstance(document, bytes):
                doc = fitz.open(stream=document, filetype="pdf")
                text_content = ""
                for page in doc:
                    text_content += page.get_text()
                return text_content
            else:
                return document.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None

    async def start_chat(
        self,
        current_user: dict,
        user_id: str,
        ticket_id: Optional[str] = None,
        message: Optional[str] = None,
        image: Optional[bytes] = None,
        document: Optional[bytes] = None,
    ) -> ChatSession:
        # Fetch previous chat history if this is a continuation of an existing session
        previous_history = []
        # if ticket_id:
        #     previous_chats = await self.chat_repository.get_chats_by_user_and_ticket(user_id, ticket_id)
        #     for chat in previous_chats:
        #         previous_history.extend(chat.chat_history)

        # If ticket_id is provided, fetch the ticket and process its image_url and docs_url
        if ticket_id:
            ticket = await self.ticket_service.get_ticket_by_id(ticket_id, current_user)
            if ticket:
                # Fetch and process image from ticket's image_url
                if ticket.get("image_url"):
                    try:
                        image = await fetch_file_from_url(ticket["image_url"])
                    except Exception as e:
                        print(f"Error fetching image from URL: {str(e)}")

                # Fetch and process document from ticket's docs_url
                if ticket.get("docs_url"):
                    try:
                        document = await fetch_file_from_url(ticket["docs_url"])
                    except Exception as e:
                        print(f"Error fetching document from URL: {str(e)}")

        # Start a new Gemini chat session with previous history
        chat = model.start_chat(history=previous_history)

        # Get formatted context
        context_prompt = await self._format_context_prompt(current_user, user_id, ticket_id)

        # Prepare input content
        input_content = [context_prompt]

        if message:
            input_content.append(f"User Query: {message}")

        if image:
            img = await self._process_image(image)
            if img:
                input_content.append(img)

        if document:
            doc_text = await self._process_document(document)
            if doc_text:
                input_content.append(f"Document content: {doc_text}")

        # Add the system prompt
        system_prompt = (
            "\nSYSTEM INSTRUCTIONS:\n"
            "You are the NexGenHealth AI Assistant, designed to provide medical information and support. "
            "This is an educational project and not for real medical use. "
            "Provide concise, informative responses in 6-8 lines. "
            "Base your responses on the provided patient data and ticket details. "
            "Be direct and avoid unnecessary medical disclaimers since this is a project. "
            "Maintain a professional yet approachable tone."
        )
        input_content.append(system_prompt)

        # Send input to the model
        response = chat.send_message(input_content)

        # Serialize the Gemini chat history
        serialized_history = [
            {"role": msg.role, "text": msg.parts[0].text}
            for msg in chat.history
        ]

        # Create a new chat session
        chat_session = ChatSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            ticket_id=ticket_id,
            messages=[
                ChatMessage(sender="user", text=message or "Started chat", timestamp=datetime.utcnow()),
                ChatMessage(sender="bot", text=response.text, timestamp=datetime.utcnow()),
            ],
            chat_history=serialized_history,
        )

        # Save the chat session
        await self.chat_repository.save_chat_session(chat_session)

        return chat_session

    async def continue_chat(
        self,
        session_id: str,
        message: str,
        image: Optional[bytes] = None,
        document: Optional[bytes] = None,
    ) -> ChatSession:
        # Fetch the chat session
        chat_session = await self.chat_repository.get_chat_session(session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Deserialize the Gemini chat history
        deserialized_history = [
            {"role": msg["role"], "parts": [{"text": msg["text"]}]}  # Convert back to Gemini format
            for msg in chat_session.chat_history
        ]

        # Restore the Gemini chat session
        chat = model.start_chat(history=deserialized_history)

        # Prepare input for the model
        input_content = [message]

        if image:
            img = await self._process_image(image)
            if img:
                input_content.append(img)

        if document:
            doc_text = await self._process_document(document)
            if doc_text:
                input_content.append(f"Document content: {doc_text}")

        # Add a prompt for concise responses
        input_content.append(
            "You are a NexGenHealth chatbot designed to assist with medical inquiries. "
            "This is a college project and will not be used in a real medical setting. "
            "Provide a concise and informative response in 4-8 lines. "
            "Focus on the key points and avoid unnecessary warnings or disclaimers. "
        )

        # Send input to the model
        response = chat.send_message(input_content)

        # Update the chat session
        chat_session.messages.extend([
            ChatMessage(sender="user", text=message, timestamp=datetime.utcnow()),
            ChatMessage(sender="bot", text=response.text, timestamp=datetime.utcnow()),
        ])
        chat_session.chat_history = [
            {"role": msg.role, "text": msg.parts[0].text}  # Serialize updated history
            for msg in chat.history
        ]
        chat_session.updated_at = datetime.utcnow()

        # Save the updated chat session
        await self.chat_repository.update_chat_session(chat_session)

        return chat_session
    
    async def get_chats_by_user_and_ticket(
        self, user_id: str, ticket_id: Optional[str] = None
    ) -> List[ChatSession]:
        """
        Retrieve all chat sessions for a specific user.
        - If `ticket_id` is provided, filter chats by both `user_id` and `ticket_id`.
        - If `ticket_id` is not provided, return all chats for the `user_id`.
        """
        return await self.chat_repository.get_chats_by_user_and_ticket(user_id, ticket_id)

    async def end_chat(self, session_id: str):
        """
        Checks if a chat session exists and then deletes it
        """
        chat_session = await self.chat_repository.get_chat_session(session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        await self.chat_repository.delete_chat_session(session_id)


    async def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve a specific chat session by its session_id.
        """
        chat_session = await self.chat_repository.get_chat_session(session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return chat_session