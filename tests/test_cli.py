from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sirius_skills import cli


def test_discover_commands_lists_runnable_scripts_only() -> None:
    commands = cli.discover_commands()

    assert (
        commands["analyze-impact"].module_name
        == "sirius_skills.commands.analyze_impact"
    )
    assert (
        commands["archive-artifacts"].module_name
        == "sirius_skills.commands.archive_artifacts"
    )
    assert (
        commands["audit-artifacts"].module_name
        == "sirius_skills.commands.audit_artifacts"
    )
    assert commands["autoplan"].module_name == "sirius_skills.commands.autoplan"
    assert commands["bootstrap"].module_name == "sirius_skills.commands.bootstrap"
    assert (
        commands["bootstrap-slice"].module_name
        == "sirius_skills.commands.bootstrap_slice"
    )
    assert commands["close-slice"].module_name == "sirius_skills.commands.close_slice"
    assert commands["learn"].module_name == "sirius_skills.commands.learn"
    assert (
        commands["manage-execution"].module_name
        == "sirius_skills.commands.manage_execution"
    )
    assert (
        commands["manage-planning"].module_name
        == "sirius_skills.commands.manage_planning"
    )
    assert (
        commands["manage-proposals"].module_name
        == "sirius_skills.commands.manage_proposals"
    )
    assert (
        commands["manage-subfeatures"].module_name
        == "sirius_skills.commands.manage_subfeatures"
    )
    assert (
        commands["measure-artifacts"].module_name
        == "sirius_skills.commands.measure_artifacts"
    )
    assert (
        commands["migrate-subfeatures"].module_name
        == "sirius_skills.commands.migrate_subfeatures"
    )
    assert (
        commands["record-review"].module_name
        == "sirius_skills.commands.record_review"
    )
    assert (
        commands["repair-artifacts"].module_name
        == "sirius_skills.commands.repair_artifacts"
    )
    assert (
        commands["report-artifacts"].module_name
        == "sirius_skills.commands.report_artifacts"
    )
    assert commands["research"].module_name == "sirius_skills.commands.research"
    assert (
        commands["scaffold-breakdown"].module_name
        == "sirius_skills.commands.scaffold_breakdown"
    )
    assert (
        commands["scaffold-design"].module_name
        == "sirius_skills.commands.scaffold_design"
    )
    assert (
        commands["trace-artifacts"].module_name
        == "sirius_skills.commands.trace_artifacts"
    )
    assert commands["ship"].module_name == "sirius_skills.commands.ship"
    assert commands["ship-slice"].module_name == "sirius_skills.commands.ship_slice"
    assert (
        commands["ship-worktree"].module_name
        == "sirius_skills.commands.ship_worktree"
    )
    assert "sync-shared-runtime" in commands
    assert "validate-workflow-state" in commands
    assert "artifact-inventory" not in commands
    assert "metrics-store" not in commands


def test_help_lists_commands(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--help"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "Available commands:" in captured.out
    assert "autoplan" in captured.out
    assert "manage-planning" in captured.out


def test_run_command_passes_arguments_and_restores_argv(tmp_path: Path) -> None:
    script_path = tmp_path / "sample_command.py"
    script_path.write_text(
        "\n".join(
            [
                "import sys",
                "def main(argv):",
                "    assert argv == ['--flag', 'value']",
                "    assert sys.argv == [__file__, '--flag', 'value']",
                "    return 7",
            ]
        ),
        encoding="utf-8",
    )
    old_argv = list(sys.argv)

    result = cli.run_command(
        cli.CommandSpec(
            name="sample-command",
            script_path=script_path,
            description=str(script_path),
            repo_root=REPO_ROOT,
        ),
        ["--flag", "value"],
    )

    assert result == 7
    assert sys.argv == old_argv


def test_main_preserves_command_separator(monkeypatch) -> None:
    seen_args = None

    def fake_run_command(spec: cli.CommandSpec, script_args: list[str]) -> int:
        nonlocal seen_args
        seen_args = script_args
        return 0

    monkeypatch.setattr(cli, "run_command", fake_run_command)

    result = cli.main(["validate-workflow-state", "--", "--collect-only"])

    assert result == 0
    assert seen_args == ["--", "--collect-only"]
