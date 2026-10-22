#!/usr/bin/env python3
"""Check a build submission folder before you submit it.

    python3 tools/check_submission.py path/to/our-submission

A submission needs:
  README.md    with a "# <team name>" title and these sections:
               "## Lane", "## What it does", "## How to use it", "## Where this fails"
  AI-USE.md    every AI tool you used, how, and links to exported chats or transcripts
               (write "None" under a "## Tools" heading if you used none)
and no file over 25 MB, nothing that looks like a secret key, and no real personal data.

The secret-key check reads text files: the suffixes in TEXT_SUFFIXES (code, notes, data,
config and shell files, and .pem/.key key files), files with no extension, and .env files.
Images, PDFs, Word files and other binary formats are skipped, and so is any file over 25 MB.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MAX_BYTES = 25 * 1024 * 1024
README_SECTIONS = ["## Lane", "## What it does", "## How to use it", "## Where this fails"]
SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".env", ".sh", ".html", ".csv", ".ipynb", ".pem", ".key",
}


def problems(folder: Path) -> list[str]:
    out = []
    readme = folder / "README.md"
    if not readme.exists():
        out.append("README.md is missing")
    else:
        text = readme.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^# \S", text, re.M):
            out.append("README.md needs a '# Team name' title on its first heading")
        for s in README_SECTIONS:
            if not re.search(rf"^{re.escape(s)}\s*$", text, re.M):
                out.append(f"README.md needs a '{s}' section")
    ai = folder / "AI-USE.md"
    if not ai.exists():
        out.append("AI-USE.md is missing (list your tools, or write None under '## Tools')")
    elif not re.search(r"^## Tools\s*$", ai.read_text(encoding="utf-8", errors="replace"), re.M):
        out.append("AI-USE.md needs a '## Tools' section")
    for p in folder.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = p.relative_to(folder)
        if p.stat().st_size > MAX_BYTES:
            out.append(f"{rel} is over 25 MB")
        elif p.suffix.lower() in TEXT_SUFFIXES or p.suffix == "" or p.name.startswith(".env"):
            if SECRET.search(p.read_text(encoding="utf-8", errors="replace")):
                out.append(f"{rel} looks like it contains a secret key; remove it and rotate the key")
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1 or not Path(argv[0]).is_dir():
        print(__doc__)
        return 2
    found = problems(Path(argv[0]))
    for p in found:
        print(f"- {p}")
    print("Ready to submit." if not found else f"{len(found)} thing(s) to fix before submitting.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
