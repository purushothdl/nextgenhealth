from pydantic import BaseModel
from typing import List

class FAQ(BaseModel):
    label: str  # Category label (e.g., "Ticket Raising")
    question: str
    answer: str

faqs = [
    # Ticket Raising
    FAQ(
        label="Ticket Raising",
        question="How do I create a ticket?",
        answer="Go to the 'Tickets' section and click 'Create Ticket.' Fill in the required details, such as title, description, and symptoms, and submit the ticket."
    ),
    FAQ(
        label="Ticket Raising",
        question="What information should I include in a ticket?",
        answer="Include details like your symptoms, medical history, and any relevant files (e.g., lab reports or images)."
    ),
    FAQ(
        label="Ticket Raising",
        question="Can I update or delete a ticket?",
        answer="Yes, you can update or delete a ticket as long as it hasn’t been assigned to a doctor."
    ),

    # Ticket Analysis by Doctors
    FAQ(
        label="Ticket Analysis by Doctors",
        question="How do I analyze a ticket?",
        answer="Go to the 'Tickets' section, select a ticket, and review the patient’s details and symptoms. You can also use the chatbot for additional insights."
    ),
    FAQ(
        label="Ticket Analysis by Doctors",
        question="What should I include in a report?",
        answer="Include your diagnosis, recommended treatment, and any follow-up steps."
    ),
    FAQ(
        label="Ticket Analysis by Doctors",
        question="How do I assign a ticket to myself?",
        answer="Admins can assign tickets to doctors. If you’re an admin, go to the ticket details and click 'Assign Doctor.'"
    ),

    # Chatbot Usage
    FAQ(
        label="Chatbot Usage",
        question="How do I start a chat with the chatbot?",
        answer="Go to the 'Chat' section and click 'Start Chat.' You can ask general questions or analyze a specific ticket."
    ),
    FAQ(
        label="Chatbot Usage",
        question="What kind of questions can the chatbot answer?",
        answer="The chatbot can answer medical questions, provide health tips, and help analyze ticket details."
    ),
    FAQ(
        label="Chatbot Usage",
        question="Can the chatbot analyze my ticket?",
        answer="Yes, if you provide a ticket ID, the chatbot can analyze the ticket and provide insights."
    ),

    # General Platform Usage
    FAQ(
        label="General Platform Usage",
        question="How do I register and log in?",
        answer="Go to the 'Auth' section and click 'Register' to create an account. Use the 'Login' option to access your account."
    ),
    FAQ(
        label="General Platform Usage",
        question="How do I update my profile?",
        answer="Go to the 'Users' section and click 'Update Profile.' Fill in the required details and save the changes."
    ),
    FAQ(
        label="General Platform Usage",
        question="How do I view notifications?",
        answer="Go to the 'Notifications' section to view all your notifications. You can also mark them as read."
    ),
]