from __future__ import annotations

import re
from pathlib import Path


design = Path("docs/validation-refactoring.md").read_text(encoding="utf-8")
lowered = design.lower()

headings = (
    "System Boundary",
    "Representative Vertical Scenario",
    "Native Responsibilities",
    "Rust Ownership and Lifecycle",
    "Verification Ownership",
    "Completion Boundary",
)
for heading in headings:
    if not re.search(rf"^## {re.escape(heading)}$", design, re.MULTILINE):
        raise SystemExit(f"missing design-gate section: {heading}")

required_concepts = (
    "validation system",
    "UDS runtime",
    "DoIP runtime",
    "diagnostic client",
    "composition root",
    "VS task",
    "listeners",
    "child tasks",
    "Unix socket",
    "temporary workspace",
    "shutdown",
    "join",
    "focused",
    "integration",
    "end-to-end",
    "human-owned",
    "enabling result",
    "parent outcome remains open",
)
for concept in required_concepts:
    if concept.lower() not in lowered:
        raise SystemExit(f"missing design-gate concept: {concept}")

for premature_claim in (
    "Status: completed",
    "parent outcome is complete",
    "host-safe validation is complete",
):
    if premature_claim.lower() in lowered:
        raise SystemExit(f"premature completion claim: {premature_claim}")
