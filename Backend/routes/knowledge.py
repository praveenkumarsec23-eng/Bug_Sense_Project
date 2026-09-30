from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User, KnowledgeEntry
from routes.auth import get_current_user


router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge Base"]
)


@router.get("")
def get_knowledge_base(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entries = (
        db.query(KnowledgeEntry)
        .order_by(KnowledgeEntry.created_at.desc())
        .all()
    )

    knowledge = []

    for entry in entries:

        bug = entry.bug

        knowledge.append({
            "id": entry.id,
            "knowledge_id": f"KB-{entry.id}",
            "bug_id": (
                f"BUG-{bug.id}"
                if bug
                else None
            ),
            "title": entry.title,
            "category": entry.category,
            "language": entry.language,
            "severity": (
                bug.severity
                if bug
                else None
            ),
            "status": (
                bug.status
                if bug
                else None
            ),
            "description": entry.description,
            "error": (
                bug.error_message
                if bug
                else None
            ),
            "root_cause": entry.root_cause,
            "solution": entry.solution,
            "source": entry.source,
            "created_at": entry.created_at
        })

    return {
        "count": len(knowledge),
        "entries": knowledge
    }