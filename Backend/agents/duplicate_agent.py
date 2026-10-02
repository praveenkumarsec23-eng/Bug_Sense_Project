import re
from difflib import SequenceMatcher


class DuplicateDetectionAgent:
    def __init__(self):
        self.name = "Duplicate Detection Agent"

    def _normalize(self, text):
        if not text:
            return ""

        text = str(text).lower().strip()
        text = re.sub(r"[^a-z0-9_]+", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _text_similarity(self, first, second):
        first = self._normalize(first)
        second = self._normalize(second)

        if not first or not second:
            return 0.0

        return SequenceMatcher(
            None,
            first,
            second
        ).ratio()

    def _calculate_duplicate_score(
        self,
        current_title,
        current_description,
        current_error_message,
        current_language,
        current_exception,
        candidate
    ):
        # ---------------------------------------------
        # Stable signals for duplicate detection
        # ---------------------------------------------

        title_score = self._text_similarity(
            current_title,
            candidate.get("title", "")
        )

        description_score = self._text_similarity(
            current_description,
            candidate.get("description", "")
        )

        current_language_normalized = self._normalize(
            current_language
        )

        candidate_language_normalized = self._normalize(
            candidate.get("language", "")
        )

        language_score = (
            1.0
            if (
                current_language_normalized
                and current_language_normalized
                == candidate_language_normalized
            )
            else 0.0
        )

        # RAG remains useful as an additional signal,
        # but it is no longer the entire duplicate score.
        rag_score = float(
            candidate.get("similarity", 0.0)
        )

        # Exact title matches are a very strong duplicate signal.
        if title_score >= 0.98:
            duplicate_score = (
                (0.55 * title_score)
                + (0.20 * description_score)
                + (0.10 * language_score)
                + (0.15 * rag_score)
            )
        else:
            duplicate_score = (
                (0.40 * title_score)
                + (0.25 * description_score)
                + (0.10 * language_score)
                + (0.25 * rag_score)
            )

        return min(
            round(duplicate_score, 4),
            1.0
        )

    def analyze(
        self,
        similar_bugs=None,
        duplicate_threshold=0.70,
        title="",
        description="",
        error_message="",
        language="",
        exception_type=""
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

        scored_candidates = []

        for candidate in similar_bugs:
            candidate_copy = dict(candidate)

            duplicate_score = self._calculate_duplicate_score(
                current_title=title,
                current_description=description,
                current_error_message=error_message,
                current_language=language,
                current_exception=exception_type,
                candidate=candidate
            )

            candidate_copy["duplicate_similarity"] = (
                duplicate_score
            )

            candidate_copy["duplicate_similarity_percent"] = (
                round(duplicate_score * 100, 2)
            )

            scored_candidates.append(
                candidate_copy
            )

        scored_candidates.sort(
            key=lambda item: item[
                "duplicate_similarity"
            ],
            reverse=True
        )

        best_match = scored_candidates[0]

        similarity = float(
            best_match.get(
                "duplicate_similarity",
                0.0
            )
        )

        is_duplicate = (
            similarity >= duplicate_threshold
        )

        similarity_percent = round(
            similarity * 100,
            2
        )

        if is_duplicate:
            reason = (
                f"A historical bug matches the current "
                f"bug with {similarity_percent}% "
                f"duplicate confidence."
            )
        else:
            reason = (
                f"The closest historical bug has "
                f"{similarity_percent}% duplicate confidence, "
                f"which is below the duplicate threshold."
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
    duplicate_threshold=0.70,
    title="",
    description="",
    error_message="",
    language="",
    exception_type=""
):
    return DuplicateDetectionAgent().analyze(
        similar_bugs=similar_bugs,
        duplicate_threshold=duplicate_threshold,
        title=title,
        description=description,
        error_message=error_message,
        language=language,
        exception_type=exception_type
    )