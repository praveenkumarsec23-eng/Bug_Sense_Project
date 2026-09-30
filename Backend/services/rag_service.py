from sentence_transformers import SentenceTransformer, util


class RAGService:
    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

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

    def search(
        self,
        query,
        knowledge_entries,
        top_k=3,
        minimum_score=0.25
    ):
        if not query or not query.strip():
            return []

        if not knowledge_entries:
            return []

        valid_entries = []
        knowledge_texts = []

        for entry in knowledge_entries:
            text = self.build_knowledge_text(entry)

            if not text:
                continue

            valid_entries.append(entry)
            knowledge_texts.append(text)

        if not valid_entries:
            return []

        query_embedding = self.model.encode(
            query,
            convert_to_tensor=True
        )

        knowledge_embeddings = self.model.encode(
            knowledge_texts,
            convert_to_tensor=True
        )

        similarities = util.cos_sim(
            query_embedding,
            knowledge_embeddings
        )[0]

        results = []

        for index, score in enumerate(similarities):
            similarity = float(score.item())

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
                "similarity": round(similarity, 4),
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


rag_service = RAGService()