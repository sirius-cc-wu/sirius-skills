from __future__ import annotations

import json
from importlib import metadata
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse


DEFAULT_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
INSTALLED_PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def root_has_scripts(path: Path) -> bool:
    return (path / "skills").is_dir()


def source_root_from_distribution() -> Path | None:
    try:
        distribution = metadata.distribution("sirius-skills")
        direct_url_text = distribution.read_text("direct_url.json")
    except metadata.PackageNotFoundError:
        return None
    if direct_url_text is None:
        return None

    try:
        direct_url = json.loads(direct_url_text)
    except json.JSONDecodeError:
        return None

    url = direct_url.get("url")
    if not isinstance(url, str):
        return None
    parsed = urlparse(url)
    if parsed.scheme != "file":
        return None
    source_path = Path(unquote(parsed.path))
    if source_path.is_dir():
        return source_path
    return None


def iter_candidate_roots() -> Iterable[Path]:
    yield INSTALLED_PACKAGE_ROOT
    yield DEFAULT_PACKAGE_ROOT
    distribution_root = source_root_from_distribution()
    if distribution_root is not None:
        yield distribution_root
    yield Path.cwd()


def package_root() -> Path:
    seen: set[Path] = set()
    for candidate in iter_candidate_roots():
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if root_has_scripts(resolved):
            return resolved
    return DEFAULT_PACKAGE_ROOT
