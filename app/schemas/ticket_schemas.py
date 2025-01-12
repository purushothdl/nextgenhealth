from pydantic import BaseModel, Field
from typing import Optional

class TicketCreate(BaseModel):
    title: str = Field(..., description="Title of the ticket")
    description: str = Field(..., description="Description of the ticket")
    bp: Optional[str] = Field(None, description="Blood pressure (e.g., 140/90)")
    sugar_level: Optional[str] = Field(None, description="Sugar level (e.g., 120)")
    weight: Optional[float] = Field(None, description="Weight in kilograms")
    symptoms: Optional[str] = Field(None, description="Symptoms experienced by the patient")