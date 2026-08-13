from __future__ import annotations

from pathlib import Path

from sirius_skills.commands import sync_shared_references


def test_sync_updates_only_supported_skill_consumers(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / sync_shared_references.REFERENCE_RELATIVE_PATH
    source.parent.mkdir(parents=True)
    source.write_text("# Shared reference\n", encoding="utf-8")
    monkeypatch.setattr(sync_shared_references, "package_root", lambda: tmp_path)

    assert sync_shared_references.main([]) == 0

    expected_targets = {
        tmp_path / "skills/simplify/references/config-surface-governance.md"
    }
    assert {path for path in tmp_path.rglob("config-surface-governance.md")} == {
        source,
        *expected_targets,
    }
    assert all(path.read_text(encoding="utf-8") == "# Shared reference\n" for path in expected_targets)
