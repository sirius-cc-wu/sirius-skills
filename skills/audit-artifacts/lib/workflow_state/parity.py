import os
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

from workflow_state.models import InstalledParityRecord


def _resolve_source_repo_root() -> Optional[Path]:
    current = Path(__file__).resolve()
    required_paths = (
        Path("skills") / "guide-planning" / "scripts" / "manage_planning.py",
        Path("skills") / "propose" / "scripts" / "manage_proposals.py",
        Path("skills") / "guide-execution" / "scripts" / "manage_execution.py",
        Path("skills") / "add-subfeature" / "scripts" / "manage_subfeatures.py",
    )
    for candidate in current.parents:
        if all((candidate / relpath).is_file() for relpath in required_paths):
            return candidate
    return None


REPO_ROOT = _resolve_source_repo_root()
SKILLS_ROOT = REPO_ROOT / "skills" if REPO_ROOT is not None else None
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
SKILL_HOME_ENV_VARS = ("CODEX_SKILLS_HOME",)


def _local_skill_home_candidates() -> List[Path]:
    candidates: List[Path] = []
    seen: set[Path] = set()

    def add_candidate(path: Path) -> None:
        expanded = path.expanduser()
        if expanded in seen:
            return
        seen.add(expanded)
        candidates.append(expanded)

    for env_var in SKILL_HOME_ENV_VARS:
        raw_value = os.environ.get(env_var)
        if raw_value:
            add_candidate(Path(raw_value))

    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        add_candidate(Path(codex_home) / "skills")

    home = Path.home()
    add_candidate(home / ".agents" / "skills")
    add_candidate(home / ".codex" / "skills")

    return candidates


def _discover_installed_skills_from_local_homes() -> List[Dict[str, str]]:
    installed: List[Dict[str, str]] = []
    seen_names = set()
    for root in _local_skill_home_candidates():
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            if not (child / "SKILL.md").is_file():
                continue
            if child.name in seen_names:
                continue
            seen_names.add(child.name)
            installed.append({"name": child.name, "path": str(child)})
    return installed


def discover_installed_skills() -> List[Dict[str, str]]:
    installed = _discover_installed_skills_from_local_homes()
    if installed:
        return installed
    searched = ", ".join(str(path) for path in _local_skill_home_candidates())
    raise RuntimeError(
        "Failed to inspect installed skills from local skill homes: "
        f"no installed skills found under {searched}."
    )


def inspect_installed_skill_parity(
    installed_skills: Optional[Sequence[Mapping[str, object]]] = None,
    skill_names: Optional[Sequence[str]] = None,
) -> List[InstalledParityRecord]:
    if SKILLS_ROOT is None:
        return [
            InstalledParityRecord(
                skill_name="installed-parity",
                relative_path=".",
                code="installed_parity_unavailable",
                message=(
                    "Installed skill parity is unavailable because no sirius-skills source "
                    "repository root could be resolved from the packaged runtime."
                ),
                repo_path="",
                installed_path="",
            )
        ]
    if installed_skills is not None:
        listing = installed_skills
    else:
        try:
            listing = discover_installed_skills()
        except RuntimeError as exc:
            return [
                InstalledParityRecord(
                    skill_name="installed-parity",
                    relative_path=".",
                    code="installed_parity_unavailable",
                    message=str(exc),
                    repo_path=str(SKILLS_ROOT),
                    installed_path="",
                )
            ]
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
            findings.append(
                InstalledParityRecord(
                    skill_name="installed-parity",
                    relative_path=".",
                    code="installed_parity_unavailable",
                    message=f"Repo skill root is missing for parity target `{skill_name}`.",
                    repo_path=str(repo_root),
                    installed_path=str(installed_root),
                )
            )
            continue
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
