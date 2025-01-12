from fastapi import Depends
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.admin_service import AdminService
from app.services.ticket_service import TicketService
from app.services.notification_service import NotificationService
from app.services.chat_service import ChatService
from app.services.feedback_service import FeedbackService  # Import FeedbackService
from app.repositories.user_repository import UserRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.feedback_repository import FeedbackRepository  # Import FeedbackRepository
from app.repositories.notification_repository import NotificationRepository
from app.database.database import Users, Tickets, Notifications, Feedback  # Add Feedback collection

# Repository dependencies
def get_user_repository():
    return UserRepository(collection=Users)

def get_ticket_repository():
    return TicketRepository(collection=Tickets)

def get_notification_repository():
    return NotificationRepository(collection=Notifications)

def get_chat_repository():
    return ChatRepository()

def get_feedback_repository():  # Add FeedbackRepository dependency
    return FeedbackRepository(collection=Feedback)

# Service dependencies

def get_notification_service(
    notification_repository: NotificationRepository = Depends(get_notification_repository),
):
    return NotificationService(notification_repository)

def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return UserService(user_repository, notification_service)

def get_auth_service(
    user_service: UserService = Depends(get_user_service)
):
    return AuthService(user_service)

def get_admin_service(
    user_repository: UserRepository = Depends(get_user_repository),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return AdminService(user_repository, notification_service)

def get_ticket_service(
    ticket_repository: TicketRepository = Depends(get_ticket_repository),
    notification_service: NotificationService = Depends(get_notification_service),
    user_repository: UserRepository = Depends(get_user_repository)
):
    return TicketService(
        ticket_repository=ticket_repository,
        user_repository=user_repository,
        notification_service=notification_service
    )

def get_chat_service(
    chat_repository: ChatRepository = Depends(get_chat_repository),
    user_service: UserService = Depends(get_user_service),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return ChatService(chat_repository, user_service, ticket_service)

def get_feedback_service(  
    feedback_repository: FeedbackRepository = Depends(get_feedback_repository),
):
    return FeedbackService(feedback_repository)