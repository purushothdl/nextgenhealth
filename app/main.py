from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.firebase import initialize_firebase
from app.routers.auth_router import auth_router
from app.routers.user_router import user_router
from app.routers.admin_router import admin_router
from app.routers.ticket_router import ticket_router
from app.routers.notification_router import notification_router
from app.routers.chat_router import chat_router
from app.routers.feedback_router import feedback_router
from app.routers.misc_router import misc_router

app = FastAPI()

# Initialize Firebase
initialize_firebase() 

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the auth router
app.include_router(auth_router, prefix='/api')
app.include_router(user_router, prefix='/api')
app.include_router(admin_router, prefix='/api')
app.include_router(ticket_router, prefix='/api')
app.include_router(notification_router, prefix='/api')
app.include_router(chat_router, prefix='/api')
app.include_router(feedback_router, prefix='/api')
app.include_router(misc_router, prefix='/api')

@app.get("/")
async def root():
    return {"message": "Welcome to the Next-Gen Health Server!"}