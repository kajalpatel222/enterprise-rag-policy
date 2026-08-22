"""Preview structural chunks from the ACME policy corpus."""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SECTION_PATTERN = re.compile(
    r"(?m)^(?P<number>\d+)\.\s+(?P<title>[^\n]+)\n[-=]+\n"
)
SUBSECTION_PATTERN = re.compile(r"(?m)^(?!\s)(?P<title>[A-Z][^:\n]{1,60}):\s*$")
VERSION_PATTERN = re.compile(
    r"Version\s+(?P<version>[^|\n]+)\|\s+(?P<label>[^:]+):\s+(?P<date>[^\n]+)"
)


def extract_chunks(path: Path) -> list[dict[str, object]]:
    # Read one source document and identify its numbered policy sections.
    text = path.read_text(encoding="utf-8").strip()
    matches = list(SECTION_PATTERN.finditer(text))
    chunks: list[dict[str, object]] = []
    version_match = VERSION_PATTERN.search(text)
    document_version = version_match.group("version").strip() if version_match else ""
    document_date_label = version_match.group("label").strip() if version_match else ""
    document_date = version_match.group("date").strip() if version_match else ""
    document_title = text.splitlines()[0].strip()
    department = path.parent.name

    for index, match in enumerate(matches):
        # A section ends where the next numbered section begins.
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        # Keep clear subsection labels as optional metadata for later citations.
        subsection_titles = [
            match.group("title").strip()
            for match in SUBSECTION_PATTERN.finditer(body)
            if not match.group("title").startswith(("The ", "To ", "ACME ", "Example "))
        ]
        chunks.append(
            {
                "text": f"{match.group('title').strip()}\n\n{body}",
                "source_file": str(path.relative_to(PROJECT_ROOT)),
                "department": department,
                "document_title": document_title,
                "document_version": document_version,
                "document_date_label": document_date_label,
                "document_date": document_date,
                "section_number": match.group("number"),
                "section_title": match.group("title").strip(),
                "subsection_titles": subsection_titles,
            }
        )

    return chunks


def main() -> None:
    # Preview every source file without calling an external service.
    files = sorted(RAW_DATA_DIR.glob("*/*.txt"))
    all_chunks = [chunk for path in files for chunk in extract_chunks(path)]

    print(f"Documents found: {len(files)}")
    print(f"Policy chunks found: {len(all_chunks)}")

    for chunk in all_chunks:
        print(
            f"- {chunk['source_file']} | section {chunk['section_number']}: "
            f"{chunk['section_title']}"
        )

    if all_chunks:
        print("\nFirst chunk preview:\n")
        print("Metadata:")
        for key in (
            "department",
            "document_title",
            "document_version",
            "document_date_label",
            "document_date",
            "section_number",
            "section_title",
            "subsection_titles",
        ):
            print(f"  {key}: {all_chunks[0][key]}")
        print("\nText:")
        print(all_chunks[0]["text"][:600])


if __name__ == "__main__":
    main()
