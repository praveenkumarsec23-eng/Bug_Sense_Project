from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# =========================================================
# BUG CREATE
# Data received from Bug Analyzer frontend
# =========================================================

class BugCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    language: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    description: Optional[str] = Field(
        default=None,
        max_length=10000
    )

    error_message: Optional[str] = Field(
        default=None,
        max_length=10000
    )

    stack_trace: Optional[str] = Field(
        default=None,
        max_length=30000
    )

    code: Optional[str] = Field(
        default=None,
        max_length=100000
    )

    analyze_root_cause: bool = True
    search_similar_bugs: bool = True
    generate_fix_recommendation: bool = True
    detect_duplicates: bool = True


# =========================================================
# BUG RESPONSE
# Data sent back to frontend
# =========================================================

class BugResponse(BaseModel):
    id: int
    user_id: int

    title: str
    language: str

    description: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    code: Optional[str] = None

    severity: Optional[str] = None
    status: str

    created_at: datetime

    class Config:
        from_attributes = True