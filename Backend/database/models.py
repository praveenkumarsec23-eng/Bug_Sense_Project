from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Float,
    Boolean
)

from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


# =========================================================
# USER MODEL
# Used for Login and Profile
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default="Developer"
    )

    # Professional profile information
    primary_skills = Column(
        Text,
        nullable=True
    )

    specialization = Column(
        String(150),
        nullable=True
    )

    experience = Column(
        String(150),
        nullable=True
    )

    # Updated whenever profile information changes
    updated_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # One user can have many bugs
    bugs = relationship(
        "Bug",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One user has one settings record
    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

# =========================================================
# BUG MODEL
# Used for Bug Analyzer, Dashboard and Bug History
# =========================================================

class Bug(Base):
    __tablename__ = "bugs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)

    language = Column(String(50), nullable=False)

    description = Column(Text, nullable=True)

    error_message = Column(Text, nullable=True)

    stack_trace = Column(Text, nullable=True)

    code = Column(Text, nullable=True)

    severity = Column(String(50), nullable=True)

    status = Column(String(50), default="Analyzed")

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="bugs"
    )

    analysis = relationship(
        "Analysis",
        back_populates="bug",
        uselist=False,
        cascade="all, delete-orphan"
    )

# =========================================================
# ANALYSIS MODEL
# Used for Analysis Result and Bug History
# =========================================================

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    bug_id = Column(
        Integer,
        ForeignKey("bugs.id"),
        unique=True,
        nullable=False
    )

    # =====================================================
    # TRIAGE AGENT OUTPUT
    # =====================================================

    bug_type = Column(
        String(100),
        nullable=True
    )

    priority = Column(
        String(20),
        nullable=True
    )

    triage_reason = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # LOG ANALYSIS AGENT OUTPUT
    # =====================================================

    exception_type = Column(
        String(150),
        nullable=True
    )

    failure_file = Column(
        String(255),
        nullable=True
    )

    failure_line = Column(
        Integer,
        nullable=True
    )

    failure_function = Column(
        String(255),
        nullable=True
    )

    failure_code = Column(
        Text,
        nullable=True
    )

       # =====================================================
    # ROOT CAUSE AGENT OUTPUT
    # =====================================================

    root_cause = Column(
        Text,
        nullable=True
    )

    explanation = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # DUPLICATE DETECTION AGENT OUTPUT
    # =====================================================

    is_duplicate = Column(
        Boolean,
        nullable=True
    )

    duplicate_confidence = Column(
        Float,
        nullable=True
    )

    matched_bug_id = Column(
        Integer,
        nullable=True
    )

    matched_knowledge_id = Column(
        Integer,
        nullable=True
    )

    duplicate_reason = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # REMEDIATION AGENT OUTPUT
    # =====================================================

    solution = Column(
        Text,
        nullable=True
    )

    fixed_code = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # ANALYSIS CONFIDENCE
    # =====================================================

    confidence = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    bug = relationship(
        "Bug",
        back_populates="analysis"
    )

# =========================================================
# KNOWLEDGE ENTRY MODEL
# Used for Knowledge Base and future RAG
# =========================================================

class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Links this knowledge entry to the original bug
    bug_id = Column(
        Integer,
        ForeignKey("bugs.id"),
        nullable=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=True
    )

    language = Column(
        String(50),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    root_cause = Column(
        Text,
        nullable=True
    )

    solution = Column(
        Text,
        nullable=True
    )

    source = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Knowledge entry belongs to an original bug
    bug = relationship(
        "Bug"
    )


# =========================================================
# USER SETTINGS MODEL
# Used for Settings page
# =========================================================

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    # =====================================================
    # GENERAL SETTINGS
    # =====================================================

    general_language = Column(
        String(20),
        default="en"
    )

    general_timezone = Column(
        String(50),
        default="UTC"
    )

    general_date_format = Column(
        String(20),
        default="MM/DD/YYYY"
    )

    general_auto_save = Column(
        Boolean,
        default=True
    )


    # =====================================================
    # APPEARANCE
    # =====================================================

    appearance_theme = Column(
        String(20),
        default="dark"
    )

    appearance_compact_mode = Column(
        Boolean,
        default=False
    )

    appearance_animations = Column(
        Boolean,
        default=True
    )


    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    notif_analysis_completed = Column(
        Boolean,
        default=True
    )

    notif_new_knowledge = Column(
        Boolean,
        default=True
    )

    notif_bug_alerts = Column(
        Boolean,
        default=True
    )

    notif_system_notifications = Column(
        Boolean,
        default=False
    )


    # =====================================================
    # PRIVACY
    # =====================================================

    privacy_save_history = Column(
        Boolean,
        default=True
    )

    privacy_store_resolved = Column(
        Boolean,
        default=True
    )

    privacy_usage_analytics = Column(
        Boolean,
        default=False
    )


    # =====================================================
    # AI & DIAGNOSIS
    # =====================================================

    ai_suggestions = Column(
        Boolean,
        default=True
    )

    ai_historical_retrieval = Column(
        Boolean,
        default=True
    )

    ai_root_cause = Column(
        Boolean,
        default=True
    )

    ai_fix_recommendations = Column(
        Boolean,
        default=True
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    # Settings belong to one user
    user = relationship(
        "User",
        back_populates="settings"
    )