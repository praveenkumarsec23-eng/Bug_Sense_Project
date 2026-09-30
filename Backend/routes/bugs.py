from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from sqlalchemy.orm import Session
import logging

from database.database import get_db

from database.models import (
    User,
    Bug,
    Analysis,
    KnowledgeEntry
)

from routes.auth import get_current_user
from schemas.bug import BugCreate

from agents.orchestrator import run_bug_analysis

from services.file_service import (
    process_source_file,
    SourceFileError
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/bugs",
    tags=["Bugs"]
)


# =========================================================
# UPLOAD SOURCE FILE
# =========================================================

@router.post("/upload-source")
async def upload_source_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        file_content = await file.read()

        result = process_source_file(
            filename=file.filename,
            file_content=file_content
        )

        return {
            "message": "Source file uploaded successfully",
            "file": {
                "filename": result["filename"],
                "language": result["language"],
                "code": result["code"],
                "size": result["size"]
            }
        }

    except SourceFileError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        logger.exception("Unexpected error while processing source file")
        raise HTTPException(
            status_code=500,
            detail="Failed to process source file."
        )


# =========================================================
# ANALYZE / SUBMIT BUG
# =========================================================

@router.post("/analyze")
def analyze_bug(
    bug_data: BugCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    if not bug_data.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Bug title is required"
        )

    if not bug_data.language.strip():
        raise HTTPException(
            status_code=400,
            detail="Programming language is required"
        )

    has_bug_content = any([
        bug_data.description
        and bug_data.description.strip(),

        bug_data.error_message
        and bug_data.error_message.strip(),

        bug_data.stack_trace
        and bug_data.stack_trace.strip(),

        bug_data.code
        and bug_data.code.strip()
    ])

    if not has_bug_content:
        raise HTTPException(
            status_code=400,
            detail="Please provide bug details"
        )

    # =====================================================
    # LOAD KNOWLEDGE BASE
    # =====================================================

    knowledge_entries = []

    if (
        bug_data.search_similar_bugs
        or bug_data.detect_duplicates
    ):
        try:
            knowledge_entries = (
                db.query(KnowledgeEntry)
                .all()
            )

        except Exception:
            logger.exception("Failed to load Knowledge Base during analysis")
            raise HTTPException(
                status_code=500,
                detail="Unable to load the Knowledge Base."
            )

    # =====================================================
    # AGENT ORCHESTRATOR
    # =====================================================

    try:
        orchestrator_result = run_bug_analysis(
            title=bug_data.title,
            language=bug_data.language,
            description=bug_data.description or "",
            error_message=bug_data.error_message or "",
            stack_trace=bug_data.stack_trace or "",
            code=bug_data.code or "",

            analyze_root_cause=(
                bug_data.analyze_root_cause
            ),

            search_similar_bugs=(
                bug_data.search_similar_bugs
            ),

            detect_duplicates=(
                bug_data.detect_duplicates
            ),

            generate_fix_recommendation=(
                bug_data.generate_fix_recommendation
            ),

            knowledge_entries=knowledge_entries
        )

    except Exception:
        logger.exception("Agent orchestrator failed during bug analysis")
        raise HTTPException(
            status_code=500,
            detail="Bug analysis could not be completed."
        )

    # =====================================================
    # EXTRACT ORCHESTRATOR RESULTS
    # =====================================================

    triage_result = orchestrator_result["triage"]

    log_result = orchestrator_result[
        "log_analysis"
    ]

    root_cause_result = orchestrator_result[
        "root_cause"
    ]

    similar_bugs = orchestrator_result[
        "rag"
    ]["similar_bugs"]

    duplicate_result = orchestrator_result[
        "duplicate_detection"
    ]

    remediation_result = orchestrator_result[
        "remediation"
    ]

    # =====================================================
    # CREATE BUG
    # =====================================================

    bug = Bug(
        user_id=current_user.id,
        title=bug_data.title.strip(),
        language=bug_data.language.strip(),
        description=bug_data.description,
        error_message=bug_data.error_message,
        stack_trace=bug_data.stack_trace,
        code=bug_data.code,

        # Generated by Triage Agent
        severity=triage_result["severity"],

        status="Analyzed"
    )

    db.add(bug)
    db.commit()
    db.refresh(bug)

    # =====================================================
    # CREATE ANALYSIS
    # =====================================================

    analysis = Analysis(
        bug_id=bug.id,

        # =================================================
        # TRIAGE AGENT OUTPUT
        # =================================================

        bug_type=triage_result["bug_type"],
        priority=triage_result["priority"],
        triage_reason=triage_result["reason"],

        # =================================================
        # LOG ANALYSIS AGENT OUTPUT
        # =================================================

        exception_type=log_result["exception"],
        failure_file=log_result["file"],
        failure_line=log_result["line"],
        failure_function=log_result["function"],
        failure_code=log_result["failure_code"],

        # =================================================
        # ROOT CAUSE AGENT OUTPUT
        # =================================================

        root_cause=(
            root_cause_result["root_cause"]
            if root_cause_result
            else None
        ),

        explanation=(
            root_cause_result["explanation"]
            if root_cause_result
            else None
        ),

        # =================================================
        # DUPLICATE DETECTION AGENT OUTPUT
        # =================================================

        is_duplicate=(
            duplicate_result["is_duplicate"]
            if duplicate_result
            else False
        ),

        duplicate_confidence=(
            duplicate_result["duplicate_confidence"]
            if duplicate_result
            else 0.0
        ),

        matched_bug_id=(
            duplicate_result["matched_bug_id"]
            if duplicate_result
            else None
        ),

        matched_knowledge_id=(
            duplicate_result["matched_knowledge_id"]
            if duplicate_result
            else None
        ),

        duplicate_reason=(
            duplicate_result["reason"]
            if duplicate_result
            else "Duplicate detection was not performed."
        ),

        # =================================================
        # REMEDIATION AGENT OUTPUT
        # =================================================

        solution=(
            remediation_result["solution"]
            if remediation_result
            else None
        ),

        fixed_code=(
            remediation_result["fixed_code"]
            if remediation_result
            else None
        ),

        # This represents Root Cause confidence
        confidence=(
            root_cause_result["confidence"]
            if root_cause_result
            else 0.0
        )
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "message": "Bug analyzed successfully",

        "orchestrator": {
            "name": orchestrator_result["orchestrator"],
            "agents": orchestrator_result["agents"],
            "rag_matches_found": (
                orchestrator_result["rag"][
                    "matches_found"
                ]
            )
        },

        "bug": {
            "id": bug.id,
            "bug_id": f"BUG-{bug.id}",
            "title": bug.title,
            "language": bug.language,
            "description": bug.description,
            "error_message": bug.error_message,
            "stack_trace": bug.stack_trace,
            "code": bug.code,
            "severity": bug.severity,
            "status": bug.status,
            "created_at": bug.created_at
        },

        "analysis": {
            "id": analysis.id,
            "bug_id": analysis.bug_id,

            # =============================================
            # TRIAGE AGENT
            # =============================================

            "bug_type": analysis.bug_type,
            "priority": analysis.priority,
            "triage_reason": analysis.triage_reason,

            # =============================================
            # LOG ANALYSIS AGENT
            # =============================================

            "exception_type": analysis.exception_type,
            "failure_file": analysis.failure_file,
            "failure_line": analysis.failure_line,
            "failure_function": analysis.failure_function,
            "failure_code": analysis.failure_code,

            # =============================================
            # ROOT CAUSE AGENT
            # =============================================

            "root_cause": analysis.root_cause,
            "explanation": analysis.explanation,
            "confidence": analysis.confidence,

            # =============================================
            # DUPLICATE DETECTION AGENT
            # =============================================

            "is_duplicate": analysis.is_duplicate,

            "duplicate_confidence": (
                analysis.duplicate_confidence
            ),

            "matched_bug_id": (
                analysis.matched_bug_id
            ),

            "matched_knowledge_id": (
                analysis.matched_knowledge_id
            ),

            "duplicate_reason": (
                analysis.duplicate_reason
            ),

            "similar_bugs": similar_bugs,

            # =============================================
            # REMEDIATION AGENT
            # =============================================

            "solution": analysis.solution,
            "fixed_code": analysis.fixed_code,

            "remediation_reasoning": (
                remediation_result["reasoning"]
                if remediation_result
                else None
            ),

            "remediation_confidence": (
                remediation_result["confidence"]
                if remediation_result
                else 0.0
            ),

            "created_at": analysis.created_at
        }
    }


# =========================================================
# BUG HISTORY
# =========================================================

@router.get("/history")
def get_bug_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bugs = (
        db.query(Bug)
        .filter(
            Bug.user_id == current_user.id
        )
        .order_by(
            Bug.created_at.desc()
        )
        .all()
    )

    history = []

    for bug in bugs:
        analysis = (
            db.query(Analysis)
            .filter(
                Analysis.bug_id == bug.id
            )
            .first()
        )

        history.append({
            "id": bug.id,
            "bug_id": f"BUG-{bug.id}",
            "title": bug.title,
            "language": bug.language,
            "severity": bug.severity,
            "status": bug.status,
            "created_at": bug.created_at,

            "bug_type": (
                analysis.bug_type
                if analysis
                else None
            ),

            "priority": (
                analysis.priority
                if analysis
                else None
            ),

            "triage_reason": (
                analysis.triage_reason
                if analysis
                else None
            ),

            "confidence": (
                analysis.confidence
                if analysis
                else None
            )
        })

    return {
        "count": len(history),
        "bugs": history
    }


# =========================================================
# RESOLVE BUG AND ADD TO KNOWLEDGE BASE
# =========================================================

@router.post("/{bug_id}/resolve")
def resolve_bug(
    bug_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bug = (
        db.query(Bug)
        .filter(
            Bug.id == bug_id,
            Bug.user_id == current_user.id
        )
        .first()
    )

    if not bug:
        raise HTTPException(
            status_code=404,
            detail="Bug not found"
        )

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.bug_id == bug.id
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=400,
            detail="Bug analysis not found"
        )

    existing_entry = (
        db.query(KnowledgeEntry)
        .filter(
            KnowledgeEntry.bug_id == bug.id
        )
        .first()
    )

    # =====================================================
    # ALREADY EXISTS IN KNOWLEDGE BASE
    # =====================================================

    if existing_entry:
        bug.status = "Resolved"

        db.commit()
        db.refresh(bug)

        return {
            "message": (
                "Bug is already resolved and stored "
                "in the Knowledge Base"
            ),
            "bug_id": f"BUG-{bug.id}",
            "knowledge_id": (
                f"KB-{existing_entry.id}"
            ),
            "status": bug.status
        }

    # =====================================================
    # CREATE KNOWLEDGE BASE ENTRY
    # =====================================================

    knowledge_entry = KnowledgeEntry(
        bug_id=bug.id,
        title=bug.title,

        category=(
            analysis.bug_type
            or "Uncategorized"
        ),

        language=bug.language,
        description=bug.description,

        # Root Cause Agent output
        root_cause=analysis.root_cause,

        # Remediation Agent output
        solution=analysis.solution,

        source="Resolved Bug"
    )

    bug.status = "Resolved"

    db.add(knowledge_entry)
    db.commit()

    db.refresh(knowledge_entry)
    db.refresh(bug)

    return {
        "message": (
            "Bug resolved and added "
            "to the Knowledge Base"
        ),
        "bug_id": f"BUG-{bug.id}",
        "knowledge_id": (
            f"KB-{knowledge_entry.id}"
        ),
        "status": bug.status
    }

# =========================================================
# RE-ANALYZE EXISTING BUG
# =========================================================

@router.post("/{bug_id}/reanalyze")
def reanalyze_bug(
    bug_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # =====================================================
    # GET EXISTING BUG
    # =====================================================

    bug = (
        db.query(Bug)
        .filter(
            Bug.id == bug_id,
            Bug.user_id == current_user.id
        )
        .first()
    )

    if not bug:
        raise HTTPException(
            status_code=404,
            detail="Bug not found"
        )

    # =====================================================
    # GET EXISTING ANALYSIS
    # =====================================================

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.bug_id == bug.id
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Bug analysis not found"
        )

    # =====================================================
    # LOAD CURRENT KNOWLEDGE BASE
    # =====================================================

    try:
        knowledge_entries = (
            db.query(KnowledgeEntry)
            .all()
        )

    except Exception:
        logger.exception("Failed to load Knowledge Base during re-analysis")
        raise HTTPException(
            status_code=500,
            detail="Unable to load the Knowledge Base."
        )

    # =====================================================
    # RUN MULTI-AGENT ORCHESTRATOR AGAIN
    # =====================================================

    try:
        orchestrator_result = run_bug_analysis(
            title=bug.title,
            language=bug.language,
            description=bug.description or "",
            error_message=bug.error_message or "",
            stack_trace=bug.stack_trace or "",
            code=bug.code or "",

            analyze_root_cause=True,
            search_similar_bugs=True,
            detect_duplicates=True,
            generate_fix_recommendation=True,

            knowledge_entries=knowledge_entries
        )

    except Exception:
        logger.exception("Agent orchestrator failed during bug re-analysis")
        raise HTTPException(
            status_code=500,
            detail="Bug re-analysis could not be completed."
        )

    # =====================================================
    # EXTRACT RESULTS
    # =====================================================

    triage_result = orchestrator_result["triage"]
    log_result = orchestrator_result["log_analysis"]
    root_cause_result = orchestrator_result["root_cause"]

    similar_bugs = orchestrator_result[
        "rag"
    ]["similar_bugs"]

    duplicate_result = orchestrator_result[
        "duplicate_detection"
    ]

    remediation_result = orchestrator_result[
        "remediation"
    ]

    # =====================================================
    # UPDATE BUG
    # =====================================================

    bug.severity = triage_result["severity"]

    # Re-analysis means the latest analysis is available.
    # Do not automatically create a Knowledge Base entry here.
    if bug.status != "Resolved":
        bug.status = "Analyzed"

    # =====================================================
    # UPDATE EXISTING ANALYSIS
    # =====================================================

    # Triage Agent
    analysis.bug_type = triage_result["bug_type"]
    analysis.priority = triage_result["priority"]
    analysis.triage_reason = triage_result["reason"]

    # Log Analysis Agent
    analysis.exception_type = log_result["exception"]
    analysis.failure_file = log_result["file"]
    analysis.failure_line = log_result["line"]
    analysis.failure_function = log_result["function"]
    analysis.failure_code = log_result["failure_code"]

    # Root Cause Agent
    analysis.root_cause = (
        root_cause_result["root_cause"]
        if root_cause_result
        else None
    )

    analysis.explanation = (
        root_cause_result["explanation"]
        if root_cause_result
        else None
    )

    analysis.confidence = (
        root_cause_result["confidence"]
        if root_cause_result
        else 0.0
    )

    # Duplicate Detection Agent
    analysis.is_duplicate = (
        duplicate_result["is_duplicate"]
        if duplicate_result
        else False
    )

    analysis.duplicate_confidence = (
        duplicate_result["duplicate_confidence"]
        if duplicate_result
        else 0.0
    )

    analysis.matched_bug_id = (
        duplicate_result["matched_bug_id"]
        if duplicate_result
        else None
    )

    analysis.matched_knowledge_id = (
        duplicate_result["matched_knowledge_id"]
        if duplicate_result
        else None
    )

    analysis.duplicate_reason = (
        duplicate_result["reason"]
        if duplicate_result
        else "Duplicate detection was not performed."
    )

    # Remediation Agent
    analysis.solution = (
        remediation_result["solution"]
        if remediation_result
        else None
    )

    analysis.fixed_code = (
        remediation_result["fixed_code"]
        if remediation_result
        else None
    )

    # =====================================================
    # SAVE UPDATED RESULTS
    # =====================================================

    try:
        db.commit()
        db.refresh(bug)
        db.refresh(analysis)

    except Exception:
        db.rollback()
        logger.exception("Failed to save bug re-analysis results")

        raise HTTPException(
            status_code=500,
            detail="Re-analysis results could not be saved."
        )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "message": "Bug re-analyzed successfully",

        "bug": {
            "id": bug.id,
            "bug_id": f"BUG-{bug.id}",
            "title": bug.title,
            "language": bug.language,
            "severity": bug.severity,
            "status": bug.status
        },

        "analysis": {
            "id": analysis.id,
            "bug_id": analysis.bug_id,

            "bug_type": analysis.bug_type,
            "priority": analysis.priority,
            "triage_reason": analysis.triage_reason,

            "exception_type": analysis.exception_type,
            "failure_file": analysis.failure_file,
            "failure_line": analysis.failure_line,
            "failure_function": analysis.failure_function,
            "failure_code": analysis.failure_code,

            "root_cause": analysis.root_cause,
            "explanation": analysis.explanation,
            "confidence": analysis.confidence,

            "is_duplicate": analysis.is_duplicate,
            "duplicate_confidence": (
                analysis.duplicate_confidence
            ),
            "matched_bug_id": analysis.matched_bug_id,
            "matched_knowledge_id": (
                analysis.matched_knowledge_id
            ),
            "duplicate_reason": (
                analysis.duplicate_reason
            ),
            "similar_bugs": similar_bugs,

            "solution": analysis.solution,
            "fixed_code": analysis.fixed_code,

            "remediation_reasoning": (
                remediation_result["reasoning"]
                if remediation_result
                else None
            ),

            "remediation_confidence": (
                remediation_result["confidence"]
                if remediation_result
                else 0.0
            )
        },

        "orchestrator": {
            "name": orchestrator_result["orchestrator"],
            "agents": orchestrator_result["agents"],
            "rag_matches_found": (
                orchestrator_result["rag"]["matches_found"]
            )
        }
    }
# =========================================================
# GET SINGLE BUG + ANALYSIS RESULT
# =========================================================

@router.get("/{bug_id}")
def get_bug_result(
    bug_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bug = (
        db.query(Bug)
        .filter(
            Bug.id == bug_id,
            Bug.user_id == current_user.id
        )
        .first()
    )

    if not bug:
        raise HTTPException(
            status_code=404,
            detail="Bug not found"
        )

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.bug_id == bug.id
        )
        .first()
    )

    # =====================================================
    # MATCHED KNOWLEDGE BASE ENTRY
    # =====================================================

    matched_knowledge = None

    if (
        analysis
        and analysis.matched_knowledge_id
    ):
        matched_entry = (
            db.query(KnowledgeEntry)
            .filter(
                KnowledgeEntry.id
                == analysis.matched_knowledge_id
            )
            .first()
        )

        if matched_entry:
            matched_knowledge = {
                "knowledge_id": matched_entry.id,
                "bug_id": matched_entry.bug_id,
                "title": matched_entry.title,
                "category": matched_entry.category,
                "language": matched_entry.language,
                "description": matched_entry.description,
                "root_cause": matched_entry.root_cause,
                "solution": matched_entry.solution,
                "source": matched_entry.source
            }

    return {
        "bug": {
            "id": bug.id,
            "bug_id": f"BUG-{bug.id}",
            "title": bug.title,
            "language": bug.language,
            "description": bug.description,
            "error_message": bug.error_message,
            "stack_trace": bug.stack_trace,
            "code": bug.code,
            "severity": bug.severity,
            "status": bug.status,
            "created_at": bug.created_at
        },

        "analysis": {
            "id": (
                analysis.id
                if analysis
                else None
            ),

            "bug_id": (
                analysis.bug_id
                if analysis
                else None
            ),

            # =============================================
            # TRIAGE AGENT
            # =============================================

            "bug_type": (
                analysis.bug_type
                if analysis
                else None
            ),

            "priority": (
                analysis.priority
                if analysis
                else None
            ),

            "triage_reason": (
                analysis.triage_reason
                if analysis
                else None
            ),

            # =============================================
            # LOG ANALYSIS AGENT
            # =============================================

            "exception_type": (
                analysis.exception_type
                if analysis
                else None
            ),

            "failure_file": (
                analysis.failure_file
                if analysis
                else None
            ),

            "failure_line": (
                analysis.failure_line
                if analysis
                else None
            ),

            "failure_function": (
                analysis.failure_function
                if analysis
                else None
            ),

            "failure_code": (
                analysis.failure_code
                if analysis
                else None
            ),

            # =============================================
            # ROOT CAUSE AGENT
            # =============================================

            "root_cause": (
                analysis.root_cause
                if analysis
                else None
            ),

            "explanation": (
                analysis.explanation
                if analysis
                else None
            ),

            "confidence": (
                analysis.confidence
                if analysis
                else None
            ),

            # =============================================
            # DUPLICATE DETECTION AGENT
            # =============================================

            "is_duplicate": (
                analysis.is_duplicate
                if analysis
                else False
            ),

            "duplicate_confidence": (
                analysis.duplicate_confidence
                if analysis
                else 0.0
            ),

            "matched_bug_id": (
                analysis.matched_bug_id
                if analysis
                else None
            ),

            "matched_knowledge_id": (
                analysis.matched_knowledge_id
                if analysis
                else None
            ),

            "duplicate_reason": (
                analysis.duplicate_reason
                if analysis
                else None
            ),

            "matched_knowledge": matched_knowledge,

            # =============================================
            # REMEDIATION AGENT
            # =============================================

            "solution": (
                analysis.solution
                if analysis
                else None
            ),

            "fixed_code": (
                analysis.fixed_code
                if analysis
                else None
            ),

            "created_at": (
                analysis.created_at
                if analysis
                else None
            )
        }
    }