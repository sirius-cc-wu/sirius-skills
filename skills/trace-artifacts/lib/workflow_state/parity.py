import json
import subprocess
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

from workflow_state.inventory import REPO_ROOT as INVENTORY_REPO_ROOT
from workflow_state.models import InstalledParityRecord


REPO_ROOT = INVENTORY_REPO_ROOT
SKILLS_ROOT = REPO_ROOT / "skills"
PARITY_TARGETS: Dict[str, Sequence[str]] = {
    "audit-artifacts": (
        "scripts/audit_artifacts.py",
        "scripts/artifact_inventory.py",
        "lib/workflow_state",
    ),
    "trace-artifacts": (
        "scripts/trace_artifacts.py",
        "scripts/trace_data.py",
        "lib/workflow_state",
    ),
    "repair-artifacts": (
        "scripts/repair_artifacts.py",
        "scripts/repair_data.py",
        "lib/workflow_state",
    ),
    "report-artifacts": (
        "scripts/report_artifacts.py",
        "scripts/report_data.py",
        "scripts/metrics_store.py",
        "lib/workflow_state",
    ),
}
IGNORED_DIR_NAMES = {"__pycache__"}


def discover_installed_skills() -> List[Dict[str, str]]:
    completed = subprocess.run(
        ["npx", "skills", "ls", "-g", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Failed to inspect installed skills via `npx skills ls -g --json`: "
            f"{completed.stderr.strip() or 'command exited non-zero'}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Failed to parse installed skills from `npx skills ls -g --json`."
        ) from exc
    if not isinstance(payload, list):
        raise RuntimeError("Expected `npx skills ls -g --json` to return a JSON array.")

    installed: List[Dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise RuntimeError("Installed skill listing included a non-object entry.")
        name = item.get("name")
        path = item.get("path")
        if not isinstance(name, str) or not isinstance(path, str):
            raise RuntimeError("Installed skill listing entry is missing string `name` or `path`.")
        installed.append({"name": name, "path": path})
    return installed


def inspect_installed_skill_parity(
    installed_skills: Optional[Sequence[Mapping[str, object]]] = None,
    skill_names: Optional[Sequence[str]] = None,
) -> List[InstalledParityRecord]:
    listing = installed_skills if installed_skills is not None else discover_installed_skills()
    installed_by_name: Dict[str, Path] = {}
    for item in listing:
        name = item.get("name")
        path = item.get("path")
        if not isinstance(name, str) or not isinstance(path, str):
            raise RuntimeError("Installed skill listing entry is missing string `name` or `path`.")
        if name in PARITY_TARGETS:
            installed_by_name[name] = Path(path)

    findings: List[InstalledParityRecord] = []
    for skill_name in skill_names or tuple(PARITY_TARGETS):
        targets = PARITY_TARGETS.get(skill_name)
        if targets is None:
            continue
        installed_root = installed_by_name.get(skill_name)
        if installed_root is None:
            continue
        repo_root = SKILLS_ROOT / skill_name
        if not repo_root.is_dir():
            raise RuntimeError(f"Repo skill root is missing for parity target `{skill_name}`.")
        if not installed_root.is_dir():
            findings.append(
                InstalledParityRecord(
                    skill_name=skill_name,
                    relative_path=".",
                    code="missing_installed_root",
                    message=f"Installed `{skill_name}` skill root is missing.",
                    repo_path=str(repo_root),
                    installed_path=str(installed_root),
                )
            )
            continue
        for relative_target in targets:
            findings.extend(
                _compare_target(
                    skill_name=skill_name,
                    relative_target=relative_target,
                    repo_target=repo_root / relative_target,
                    installed_target=installed_root / relative_target,
                )
            )

    return sorted(findings, key=lambda item: (item.skill_name, item.relative_path, item.code))


def _compare_target(
    *,
    skill_name: str,
    relative_target: str,
    repo_target: Path,
    installed_target: Path,
) -> List[InstalledParityRecord]:
    if not repo_target.exists():
        raise RuntimeError(
            f"Repo parity target `{relative_target}` is missing for `{skill_name}`."
        )
    if repo_target.is_dir():
        return _compare_directory(
            skill_name=skill_name,
            relative_target=relative_target,
            repo_target=repo_target,
            installed_target=installed_target,
        )
    return _compare_file(
        skill_name=skill_name,
        relative_path=relative_target,
        repo_target=repo_target,
        installed_target=installed_target,
    )


def _compare_directory(
    *,
    skill_name: str,
    relative_target: str,
    repo_target: Path,
    installed_target: Path,
) -> List[InstalledParityRecord]:
    repo_snapshot = _snapshot_directory(repo_target)
    if not installed_target.is_dir():
        return [
            InstalledParityRecord(
                skill_name=skill_name,
                relative_path=relative_target,
                code="missing_installed_directory",
                message=f"Installed `{skill_name}` copy is missing `{relative_target}`.",
                repo_path=str(repo_target),
                installed_path=str(installed_target),
            )
        ]

    installed_snapshot = _snapshot_directory(installed_target)
    findings: List[InstalledParityRecord] = []
    for child_relpath, repo_bytes in sorted(repo_snapshot.items()):
        relative_path = f"{relative_target}/{child_relpath}"
        installed_bytes = installed_snapshot.get(child_relpath)
        if installed_bytes is None:
            findings.append(
                InstalledParityRecord(
                    skill_name=skill_name,
                    relative_path=relative_path,
                    code="missing_installed_file",
                    message=(
                        f"Installed `{skill_name}` copy is missing `{relative_path}`."
                    ),
                    repo_path=str(repo_target / child_relpath),
                    installed_path=str(installed_target / child_relpath),
                )
            )
            continue
        if installed_bytes != repo_bytes:
            findings.append(
                InstalledParityRecord(
                    skill_name=skill_name,
                    relative_path=relative_path,
                    code="content_mismatch",
                    message=(
                        f"Installed `{skill_name}` copy differs from the repo source at "
                        f"`{relative_path}`."
                    ),
                    repo_path=str(repo_target / child_relpath),
                    installed_path=str(installed_target / child_relpath),
                )
            )
    return findings


def _compare_file(
    *,
    skill_name: str,
    relative_path: str,
    repo_target: Path,
    installed_target: Path,
) -> List[InstalledParityRecord]:
    if not installed_target.is_file():
        return [
            InstalledParityRecord(
                skill_name=skill_name,
                relative_path=relative_path,
                code="missing_installed_file",
                message=f"Installed `{skill_name}` copy is missing `{relative_path}`.",
                repo_path=str(repo_target),
                installed_path=str(installed_target),
            )
        ]
    if installed_target.read_bytes() == repo_target.read_bytes():
        return []
    return [
        InstalledParityRecord(
            skill_name=skill_name,
            relative_path=relative_path,
            code="content_mismatch",
            message=(
                f"Installed `{skill_name}` copy differs from the repo source at "
                f"`{relative_path}`."
            ),
            repo_path=str(repo_target),
            installed_path=str(installed_target),
        )
    ]


def _snapshot_directory(root: Path) -> Dict[str, bytes]:
    snapshot: Dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        snapshot[str(path.relative_to(root))] = path.read_bytes()
    return snapshot
