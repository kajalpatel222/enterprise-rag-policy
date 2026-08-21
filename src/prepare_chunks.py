"""Preview structural chunks from the ACME policy corpus."""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SECTION_PATTERN = re.compile(
    r"(?m)^(?P<number>\d+)\.\s+(?P<title>[^\n]+)\n[-=]+\n"
)


def extract_chunks(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8").strip()
    matches = list(SECTION_PATTERN.finditer(text))
    chunks: list[dict[str, str]] = []

    for index, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        chunks.append(
            {
                "text": f"{match.group('title').strip()}\n\n{body}",
                "source_file": str(path.relative_to(PROJECT_ROOT)),
                "section_number": match.group("number"),
                "section_title": match.group("title").strip(),
            }
        )

    return chunks


def main() -> None:
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
        print(all_chunks[0]["text"][:600])


if __name__ == "__main__":
    main()
