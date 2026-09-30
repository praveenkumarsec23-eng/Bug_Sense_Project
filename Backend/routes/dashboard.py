from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.database import get_db
from database.models import User, Bug, Analysis, KnowledgeEntry
from routes.auth import get_current_user


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    user_id = current_user.id

    total_bugs = (
        db.query(Bug)
        .filter(Bug.user_id == user_id)
        .count()
    )

    open_bugs = (
        db.query(Bug)
        .filter(
            Bug.user_id == user_id,
            func.lower(Bug.status) == "open"
        )
        .count()
    )

    resolved_bugs = (
        db.query(Bug)
        .filter(
            Bug.user_id == user_id,
            func.lower(Bug.status) == "resolved"
        )
        .count()
    )

    critical_bugs = (
        db.query(Bug)
        .filter(
            Bug.user_id == user_id,
            func.lower(Bug.severity) == "critical"
        )
        .count()
    )


    severity_levels = [
        "critical",
        "high",
        "medium",
        "low"
    ]

    severity = {}

    for level in severity_levels:

        severity[level] = (
            db.query(Bug)
            .filter(
                Bug.user_id == user_id,
                func.lower(Bug.severity) == level
            )
            .count()
        )


    category_rows = (
        db.query(
            Analysis.bug_type,
            func.count(Analysis.id)
        )
        .join(
            Bug,
            Analysis.bug_id == Bug.id
        )
        .filter(
            Bug.user_id == user_id
        )
        .group_by(
            Analysis.bug_type
        )
        .all()
    )

    categories = []

    for category, count in category_rows:

        categories.append({
            "category": category or "Uncategorized",
            "count": count
        })


    recent_bug_rows = (
        db.query(Bug, Analysis)
        .outerjoin(
            Analysis,
            Analysis.bug_id == Bug.id
        )
        .filter(
            Bug.user_id == user_id
        )
        .order_by(
            Bug.created_at.desc()
        )
        .limit(5)
        .all()
    )

    recent_bugs = []

    for bug, analysis in recent_bug_rows:

        recent_bugs.append({
            "id": bug.id,
            "bug_id": f"BUG-{bug.id}",
            "title": bug.title,
            "category": (
                analysis.bug_type
                if analysis and analysis.bug_type
                else "Uncategorized"
            ),
            "severity": bug.severity,
            "status": bug.status,
            "date": bug.created_at
        })


    recent_activity = []

    for bug, analysis in recent_bug_rows:

        recent_activity.append({
            "type": "analysis",
            "bug_id": f"BUG-{bug.id}",
            "message": f"BUG-{bug.id} analyzed",
            "created_at": bug.created_at
        })


    historical_bugs = (
        db.query(KnowledgeEntry)
        .count()
    )

    resolved_issues = (
        db.query(Bug)
        .filter(
            Bug.user_id == user_id,
            func.lower(Bug.status) == "resolved"
        )
        .count()
    )


    return {
        "summary": {
            "total_bugs": total_bugs,
            "open_bugs": open_bugs,
            "resolved_bugs": resolved_bugs,
            "critical_bugs": critical_bugs
        },

        "severity": severity,

        "categories": categories,

        "recent_bugs": recent_bugs,

        "recent_activity": recent_activity,

        "knowledge_base": {
            "historical_bugs": historical_bugs,
            "resolved_issues": resolved_issues
        }
    }