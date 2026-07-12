from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = REPO_ROOT / "src" / "sirius_skills" / "commands"
WRITE_OWNER_ALLOWLIST = {
    "archive_data",
    "bootstrap",
    "close_slice",
    "manage_execution",
    "manage_planning",
    "manage_proposals",
    "manage_subfeatures",
    "metrics_store",
    "migrate_subfeatures",
    "research",
    "scaffold_breakdown",
    "scaffold_design",
    "ship",
}


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _call_owner(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id
    return None


def _string_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _write_call_signature(node: ast.Call) -> str | None:
    call_name = _call_name(node)
    if call_name in {"write_text", "write_bytes"}:
        return call_name

    if call_name == "dump" and _call_owner(node) == "json":
        return "json.dump"

    if call_name != "open":
        return None

    mode = None
    if len(node.args) >= 2:
        mode = _string_literal(node.args[1])
    for keyword in node.keywords:
        if keyword.arg == "mode":
            mode = _string_literal(keyword.value)

    if mode is None:
        return None

    if any(flag in mode for flag in ("w", "a", "x", "+")):
        return f"open({mode})"

    return None


def _scan_direct_write_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        signature = _write_call_signature(node)
        if signature is not None:
            violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}:{signature}")

    return violations


def test_commands_do_not_add_new_direct_workspace_writes() -> None:
    violations: list[str] = []

    for path in sorted(COMMANDS_DIR.glob("*.py")):
        if path.name == "__init__.py" or path.stem in WRITE_OWNER_ALLOWLIST:
            continue
        violations.extend(_scan_direct_write_calls(path))

    assert not violations, (
        "New direct workspace writes in src/sirius_skills/commands/ must be "
        f"moved behind an owned helper:\n" + "\n".join(violations)
    )
