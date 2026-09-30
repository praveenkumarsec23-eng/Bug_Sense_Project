from database.database import SessionLocal
from database.models import Bug, Analysis, KnowledgeEntry
from services.rag_service import rag_service


def main():
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # LOAD BUG-38
        # -------------------------------------------------

        bug = db.query(Bug).filter(
            Bug.id == 38
        ).first()

        if not bug:
            print("BUG-38 was not found.")
            return

        # -------------------------------------------------
        # LOAD BUG-38 ANALYSIS
        # -------------------------------------------------

        analysis = db.query(Analysis).filter(
            Analysis.bug_id == bug.id
        ).first()

        if not analysis:
            print("Analysis for BUG-38 was not found.")
            return

        # -------------------------------------------------
        # BUILD SAME SEMANTIC QUERY
        # -------------------------------------------------

        query = rag_service.build_query(
            title=bug.title,
            description=bug.description or "",
            error_message=bug.error_message or "",
            bug_type=analysis.bug_type or "",
            language=bug.language or "",
            exception_type=analysis.exception_type or "",
            root_cause=analysis.root_cause or ""
        )

        print()
        print("=" * 70)
        print("BUG-38 RAG CONTINUOUS-LEARNING TEST")
        print("=" * 70)

        print()
        print("QUERY:")
        print(query)

        # -------------------------------------------------
        # LOAD CURRENT KNOWLEDGE BASE
        # -------------------------------------------------

        knowledge_entries = (
            db.query(KnowledgeEntry)
            .order_by(KnowledgeEntry.id.asc())
            .all()
        )

        print()
        print(
            f"Knowledge Base entries loaded: "
            f"{len(knowledge_entries)}"
        )

        # -------------------------------------------------
        # RUN SEMANTIC SEARCH
        # -------------------------------------------------

        results = rag_service.search(
            query=query,
            knowledge_entries=knowledge_entries,
            top_k=10,
            minimum_score=0.0
        )

        print()
        print("=" * 70)
        print("TOP SEMANTIC MATCHES")
        print("=" * 70)

        if not results:
            print("No matches found.")
            return

        for position, result in enumerate(
            results,
            start=1
        ):
            print()
            print(f"Rank: {position}")
            print(
                f"Knowledge ID: "
                f"KB-{result['knowledge_id']}"
            )

            bug_id = result.get("bug_id")

            if bug_id:
                print(f"Bug ID: BUG-{bug_id}")
            else:
                print("Bug ID: Historical Knowledge")

            print(
                f"Title: {result['title']}"
            )

            print(
                f"Language: {result['language']}"
            )

            print(
                f"Similarity: "
                f"{result['similarity_percent']}%"
            )

            print("-" * 70)

        # -------------------------------------------------
        # SPECIFICALLY CHECK KB-21 / BUG-36
        # -------------------------------------------------

        learned_entry = next(
            (
                result
                for result in results
                if result["knowledge_id"] == 21
            ),
            None
        )

        print()
        print("=" * 70)
        print("CONTINUOUS-LEARNING CHECK")
        print("=" * 70)

        if learned_entry:

            print("KB-21 was retrieved successfully.")
            print(
                f"Source Bug: BUG-"
                f"{learned_entry['bug_id']}"
            )
            print(
                f"Title: "
                f"{learned_entry['title']}"
            )
            print(
                f"Similarity: "
                f"{learned_entry['similarity_percent']}%"
            )

            print()
            print(
                "RESULT: Newly resolved knowledge is "
                "available to semantic RAG."
            )

        else:

            print(
                "KB-21 was not found in the "
                "top semantic results."
            )

            print()
            print(
                "RESULT: We need to inspect the "
                "retrieval behavior further."
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()