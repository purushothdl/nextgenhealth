from pydantic import BaseModel
from typing import List

class FAQ(BaseModel):
    label: str  # Category label (e.g., "Registration & Approval")
    question: str
    answer: str

faqs = [
    # Registration & Approval
    FAQ(
        label="Registration & Approval",
        question="How do I register as a patient or doctor?",
        answer="Go to the 'Register' page, select your role (Patient or Doctor), and fill in the required details. Once submitted, your account will be pending admin approval."
    ),
    FAQ(
        label="Registration & Approval",
        question="How long does admin approval take?",
        answer="Admin approval typically takes 1-2 business days. You will receive a notification once your account is approved."
    ),
    FAQ(
        label="Registration & Approval",
        question="What happens after my account is approved?",
        answer="Once approved, you can log in and complete your screening form to access the dashboard."
    ),

    # Screening Form
    FAQ(
        label="Screening Form",
        question="What information do I need to provide in the screening form?",
        answer="Patients need to provide medical history, allergies, current medications, and health metrics. Doctors need to provide specialization, qualifications, and experience."
    ),
    FAQ(
        label="Screening Form",
        question="Can I update my screening form later?",
        answer="Yes, you can update your screening form at any time from the 'Profile' section."
    ),
    FAQ(
        label="Screening Form",
        question="Is the screening form mandatory?",
        answer="Yes, completing the screening form is mandatory to access the dashboard and other features."
    ),

    # Dashboard & Ticket Management
    FAQ(
        label="Dashboard & Ticket Management",
        question="How do I raise a ticket as a patient?",
        answer="Go to your dashboard and click 'Raise Ticket.' Fill in the details, upload relevant files (e.g., images, documents), and submit the ticket."
    ),
    FAQ(
        label="Dashboard & Ticket Management",
        question="How are tickets assigned to doctors?",
        answer="Admins review all tickets and assign them to available doctors based on specialization and workload."
    ),
    FAQ(
        label="Dashboard & Ticket Management",
        question="Can I track the status of my ticket?",
        answer="Yes, you can view the status of your ticket (e.g., Pending, Resolved) in the 'Tickets' section."
    ),
    FAQ(
        label="Dashboard & Ticket Management",
        question="How do doctors analyze tickets?",
        answer="Doctors can view ticket details, including patient information, and use the AI chatbot (NextGenHealth) for tailored advice and analysis."
    ),
    FAQ(
        label="Dashboard & Ticket Management",
        question="How do doctors submit reports?",
        answer="After analyzing the ticket, doctors can submit a report with their diagnosis, treatment plan, and recommendations. Patients can view this report in their dashboard."
    ),

    # AI Chatbot (NextGenHealth)
    FAQ(
        label="AI Chatbot (NextGenHealth)",
        question="What is NextGenHealth?",
        answer="NextGenHealth is an AI-powered chatbot that provides tailored medical advice based on patient details and aids doctors in analyzing tickets."
    ),
    FAQ(
        label="AI Chatbot (NextGenHealth)",
        question="How do I use NextGenHealth as a doctor?",
        answer="While analyzing a ticket, click 'Use Chatbot' to get insights and recommendations based on the patient’s medical history and symptoms."
    ),
    FAQ(
        label="AI Chatbot (NextGenHealth)",
        question="Can patients use NextGenHealth?",
        answer="Yes, patients can use NextGenHealth for general medical advice and health tips. However, it does not replace professional medical consultation."
    ),
    FAQ(
        label="AI Chatbot (NextGenHealth)",
        question="What kind of advice does NextGenHealth provide?",
        answer="NextGenHealth provides advice on symptoms, treatment options, preventive care, and general health queries. For doctors, it aids in diagnosis and treatment planning."
    ),

    # General Platform Usage
    FAQ(
        label="General Platform Usage",
        question="How do I log in to my account?",
        answer="Go to the 'Login' page and enter your registered email and password. Once logged in, you will be redirected to your dashboard."
    ),
    FAQ(
        label="General Platform Usage",
        question="How do I update my profile?",
        answer="Go to the 'Profile' section, make the necessary changes, and save your updates."
    ),
    FAQ(
        label="General Platform Usage",
        question="How do I view notifications?",
        answer="Go to the 'Notifications' section to view all your notifications. You can also mark them as read."
    ),
    FAQ(
        label="General Platform Usage",
        question="What should I do if I forget my password?",
        answer="Click 'Forgot Password' on the login page, enter your email, and follow the instructions to reset your password."
    ),
]