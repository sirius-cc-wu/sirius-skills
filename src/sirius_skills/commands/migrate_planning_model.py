#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from sirius_skills.commands import manage_planning, manage_subfeatures


STORY_REF_PATTERN = re.compile(r"Parent story:\s*`([^`]+)`", re.IGNORECASE)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or apply the simplified feature/subfeature planning model migration."
    )
    parser.add_argument("--apply", action="store_true", help="Apply safe migration actions.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    parser.add_argument("--scope", default=None, help="Optional planning scope path.")
    return parser.parse_args(argv)


def normalize_story_ids(items: List[str]) -> List[str]:
    normalized: List[str] = []
    for item in items:
        candidate = item.strip()
        if not candidate or candidate.upper() == "TBD":
            continue
        if candidate not in normalized:
            normalized.append(candidate)
    return normalized


def read_json_payload(path: Path) -> object:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Registry JSON is not valid JSON: {path}") from exc


def read_registry_rows(path: Path, key: str) -> List[Dict[str, object]]:
    payload = read_json_payload(path)
    if isinstance(payload, list):
        raw_rows = payload
    elif isinstance(payload, dict):
        raw_rows = payload.get(key, [])
    else:
        raw_rows = []
    if not isinstance(raw_rows, list):
        return []
    return [row for row in raw_rows if isinstance(row, dict)]


def infer_story_ids(subfeature_dir: Path) -> List[str]:
    candidates: List[str] = []
    discover_path = subfeature_dir / "discover.md"
    if discover_path.exists():
        candidates.extend(STORY_REF_PATTERN.findall(discover_path.read_text(encoding="utf-8")))
    return normalize_story_ids(candidates)


def action(kind: str, path: Path, message: str, applied: bool, details: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    return {
        "kind": kind,
        "path": manage_planning.normalize_feature_path(str(path)),
        "message": message,
        "applied": applied,
        "details": details or {},
    }


def rebuild_feature_registry_rows(scope_context: object, planning_dir: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for feature_dir in manage_planning.discover_feature_dirs(planning_dir):
        metadata = manage_planning.read_metadata(feature_dir)
        rows.append(manage_planning.build_registry_row(feature_dir, metadata, scope_context))
    return sorted(rows, key=lambda row: (str(row["path"]), row.get("updated_at") or ""))


def rebuild_subfeature_registry_rows(feature_dir: Path, scope_context: object) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    subfeatures_root = feature_dir / manage_subfeatures.SUBFEATURES_DIR_NAME
    if not subfeatures_root.exists():
        return []
    for subfeature_dir in sorted(path for path in subfeatures_root.iterdir() if path.is_dir()):
        if not (subfeature_dir / manage_subfeatures.METADATA_FILE).exists():
            continue
        metadata = manage_subfeatures.read_metadata(str(subfeature_dir))
        rows.append(
            manage_subfeatures.normalize_registry_row(
                {
                    "subfeature_id": metadata.get("subfeature_id", subfeature_dir.name),
                    "status": metadata.get("status", "draft"),
                    "subfeature_type": metadata.get("subfeature_type", "additive"),
                    "updated_at": metadata.get("updated_at"),
                    "path": manage_planning.relative_path_from_scope_root(
                        str(subfeature_dir), scope_context
                    ),
                }
            )
        )
    return sorted(rows, key=lambda row: (str(row["path"]), row.get("updated_at") or ""))


def build_migration_result(apply: bool = False, explicit_scope: Optional[str] = None) -> Dict[str, object]:
    scope_context = manage_planning.SCOPE_RUNTIME.resolve_scope_context(explicit_scope=explicit_scope)
    planning_dir, _, registry_path = manage_planning.get_registry_paths(
        required_config=False, scope_context=scope_context
    )
    planning_root = Path(planning_dir)
    registry = Path(registry_path)
    actions: List[Dict[str, object]] = []

    feature_dirs = [Path(path) for path in manage_planning.discover_feature_dirs(planning_dir)]
    for feature_dir in feature_dirs:
        subfeature_registry = feature_dir / manage_subfeatures.SUBFEATURES_DIR_NAME / "registry.json"
        if not subfeature_registry.exists():
            if apply:
                manage_subfeatures.ensure_subfeature_registry(str(feature_dir))
            actions.append(
                action(
                    "ensure_subfeature_registry",
                    subfeature_registry,
                    "Feature is missing the default subfeature registry.",
                    apply,
                )
            )

        rebuilt_subfeature_rows = rebuild_subfeature_registry_rows(feature_dir, scope_context)
        if rebuilt_subfeature_rows:
            current_subfeature_rows = [
                manage_subfeatures.normalize_registry_row(row)
                for row in read_registry_rows(subfeature_registry, "subfeatures")
            ]
            current_subfeature_rows = sorted(
                current_subfeature_rows,
                key=lambda row: (str(row["path"]), row.get("updated_at") or ""),
            )
            if current_subfeature_rows != rebuilt_subfeature_rows:
                if apply:
                    manage_subfeatures.write_registry(str(feature_dir), rebuilt_subfeature_rows)
                actions.append(
                    action(
                        "rebuild_subfeature_registry",
                        subfeature_registry,
                        "Feature-local subfeature registry is missing or stale; rebuild it from subfeature metadata.",
                        apply,
                        {"rebuilt_count": len(rebuilt_subfeature_rows)},
                    )
                )

        if (feature_dir / "slice-planning.md").exists() or (feature_dir / "slice-traceability.md").exists():
            actions.append(
                action(
                    "legacy_feature_breakdown",
                    feature_dir,
                    "Feature-level breakdown artifacts are legacy direct-feature execution planning; move future execution planning into subfeatures.",
                    False,
                )
            )

    raw_rows = read_registry_rows(registry, "features")
    has_subfeature_rows = any(
        "/subfeatures/" in str(row.get("path", "")) for row in raw_rows
    )
    if has_subfeature_rows:
        rebuilt_rows = rebuild_feature_registry_rows(scope_context, planning_dir)
        if apply:
            manage_planning.write_registry(rebuilt_rows, scope_context=scope_context)
        actions.append(
            action(
                "rebuild_feature_registry",
                registry,
                "Top-level planning registry contains subfeature rows; rebuild it as feature-only.",
                apply,
                {"rebuilt_count": len(rebuilt_rows)},
            )
        )

    for subfeature_dir_str in manage_planning.discover_subfeature_dirs(planning_dir):
        subfeature_dir = Path(subfeature_dir_str)
        if (subfeature_dir / "user-stories.md").exists():
            actions.append(
                action(
                    "deprecated_subfeature_user_stories",
                    subfeature_dir / "user-stories.md",
                    "Subfeature-local user-stories.md is deprecated; keep stories in the parent feature and reference story IDs from metadata.",
                    False,
                )
            )

        metadata = manage_subfeatures.read_metadata(str(subfeature_dir))
        story_ids = [item for item in metadata.get("story_ids", []) if isinstance(item, str) and item.strip()]
        if story_ids:
            continue
        inferred_story_ids = infer_story_ids(subfeature_dir)
        if not inferred_story_ids:
            actions.append(
                action(
                    "missing_subfeature_story_ids",
                    subfeature_dir,
                    "Subfeature has no story_ids and no safe parent-story references could be inferred.",
                    False,
                )
            )
            continue
        if apply:
            updated_metadata = dict(metadata)
            updated_metadata["story_ids"] = inferred_story_ids
            if not updated_metadata.get("affected_story_ids"):
                updated_metadata["affected_story_ids"] = inferred_story_ids
            manage_subfeatures.write_metadata(str(subfeature_dir), updated_metadata)
        actions.append(
            action(
                "populate_subfeature_story_ids",
                subfeature_dir,
                "Populate subfeature story_ids from explicit parent-story references.",
                apply,
                {"story_ids": inferred_story_ids},
            )
        )

    return {
        "ok": True,
        "apply": apply,
        "planning_root": manage_planning.normalize_feature_path(str(planning_root)),
        "summary": {
            "actions": len(actions),
            "applied": sum(1 for item in actions if item["applied"]),
        },
        "actions": actions,
    }


def render_text(result: Dict[str, object]) -> str:
    mode = "apply" if result.get("apply") else "dry-run"
    lines = [
        f"Planning model migration ({mode})",
        f"Planning root: {result['planning_root']}",
        f"Actions: {result['summary']['actions']} total, {result['summary']['applied']} applied",
    ]
    for item in result["actions"]:
        status = "applied" if item["applied"] else "reported"
        lines.append(f"- {item['kind']} ({status}): {item['path']} - {item['message']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        result = build_migration_result(apply=args.apply, explicit_scope=args.scope)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
