from dataclasses import Field
from pydantic import BaseModel, EmailStr, StringConstraints, constr, Field
from datetime import datetime
from typing import Annotated, Optional, List
from app.constants.user import UserRole, UserStatus

# Schema for creating a new user
class UserCreate(BaseModel):
    username: str
    password: Annotated[str, StringConstraints(min_length=8)]  # Ensure at least 8 characters
    email: EmailStr
    role: UserRole
    status: UserStatus = UserStatus.PENDING  # Default to 'pending'
    fcm_token: Optional[str] = None

# Schema for patient-specific data
class PatientData(BaseModel):
    medical_conditions: Optional[List[str]] = Field(
        default=None, description="List of medical conditions"
    )
    medical_history: Optional[List[str]] = Field(
        default=None, description="List of medical history events"
    )
    medications: Optional[List[str]] = Field(
        default=None, description="List of current medications"
    )
    allergies: Optional[List[str]] = Field(
        default=None, description="List of allergies"
    )
    age: Optional[float] = Field(
        default=None, description="Age in years"
    )
    height: Optional[float] = Field(
        default=None, description="Height in centimeters"
    )
    weight: Optional[float] = Field(
        default=None, description="Weight in kilograms"
    )
    blood_group: Optional[str] = Field(
        default=None, description="Blood group (e.g., A+, O-)"
    )

# Schema for doctor-specific data
class DoctorData(BaseModel):
    qualifications: Optional[List[str]] = Field(
        default=None, description="List of qualifications (e.g., MBBS, MD)"
    )
    specialization: Optional[List[str]] = Field(
        default=None, description="List of specializations (e.g., Cardiology, Neurology)"
    )
    experience_years: Optional[int] = Field(
        default=None, description="Years of experience"
    )
    license_number: Optional[str] = Field(
        default=None, description="Medical license number"
    )
    hospital: Optional[str] = Field(
        default=None, description="Hospital or clinic name"
    )
    age: Optional[float] = Field(
        default=None, description="Age in years"
    )
    
# Schema for returning user details (response)
class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    status: str
    patient_data: Optional[PatientData] = None  # Include patient data if applicable
    doctor_data: Optional[DoctorData] = None  # Include doctor data if applicable

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy (if used)

# Schema for updating user details
class UserUpdate(BaseModel):
    username: Optional[str] = None 
    email: Optional[EmailStr] = None
    fcm_token: Optional[str] = None
    patient_data: Optional[PatientData] = None  # Update patient data
    doctor_data: Optional[DoctorData] = None  # Update doctor data