"""Write the compiled RAG workflow as Mermaid text without running it."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_graph import create_rag_graph  # noqa: E402

OUTPUT_PATH = PROJECT_ROOT / "docs" / "rag_graph.mmd"


def main() -> None:
    """Compile the graph with inert dependencies and export its topology."""
    unused_dependency = object()
    compiled_graph = create_rag_graph(
        vector_store=unused_dependency,
        standard_chat=unused_dependency,
        complex_chat=unused_dependency,
    )

    mermaid_text = compiled_graph.get_graph().draw_mermaid()
    OUTPUT_PATH.write_text(f"{mermaid_text.rstrip()}\n", encoding="utf-8")
    print(f"Wrote LangGraph visualization to {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
