# -*- coding: utf-8 -*-
"""Export question/code data for generating code_explanations.json.

This script is intentionally read-only for the existing app files:
- reads ../index.html and extracts `const docs = [...]`
- reads ../build_review_page.py and extracts `MANUAL_CODE_BLOCKS`
- writes normalized JSON files under ../data/
"""

from __future__ import annotations

import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_HTML = BASE_DIR / "index.html"
BUILD_SCRIPT = BASE_DIR / "build_review_page.py"
DATA_DIR = BASE_DIR / "data"
DOCS_OUT = DATA_DIR / "docs_for_explanations.json"
MANUAL_OUT = DATA_DIR / "manual_code_blocks_export.json"
MANUAL_TXT_FALLBACK = DATA_DIR / "manual_code_blocks_export.txt"


def extract_const_array(source: str, variable_name: str) -> str:
    """Extract a complete JavaScript array assigned to `const variable_name`.

    The scanner matches brackets while ignoring brackets inside strings and JS
    comments. It does not evaluate JavaScript; it only slices the array text.
    """

    match = re.search(rf"\bconst\s+{re.escape(variable_name)}\s*=", source)
    if not match:
        raise ValueError(f"Could not find `const {variable_name} =`.")

    start = match.end()
    while start < len(source) and source[start].isspace():
        start += 1

    if start >= len(source) or source[start] != "[":
        raise ValueError(f"`const {variable_name}` does not start with an array.")

    depth = 0
    in_string: str | None = None
    escape = False
    in_line_comment = False
    in_block_comment = False

    for index in range(start, len(source)):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""

        if in_line_comment:
            if char in "\r\n":
                in_line_comment = False
            continue

        if in_block_comment:
            if char == "*" and nxt == "/":
                in_block_comment = False
            continue

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue

        if char in ('"', "'", "`"):
            in_string = char
            continue

        if char == "/" and nxt == "/":
            in_line_comment = True
            continue

        if char == "/" and nxt == "*":
            in_block_comment = True
            continue

        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]

    raise ValueError(f"Could not find the end of `const {variable_name}` array.")


def normalize_code_blocks(raw_blocks: Any) -> list[str]:
    """Return a clean list of code strings from the app's question structure."""

    if not isinstance(raw_blocks, list):
        return []

    normalized: list[str] = []
    for block in raw_blocks:
        if isinstance(block, str):
            code = block.strip()
        elif isinstance(block, dict):
            code = str(block.get("code", "")).strip()
        else:
            code = ""

        if code:
            normalized.append(code)

    return normalized


def load_docs_from_index() -> list[dict[str, Any]]:
    html = INDEX_HTML.read_text(encoding="utf-8")
    docs_text = extract_const_array(html, "docs")
    docs = json.loads(docs_text)
    if not isinstance(docs, list):
        raise ValueError("Extracted docs value is not a list.")
    return docs


def export_docs_for_explanations(docs: list[dict[str, Any]]) -> dict[str, Any]:
    questions: list[dict[str, Any]] = []
    per_doc_counts: Counter[str] = Counter()
    code_count = 0
    empty_code_count = 0

    for doc in docs:
        doc_id = str(doc.get("id", "")).strip()
        pdf_file = str(doc.get("file", "")).strip()
        doc_title = str(doc.get("title", "")).strip()

        for question in doc.get("questions", []):
            number = int(question.get("number", 0))
            display_id = f"Q{number:02d}"
            code_blocks = normalize_code_blocks(question.get("codeBlocks", []))
            has_code = bool(code_blocks)

            if has_code:
                code_count += 1
            else:
                empty_code_count += 1

            per_doc_counts[doc_id] += 1
            questions.append(
                {
                    "questionId": f"{doc_id}-{display_id}",
                    "docId": doc_id,
                    "docTitle": doc_title,
                    "pdfFile": pdf_file,
                    "number": number,
                    "displayId": display_id,
                    "title": str(question.get("title", "")).strip(),
                    "codeBlocks": code_blocks,
                    "sourcePages": question.get("sourcePages", []),
                    "hasCode": has_code,
                }
            )

    payload = {
        "schemaVersion": "1.0.0",
        "source": "index.html const docs",
        "questions": questions,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "totalDocs": len(docs),
        "totalQuestions": len(questions),
        "questionsWithCode": code_count,
        "questionsWithoutCode": empty_code_count,
        "perDocQuestionCounts": dict(per_doc_counts),
    }


def extract_manual_code_blocks_source(source: str) -> str:
    match = re.search(r"^MANUAL_CODE_BLOCKS\s*=", source, flags=re.MULTILINE)
    if not match:
        raise ValueError("Could not find MANUAL_CODE_BLOCKS assignment.")

    start = match.start()
    brace_start = source.find("{", match.end())
    if brace_start == -1:
        raise ValueError("Could not find MANUAL_CODE_BLOCKS opening brace.")

    depth = 0
    in_string: str | None = None
    escape = False
    triple_string: str | None = None

    for index in range(brace_start, len(source)):
        char = source[index]

        if triple_string:
            if source.startswith(triple_string, index):
                triple_string = None
            continue

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue

        if source.startswith('"""', index) or source.startswith("'''", index):
            triple_string = source[index : index + 3]
            continue

        if char in ('"', "'"):
            in_string = char
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]

    raise ValueError("Could not find MANUAL_CODE_BLOCKS closing brace.")


def export_manual_code_blocks(docs: list[dict[str, Any]]) -> bool:
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    pdf_to_doc_id = {str(doc.get("file", "")): str(doc.get("id", "")) for doc in docs}

    try:
        tree = ast.parse(source, filename=str(BUILD_SCRIPT))
        manual_value: dict[tuple[str, int], list[str]] | None = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                if "MANUAL_CODE_BLOCKS" in names:
                    manual_value = ast.literal_eval(node.value)
                    break

        if manual_value is None:
            raise ValueError("MANUAL_CODE_BLOCKS assignment not found by AST.")

        entries = []
        for key, code_blocks in manual_value.items():
            pdf_file, number = key
            doc_id = pdf_to_doc_id.get(pdf_file, Path(pdf_file).stem)
            display_id = f"Q{int(number):02d}"
            entries.append(
                {
                    "questionId": f"{doc_id}-{display_id}",
                    "docId": doc_id,
                    "pdfFile": pdf_file,
                    "number": int(number),
                    "displayId": display_id,
                    "codeBlocks": [str(code).strip() for code in code_blocks if str(code).strip()],
                }
            )

        entries.sort(key=lambda item: (item["docId"], item["number"]))
        payload = {
            "schemaVersion": "1.0.0",
            "source": "build_review_page.py MANUAL_CODE_BLOCKS",
            "entries": entries,
        }
        MANUAL_OUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return True

    except Exception as exc:
        manual_source = extract_manual_code_blocks_source(source)
        MANUAL_TXT_FALLBACK.write_text(
            f"# Failed to parse MANUAL_CODE_BLOCKS automatically: {exc}\n\n"
            + manual_source
            + "\n",
            encoding="utf-8",
        )
        return False


def main() -> None:
    docs = load_docs_from_index()
    stats = export_docs_for_explanations(docs)
    manual_json_ok = export_manual_code_blocks(docs)

    print(f"docs_for_explanations: {DOCS_OUT}")
    if manual_json_ok:
        print(f"manual_code_blocks_export: {MANUAL_OUT}")
    else:
        print(f"manual_code_blocks_export fallback: {MANUAL_TXT_FALLBACK}")

    print("\nStatistics")
    print(f"- Total docs: {stats['totalDocs']}")
    print(f"- Total questions: {stats['totalQuestions']}")
    print(f"- Questions with code: {stats['questionsWithCode']}")
    print(f"- Questions without code: {stats['questionsWithoutCode']}")
    print("- Questions per docId:")
    for doc_id, count in stats["perDocQuestionCounts"].items():
        print(f"  - {doc_id}: {count}")


if __name__ == "__main__":
    main()
