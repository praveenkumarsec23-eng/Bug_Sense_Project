from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User, UserSettings

from schemas.settings import SettingsUpdate, SettingsResponse
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"]
)


# =========================================================
# DEFAULT SETTINGS
# =========================================================

DEFAULT_SETTINGS = {
    "general_language": "en",
    "general_timezone": "UTC",
    "general_date_format": "MM/DD/YYYY",
    "general_auto_save": True,

    "appearance_theme": "dark",
    "appearance_compact_mode": False,
    "appearance_animations": True,

    "notif_analysis_completed": True,
    "notif_new_knowledge": True,
    "notif_bug_alerts": True,
    "notif_system_notifications": False,

    "privacy_save_history": True,
    "privacy_store_resolved": True,
    "privacy_usage_analytics": False,

    "ai_suggestions": True,
    "ai_historical_retrieval": True,
    "ai_root_cause": True,
    "ai_fix_recommendations": True
}


# =========================================================
# GET CURRENT USER SETTINGS
# =========================================================

@router.get(
    "",
    response_model=SettingsResponse
)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    settings = (
        db.query(UserSettings)
        .filter(UserSettings.user_id == current_user.id)
        .first()
    )

    # Existing users may not have a settings row because
    # the settings table was recreated.
    if settings is None:

        settings = UserSettings(
            user_id=current_user.id,
            **DEFAULT_SETTINGS
        )

        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


# =========================================================
# UPDATE CURRENT USER SETTINGS
# =========================================================

@router.put(
    "",
    response_model=SettingsResponse
)
def update_settings(
    settings_data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    settings = (
        db.query(UserSettings)
        .filter(UserSettings.user_id == current_user.id)
        .first()
    )

    if settings is None:

        settings = UserSettings(
            user_id=current_user.id,
            **DEFAULT_SETTINGS
        )

        db.add(settings)
        db.commit()
        db.refresh(settings)

    # Update only fields supplied by frontend
    update_data = settings_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)

    return settings


# =========================================================
# RESET SETTINGS TO DEFAULT
# =========================================================

@router.post(
    "/reset",
    response_model=SettingsResponse
)
def reset_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    settings = (
        db.query(UserSettings)
        .filter(UserSettings.user_id == current_user.id)
        .first()
    )

    if settings is None:

        settings = UserSettings(
            user_id=current_user.id,
            **DEFAULT_SETTINGS
        )

        db.add(settings)

    else:

        for field, value in DEFAULT_SETTINGS.items():
            setattr(settings, field, value)

    db.commit()
    db.refresh(settings)

    return settings