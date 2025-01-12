# NextGenHealth API

## Overview

NextGenHealth is a healthcare management system built with FastAPI, providing users with essential features such as authentication, user management, ticketing, chat, notifications, and more.

---

## **Authentication Routes**

- `POST /auth/register` – Register a new user
- `POST /auth/login` – Login and obtain an access token

---

## **User Routes**

- `GET /users/me` – Get the current user's profile
- `PUT /users/me` – Update the current user's profile

---

## **Admin Routes**

- `GET /admin/approvals` – List pending user approvals
- `POST /admin/approvals/{user_id}/approve` – Approve a user
- `POST /admin/approvals/{user_id}/reject` – Reject a user
- `POST /admin/patients` – Get all patients
- `POST /admin/doctors` – Get all doctors

---

## **Ticket Routes**

- `GET /tickets` – List tickets (filtered by role: admin sees all, doctor sees assigned, patient sees own)
- `GET /tickets/{ticket_id}` – Get a specific ticket (role-based access)
- `POST /tickets` – Create a new ticket (patient only)
- `PUT /tickets/{ticket_id}` – Update a ticket (patient only)
- `DELETE /tickets/{ticket_id}` – Delete a ticket (patient only)
- `POST /tickets/{ticket_id}/assign` – Assign a doctor to a ticket (admin only)
- `POST /tickets/{ticket_id}/report` – Submit a report for a ticket (doctor only)

---

## **Chat Routes**

- `POST /chats` – Start a new chat session
- `POST /chats/{session_id}/continue` – Continue an existing chat session
- `GET /chats/{session_id}` – Get the chat history for a session
- `GET /user/{user_id}` – Get all chats for a specific user (optionally filtered by ticket_id for doctor)
- `DELETE /chats/{session_id}` – End a chat session

---

## **Notification Routes**

- `GET /notifications` – Get all notifications for the user
- `POST /notifications/mark-read` – Mark all notifications as read

---

## **Miscellaneous Routes**

- `GET /health-tips` – Get health tips or articles
- `GET /faqs` – Get frequently asked questions
- `POST /feedback` – Submit feedback about the app

---

## Installation

### Prerequisites

Make sure you have Python 3.8+ installed.

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/NextGenHealth.git
    ```

2. Navigate to the project folder:

    ```bash
    cd NextGenHealth
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

---

## Running the Application

To run the FastAPI application:

```bash
uvicorn main:app --reload


This is a sample read me file