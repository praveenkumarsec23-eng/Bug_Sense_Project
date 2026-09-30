from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# =========================================================
# SETTINGS UPDATE
# Used when frontend saves user settings
# =========================================================

class SettingsUpdate(BaseModel):
    general_language: Optional[str] = None
    general_timezone: Optional[str] = None
    general_date_format: Optional[str] = None
    general_auto_save: Optional[bool] = None

    appearance_theme: Optional[str] = None
    appearance_compact_mode: Optional[bool] = None
    appearance_animations: Optional[bool] = None

    notif_analysis_completed: Optional[bool] = None
    notif_new_knowledge: Optional[bool] = None
    notif_bug_alerts: Optional[bool] = None
    notif_system_notifications: Optional[bool] = None

    privacy_save_history: Optional[bool] = None
    privacy_store_resolved: Optional[bool] = None
    privacy_usage_analytics: Optional[bool] = None

    ai_suggestions: Optional[bool] = None
    ai_historical_retrieval: Optional[bool] = None
    ai_root_cause: Optional[bool] = None
    ai_fix_recommendations: Optional[bool] = None


# =========================================================
# SETTINGS RESPONSE
# Used when sending settings back to frontend
# =========================================================

class SettingsResponse(BaseModel):
    id: int
    user_id: int

    general_language: str
    general_timezone: str
    general_date_format: str
    general_auto_save: bool

    appearance_theme: str
    appearance_compact_mode: bool
    appearance_animations: bool

    notif_analysis_completed: bool
    notif_new_knowledge: bool
    notif_bug_alerts: bool
    notif_system_notifications: bool

    privacy_save_history: bool
    privacy_store_resolved: bool
    privacy_usage_analytics: bool

    ai_suggestions: bool
    ai_historical_retrieval: bool
    ai_root_cause: bool
    ai_fix_recommendations: bool

    created_at: datetime

    class Config:
        from_attributes = True