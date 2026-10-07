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

    def _contains_signal(self, signal, *candidate_fields):
        """
        Check whether an important technical signal from the
        current bug appears anywhere in the historical knowledge.
        """

        signal = self._normalize(signal)

        if not signal:
            return 0.0

        candidate_text = self._normalize(
            " ".join(
                str(field or "")
                for field in candidate_fields
            )
        )

        if not candidate_text:
            return 0.0

        return 1.0 if signal in candidate_text else 0.0

    def _calculate_duplicate_score(
        self,
        current_title,
        current_description,
        current_error_message,
        current_language,
        current_exception,
        candidate
    ):
        # -------------------------------------------------
        # Textual similarity signals
        # -------------------------------------------------

        title_score = self._text_similarity(
            current_title,
            candidate.get("title", "")
        )

        description_score = self._text_similarity(
            current_description,
            candidate.get("description", "")
        )

        # -------------------------------------------------
        # Programming-language signal
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Historical technical context
        #
        # The Knowledge Base currently stores title,
        # description, root cause and solution rather than
        # dedicated exception/error-message columns.
        # Search those fields for technical signals.
        # -------------------------------------------------

        candidate_context = (
            candidate.get("title", ""),
            candidate.get("description", ""),
            candidate.get("root_cause", ""),
            candidate.get("solution", "")
        )

        exception_score = self._contains_signal(
            current_exception,
            *candidate_context
        )

        error_score = self._contains_signal(
            current_error_message,
            *candidate_context
        )

        # -------------------------------------------------
        # RAG retrieval score
        # -------------------------------------------------

        rag_score = float(
            candidate.get("similarity", 0.0)
        )

        rag_score = max(
            0.0,
            min(rag_score, 1.0)
        )

        # -------------------------------------------------
        # Weighted duplicate score
        #
        # Technical signals receive meaningful weight so
        # that the decision is not dominated by broad
        # Knowledge Base text overlap.
        # -------------------------------------------------

        duplicate_score = (
            (0.30 * title_score)
            + (0.15 * description_score)
            + (0.10 * language_score)
            + (0.20 * exception_score)
            + (0.10 * error_score)
            + (0.15 * rag_score)
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
            "similar_bugs": scored_candidates
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