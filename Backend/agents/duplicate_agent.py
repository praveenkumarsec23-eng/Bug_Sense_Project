class DuplicateDetectionAgent:
    def __init__(self):
        self.name = "Duplicate Detection Agent"

    def analyze(
        self,
        similar_bugs=None,
        duplicate_threshold=0.70
    ):
        similar_bugs = similar_bugs or []

        if not similar_bugs:
            return {
                "agent": self.name,
                "is_duplicate": False,
                "duplicate_confidence": 0.0,
                "matched_bug_id": None,
                "matched_knowledge_id": None,
                "matched_title": None,
                "reason": (
                    "No sufficiently similar historical "
                    "bugs were found in the Knowledge Base."
                ),
                "similar_bugs": []
            }

        best_match = similar_bugs[0]

        similarity = float(
            best_match.get("similarity", 0.0)
        )

        is_duplicate = (
            similarity >= duplicate_threshold
        )

        if is_duplicate:
            reason = (
                f"A similar historical bug was found with "
                f"{best_match.get('similarity_percent', 0)}% "
                f"semantic similarity."
            )
        else:
            reason = (
                f"The closest historical bug has "
                f"{best_match.get('similarity_percent', 0)}% "
                f"semantic similarity, which is below the "
                f"duplicate threshold."
            )

        return {
            "agent": self.name,
            "is_duplicate": is_duplicate,
            "duplicate_confidence": round(
                similarity,
                4
            ),
            "matched_bug_id": best_match.get(
                "bug_id"
            ),
            "matched_knowledge_id": best_match.get(
                "knowledge_id"
            ),
            "matched_title": best_match.get(
                "title"
            ),
            "reason": reason,
            "similar_bugs": similar_bugs
        }


def run_duplicate_agent(
    similar_bugs=None,
    duplicate_threshold=0.70
):
    return DuplicateDetectionAgent().analyze(
        similar_bugs=similar_bugs,
        duplicate_threshold=duplicate_threshold
    )