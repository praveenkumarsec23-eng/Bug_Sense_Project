import os
import re
from collections import Counter


class RAGService:
    """
    BugSense RAG service.

    By default, a lightweight local similarity search is used so that
    BugSense can run on low-memory environments such as Render's
    free 512 MB instance.

    Semantic SentenceTransformer RAG can be enabled later with:

        ENABLE_SEMANTIC_RAG=true

    This keeps the RAG architecture available without forcing the
    heavy ML model to load during application startup.
    """

    def __init__(self):
        self.model = None
        self.util = None

        self.semantic_enabled = (
            os.getenv("ENABLE_SEMANTIC_RAG", "false").lower()
            == "true"
        )

    def _load_semantic_model(self):
        """
        Load SentenceTransformer only when semantic RAG is explicitly enabled.
        """

        if not self.semantic_enabled:
            return False

        if self.model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer, util

            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

            self.util = util

            return True

        except Exception:
            self.model = None
            self.util = None
            return False

    def build_query(
        self,
        title="",
        description="",
        error_message="",
        bug_type="",
        language="",
        exception_type="",
        root_cause=""
    ):
        parts = [
            title or "",
            description or "",
            error_message or "",
            bug_type or "",
            language or "",
            exception_type or "",
            root_cause or ""
        ]

        return " ".join(
            part.strip()
            for part in parts
            if part and part.strip()
        )

    def build_knowledge_text(self, entry):
        parts = [
            entry.title or "",
            entry.category or "",
            entry.language or "",
            entry.description or "",
            entry.root_cause or "",
            entry.solution or ""
        ]

        return " ".join(
            str(part).strip()
            for part in parts
            if part and str(part).strip()
        )

    def _tokenize(self, text):
        """
        Lightweight tokenization used by the fallback RAG search.
        """

        return set(
            re.findall(
                r"[a-zA-Z0-9_]+",
                text.lower()
            )
        )

    def _keyword_similarity(self, query, text):
        """
        Lightweight similarity calculation.

        This does not require PyTorch, Transformers, or any
        other heavy ML package.

        It calculates overlap between important words in the
        bug query and the historical knowledge entry.
        """

        query_tokens = self._tokenize(query)
        text_tokens = self._tokenize(text)

        if not query_tokens or not text_tokens:
            return 0.0

        common_tokens = query_tokens.intersection(text_tokens)

        if not common_tokens:
            return 0.0

        # Jaccard similarity
        similarity = (
            len(common_tokens)
            / len(query_tokens.union(text_tokens))
        )

        return float(similarity)

    def _lightweight_search(
        self,
        query,
        valid_entries,
        knowledge_texts,
        top_k,
        minimum_score
    ):
        """
        Lightweight RAG fallback.

        Used by default on low-memory deployments.
        """

        results = []

        for entry, text in zip(
            valid_entries,
            knowledge_texts
        ):
            similarity = self._keyword_similarity(
                query,
                text
            )

            if similarity < minimum_score:
                continue

            results.append({
                "knowledge_id": entry.id,
                "bug_id": entry.bug_id,
                "title": entry.title,
                "category": entry.category,
                "language": entry.language,
                "description": entry.description,
                "root_cause": entry.root_cause,
                "solution": entry.solution,
                "source": entry.source,
                "similarity": round(
                    similarity,
                    4
                ),
                "similarity_percent": round(
                    similarity * 100,
                    2
                )
            })

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return results[:top_k]

    def _semantic_search(
        self,
        query,
        valid_entries,
        knowledge_texts,
        top_k,
        minimum_score
    ):
        """
        Original SentenceTransformer-based semantic RAG.

        The model is loaded lazily only when explicitly enabled.
        """

        if not self._load_semantic_model():
            return None

        query_embedding = self.model.encode(
            query,
            convert_to_tensor=True
        )

        knowledge_embeddings = self.model.encode(
            knowledge_texts,
            convert_to_tensor=True
        )

        similarities = self.util.cos_sim(
            query_embedding,
            knowledge_embeddings
        )[0]

        results = []

        for index, score in enumerate(similarities):

            similarity = float(
                score.item()
            )

            if similarity < minimum_score:
                continue

            entry = valid_entries[index]

            results.append({
                "knowledge_id": entry.id,
                "bug_id": entry.bug_id,
                "title": entry.title,
                "category": entry.category,
                "language": entry.language,
                "description": entry.description,
                "root_cause": entry.root_cause,
                "solution": entry.solution,
                "source": entry.source,
                "similarity": round(
                    similarity,
                    4
                ),
                "similarity_percent": round(
                    similarity * 100,
                    2
                )
            })

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return results[:top_k]

    def search(
        self,
        query,
        knowledge_entries,
        top_k=3,
        minimum_score=0.25
    ):
        """
        Search historical BugSense knowledge.

        Default:
            Lightweight RAG

        Optional:
            SentenceTransformer semantic RAG
        """

        if not query or not query.strip():
            return []

        if not knowledge_entries:
            return []

        valid_entries = []
        knowledge_texts = []

        for entry in knowledge_entries:

            text = self.build_knowledge_text(
                entry
            )

            if not text:
                continue

            valid_entries.append(entry)
            knowledge_texts.append(text)

        if not valid_entries:
            return []

        # -------------------------------------------------
        # SEMANTIC RAG
        # -------------------------------------------------

        if self.semantic_enabled:

            semantic_results = self._semantic_search(
                query,
                valid_entries,
                knowledge_texts,
                top_k,
                minimum_score
            )

            if semantic_results is not None:
                return semantic_results

        # -------------------------------------------------
        # LIGHTWEIGHT RAG FALLBACK
        # -------------------------------------------------

        return self._lightweight_search(
            query,
            valid_entries,
            knowledge_texts,
            top_k,
            minimum_score
        )


# Create the service WITHOUT loading any ML model.
rag_service = RAGService()