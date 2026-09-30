from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# =========================================================
# ANALYSIS CREATE
# Used when storing AI analysis result
# =========================================================

class AnalysisCreate(BaseModel):
    bug_id: int
    bug_type: Optional[str] = None
    root_cause: Optional[str] = None
    explanation: Optional[str] = None
    solution: Optional[str] = None
    fixed_code: Optional[str] = None
    confidence: Optional[float] = None


# =========================================================
# ANALYSIS RESPONSE
# Used when sending analysis result to frontend
# =========================================================

class AnalysisResponse(BaseModel):
    id: int
    bug_id: int
    bug_type: Optional[str] = None
    root_cause: Optional[str] = None
    explanation: Optional[str] = None
    solution: Optional[str] = None
    fixed_code: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True