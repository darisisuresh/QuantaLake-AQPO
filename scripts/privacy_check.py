#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
tracked = subprocess.run(
    ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
).stdout.splitlines()

blocked_suffixes = {".docx", ".pdf", ".tex", ".txt"}
blocked_parts = {"raw", "private", "extracted-text", "reports"}
blocked_terms = (
    "darisi.suresh" + "@" + "ieee.org",
    "/" + "Users" + "/",
    "Co-" + "authored-by",
    "Co" + "dex",
    "Open" + "AI",
)
errors = []
for name in tracked:
    path = Path(name)
    if path.suffix.lower() in blocked_suffixes or blocked_parts.intersection(path.parts):
        errors.append(f"blocked path: {name}")
        continue
    full = ROOT / path
    if full.is_file():
        text = full.read_text(encoding="utf-8", errors="ignore")
        for term in blocked_terms:
            if term in text:
                errors.append(f"blocked term {term!r} in {name}")

if errors:
    raise SystemExit("Privacy gate failed:\n" + "\n".join(errors))
print(f"Privacy gate passed for {len(tracked)} tracked files")
