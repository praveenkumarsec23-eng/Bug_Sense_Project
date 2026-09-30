from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# =========================================================
# KNOWLEDGE CREATE
# Used when adding a knowledge entry
# =========================================================

class KnowledgeCreate(BaseModel):
    title: str
    category: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    source: Optional[str] = None


# =========================================================
# KNOWLEDGE RESPONSE
# Used when sending knowledge data to frontend
# =========================================================

class KnowledgeResponse(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True