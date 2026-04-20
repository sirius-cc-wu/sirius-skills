#!/usr/bin/env python3

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath


SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = SCRIPT_DIR.parents[1]
GUIDE_PLANNING_SCRIPT = SKILLS_DIR / "guide-planning" / "scripts" / "manage_planning.py"
OUTPUT_FILE = "reference-research.md"


@dataclass(frozen=True)
class ResearchDetails:
    target_id: str
    target_type: str
    target_path: str
    planning_status: str
    question: str
    sources: list[str]
    chosen_reference: str
    decision: str
    alternatives: list[str]
    research_artifact: str


def load_module(script_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a durable reference-research.md artifact for one planning packet."
    )
    parser.add_argument("target", help="Feature slug, subfeature slug, or planning packet path.")
    parser.add_argument(
        "--scope",
        default=None,
        help="Optional planning scope path when nested scopes are ambiguous.",
    )
    parser.add_argument(
        "--question",
        required=True,
        help="Research question or decision statement for this target.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Reviewed source with optional note. Repeatable.",
    )
    parser.add_argument(
        "--chosen-reference",
        required=True,
        help="The preferred source or reference path.",
    )
    parser.add_argument(
        "--decision",
        required=True,
        help="Chosen borrowing-path decision for the target.",
    )
    parser.add_argument(
        "--alternative",
        action="append",
        default=[],
        help="Lower-priority alternative and caveat. Repeatable.",
    )
    parser.add_argument(
        "--wiki-status",
        choices=("written", "skipped", "deferred"),
        default=None,
        help="How reusable wiki follow-up was handled.",
    )
    parser.add_argument(
        "--wiki-page",
        default=None,
        help="Wiki page path when reusable synthesis was written there.",
    )
    parser.add_argument(
        "--wiki-note",
        default=None,
        help="Optional note about wiki follow-up status.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing reference-research.md file.",
    )
    return parser.parse_args()


def derive_wiki_dir_name(planning_dir: str) -> str:
    planning_path = PurePosixPath(planning_dir)
    parent = planning_path.parent
    if str(parent) in {"", "."}:
        return "wiki"
    return str(parent / "wiki")


def normalize_relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        text = str(path)
        return text[2:] if text.startswith("./") else text


def format_bullets(items: list[str], empty_line: str) -> str:
    if not items:
        return f"- {empty_line}"
    return "\n".join(f"- {item}" for item in items)


def default_wiki_status(wiki_root_exists: bool) -> str:
    return "skipped" if wiki_root_exists else "deferred"


def resolve_wiki_page_path(wiki_root: Path, wiki_page: str, repo_root: Path) -> Path:
    raw_path = Path(wiki_page)
    candidates = [raw_path] if raw_path.is_absolute() else [repo_root / raw_path, wiki_root / raw_path]

    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(wiki_root.resolve())
            return resolved
        except ValueError:
            continue

    raise RuntimeError("Requested wiki page must stay inside the derived wiki root.")


def format_title(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").strip().title() or "Research Synthesis"


def build_wiki_page_content(
    title: str,
    details: ResearchDetails,
) -> str:
    return f"""# {title}

## Summary

- Source planning target: `{details.target_path}`
- Source research artifact: `{details.research_artifact}`
- Preferred reference: `{details.chosen_reference}`

## Reusable Conclusion

{details.decision}

## Research Question

{details.question}

## Sources Reviewed

{format_bullets(details.sources, "No reviewed sources were recorded.")}

## Lower-Priority Alternatives

{format_bullets(details.alternatives, "No lower-priority alternatives were recorded.")}

## Origin

- Generated from `{details.research_artifact}` for `{details.target_id}`
"""


def upsert_wiki_index(index_path: Path, wiki_page_rel: str, summary: str) -> None:
    entry = f"- [{format_title(Path(wiki_page_rel).stem)}]({wiki_page_rel}) — {summary}"
    lines = []
    if index_path.exists():
        lines = index_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        lines = ["# Wiki Index", ""]

    updated = False
    for index, line in enumerate(lines):
        if f"]({wiki_page_rel})" in line:
            lines[index] = entry
            updated = True
            break
    if not updated:
        if lines and lines[-1] != "":
            lines.append("")
        lines.append(entry)

    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def append_wiki_log(
    log_path: Path,
    subject: str,
    wiki_page_rel: str,
    research_artifact: str,
    chosen_reference: str,
    decision: str,
) -> None:
    date = datetime.now().strftime("%Y-%m-%d")
    entry = (
        f"## [{date}] research | {subject}\n\n"
        f"- Updated `{wiki_page_rel}` from `{research_artifact}`\n"
        f"- Preferred reference: `{chosen_reference}`\n"
        f"- Decision: {decision}\n"
    )
    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8").rstrip()
        content = f"{existing}\n\n{entry}" if existing else entry
    else:
        content = f"# Wiki Log\n\n{entry}"
    log_path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_wiki_outputs(
    wiki_root: Path,
    wiki_page_path: Path,
    wiki_page_rel: str,
    title: str,
    details: ResearchDetails,
) -> None:
    wiki_page_path.parent.mkdir(parents=True, exist_ok=True)
    wiki_page_path.write_text(
        build_wiki_page_content(title=title, details=details),
        encoding="utf-8",
    )
    upsert_wiki_index(
        wiki_root / "index.md",
        wiki_page_rel,
        f"Reusable research for `{details.target_id}`: {details.decision}",
    )
    append_wiki_log(
        wiki_root / "log.md",
        details.target_id,
        wiki_page_rel,
        details.research_artifact,
        details.chosen_reference,
        details.decision,
    )


def resolve_target(planning_module, selector: str, explicit_scope: str | None):
    rows, feature, scope_context = planning_module.resolve_feature_lookup(
        selector, explicit_scope=explicit_scope
    )
    if feature is None:
        raise RuntimeError(f"Planning target not found: {selector}")
    target_dir = Path(planning_module.feature_dir_for_row(feature, scope_context=scope_context))
    metadata = planning_module.read_metadata(str(target_dir))
    target_type = "subfeature" if "/subfeatures/" in str(feature["path"]) else "feature"
    return feature, target_dir, metadata, scope_context, target_type


def build_content(
    details: ResearchDetails,
    wiki_root: str,
    wiki_root_exists: bool,
    wiki_status: str,
    wiki_page: str | None,
    wiki_note: str | None,
) -> str:
    wiki_presence = "yes" if wiki_root_exists else "no"
    wiki_status_line = f"- Status: `{wiki_status}`"
    wiki_page_line = (
        f"- Page: `{wiki_page}`" if wiki_page else "- Page: not recorded for this run"
    )
    wiki_note_line = f"- Note: {wiki_note}" if wiki_note else "- Note: none"

    return f"""# Reference Research: {details.target_id}

## Target

- Target type: `{details.target_type}`
- Target ID: `{details.target_id}`
- Planning path: `{details.target_path}`
- Planning status: `{details.planning_status}`

## Research Question

{details.question}

## Sources Reviewed

{format_bullets(details.sources, "No reviewed sources were recorded.")}

## Chosen Borrowing Path

- Preferred reference: `{details.chosen_reference}`
- Decision: {details.decision}

## Lower-Priority Alternatives

{format_bullets(details.alternatives, "No lower-priority alternatives were recorded.")}

## Wiki Follow-up

- Derived wiki root: `{wiki_root}`
- Wiki root present: {wiki_presence}
{wiki_status_line}
{wiki_page_line}
{wiki_note_line}
"""


def write_reference_research(
    output_path: Path,
    content: str,
    force: bool,
) -> None:
    if output_path.exists() and not force:
        raise RuntimeError(
            f"Reference research already exists at '{output_path}'. Use --force to overwrite it."
        )
    output_path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    planning_module = load_module(GUIDE_PLANNING_SCRIPT, "manage_planning")

    try:
        if not args.source:
            raise RuntimeError("At least one --source entry is required.")

        feature, target_dir, metadata, scope_context, target_type = resolve_target(
            planning_module, args.target, args.scope
        )
        config = planning_module.load_config(required=False, scope_context=scope_context)
        wiki_rel = derive_wiki_dir_name(str(config["planning_dir"]))
        wiki_root = Path(scope_context.scope_root) / wiki_rel
        wiki_root_exists = wiki_root.exists()
        repo_root = Path(scope_context.repo_root)

        wiki_status = args.wiki_status or default_wiki_status(wiki_root_exists)
        if wiki_status == "written" and not wiki_root_exists:
            raise RuntimeError(
                "Cannot record wiki status 'written' because the derived wiki root does not exist."
            )
        if wiki_status == "written" and not args.wiki_page:
            raise RuntimeError("--wiki-page is required when --wiki-status written is used.")
        if wiki_status != "written" and args.wiki_page:
            raise RuntimeError("--wiki-page is only valid when --wiki-status written is used.")

        wiki_page_path = None
        wiki_page_rel = None
        if wiki_status == "written":
            wiki_page_path = resolve_wiki_page_path(wiki_root, args.wiki_page, repo_root)
            wiki_page_rel = normalize_relpath(wiki_page_path, repo_root)

        output_path = target_dir / OUTPUT_FILE
        research_artifact_rel = normalize_relpath(output_path, repo_root)
        details = ResearchDetails(
            target_id=str(feature["feature"]),
            target_type=target_type,
            target_path=normalize_relpath(target_dir, repo_root),
            planning_status=str(metadata["status"]),
            question=args.question,
            sources=list(args.source),
            chosen_reference=args.chosen_reference,
            decision=args.decision,
            alternatives=list(args.alternative),
            research_artifact=research_artifact_rel,
        )
        content = build_content(
            details=details,
            wiki_root=normalize_relpath(wiki_root, repo_root),
            wiki_root_exists=wiki_root_exists,
            wiki_status=wiki_status,
            wiki_page=wiki_page_rel,
            wiki_note=args.wiki_note,
        )
        write_reference_research(output_path, content, force=args.force)
        if wiki_status == "written" and wiki_page_path is not None and wiki_page_rel is not None:
            write_wiki_outputs(
                wiki_root=wiki_root,
                wiki_page_path=wiki_page_path,
                wiki_page_rel=wiki_page_rel,
                title=format_title(wiki_page_path.stem),
                details=details,
            )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(
        f"Wrote {OUTPUT_FILE} for {target_type} '{feature['feature']}' at "
        f"'{normalize_relpath(output_path, repo_root)}'."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
