#!/usr/bin/env python3
"""Validate repository structure and Markdown portability without dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "CHANGELOG.md",
    "components/bom/BOM.xlsx",
    "components/bom/Full_BOM.xlsx",
    "docs/03-design/guides/README.md",
    "docs/04-calculations/INA241A2IDDFR_Output_Calculation.pdf",
    "docs/decisions/0001-coexisting-hardware-variants.md",
    "docs/workflow.md",
    "hardware/One_Board_Design/README.md",
    "hardware/Split_Board_Design/README.md",
    "hardware/Split_Board_Design/Control_Board/README.md",
    "hardware/Split_Board_Design/Relay_Board/README.md",
    "hardware/Split_Board_Design/interface/README.md",
    "hardware/libraries/README.md",
    "tools/README.md",
)

MOJIBAKE_MARKERS = ("ß╗", "├¡", "ΓÇ", "─æ", "╞░", "ï¿½", "�")
UPPERCASE_TOP_LEVEL = re.compile(r"(?<![A-Za-z0-9_])(?:Docs|Hardware)/")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in REPO_ROOT.rglob("*.md")
        if ".git" not in path.parts
    )


def normalize_link_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = re.sub(r"\s+[\"'][^\"']*[\"']\s*$", "", target)

    if not target or target.startswith("#"):
        return None

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None

    path = unquote(parsed.path)
    return path or None


def check_required_paths(errors: list[str]) -> None:
    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required path: {relative_path}")


def check_markdown(errors: list[str]) -> int:
    checked = 0
    for document in markdown_files():
        checked += 1
        relative_document = document.relative_to(REPO_ROOT).as_posix()
        text = document.read_text(encoding="utf-8")

        for marker in MOJIBAKE_MARKERS:
            if marker in text:
                errors.append(
                    f"mojibake marker {marker!r} in {relative_document}"
                )

        for match in UPPERCASE_TOP_LEVEL.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                f"uppercase top-level path at {relative_document}:{line}: "
                f"{match.group(0)}"
            )

        for raw_target in MARKDOWN_LINK.findall(text):
            target = normalize_link_target(raw_target)
            if target is None:
                continue
            resolved = (document.parent / Path(target)).resolve()
            if not resolved.is_relative_to(REPO_ROOT):
                errors.append(
                    f"local link escapes repository in {relative_document}: {target}"
                )
            elif not resolved.exists():
                errors.append(
                    f"broken local link in {relative_document}: {target}"
                )

    return checked


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    errors: list[str] = []
    check_required_paths(errors)

    try:
        checked_markdown = check_markdown(errors)
    except UnicodeDecodeError as exc:
        errors.append(f"Markdown is not valid UTF-8: {exc}")
        checked_markdown = 0

    if errors:
        print(f"Repository check: FAIL ({len(errors)} error(s))")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Repository check: PASS "
        f"({len(REQUIRED_PATHS)} required paths, "
        f"{checked_markdown} Markdown files)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
