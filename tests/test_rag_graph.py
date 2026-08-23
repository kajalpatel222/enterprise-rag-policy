"""Fast offline checks for the two LangGraph answer branches."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from langchain_core.documents import Document

from src.rag_graph import create_rag_graph


class FakeVectorStore:
    """Return one predictable chunk without contacting Pinecone."""

    def similarity_search_with_score(self, _question: str, k: int):
        document = Document(
            page_content="Remote work requirements and policy evidence.",
            metadata={"section_title": "REMOTE WORK POLICY"},
        )
        return [(document, 0.8)][:k]


class FakeChat:
    """Record model calls without contacting OpenRouter."""

    def __init__(self, name: str):
        self.name = name
        self.call_count = 0

    def invoke(self, _prompt: str):
        self.call_count += 1
        return SimpleNamespace(content=f"Answer from {self.name}")


class RAGGraphTests(unittest.TestCase):
    def setUp(self):
        self.standard_chat = FakeChat("standard")
        self.complex_chat = FakeChat("complex")
        self.graph = create_rag_graph(
            FakeVectorStore(),
            self.standard_chat,
            self.complex_chat,
        )

    def test_simple_question_uses_standard_branch(self):
        result = self.graph.invoke({"question": "Does ACME offer a stipend?"})

        self.assertEqual(result["route"], "standard")
        self.assertEqual(result["answer"], "Answer from standard")
        self.assertEqual(self.standard_chat.call_count, 1)
        self.assertEqual(self.complex_chat.call_count, 0)

    def test_complex_question_uses_complex_branch(self):
        result = self.graph.invoke(
            {"question": "What is the difference between the requirements?"}
        )

        self.assertEqual(result["route"], "complex")
        self.assertEqual(result["answer"], "Answer from complex")
        self.assertEqual(self.standard_chat.call_count, 0)
        self.assertEqual(self.complex_chat.call_count, 1)


if __name__ == "__main__":
    unittest.main()

