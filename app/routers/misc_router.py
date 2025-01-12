from fastapi import APIRouter
from typing import Dict, List
from app.database.faq_list import FAQ, faqs 
misc_router = APIRouter(prefix="/misc", tags=["misc"])

@misc_router.get("/faqs", response_model=Dict[str, List[FAQ]])
async def get_faqs():
    """
    Get frequently asked questions (FAQs) grouped by category.
    """
    grouped_faqs = {}
    for faq in faqs:
        if faq.label not in grouped_faqs:
            grouped_faqs[faq.label] = []
        grouped_faqs[faq.label].append(faq)
    return grouped_faqs