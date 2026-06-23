import importlib.util
import json
import sys
from pathlib import Path


RESEARCH_SCRIPT = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "research.py"
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_planning.py"
)
SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_subfeatures.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(module, script_name: str, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", [script_name, *args])
    return module.main()


def write_planning_config(scope_root: Path, config: dict | None = None):
    skills_dir = scope_root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "planning.json").write_text(
        json.dumps(
            config
            if config is not None
            else {
                "planning_dir": "docs/features",
                "proposal_dir": "docs/proposals",
                "design_diagram_mode": "embedded",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def setup_feature(tmp_path: Path, monkeypatch, planning_dir: str = "docs/features"):
    planning_module = load_module(PLANNING_SCRIPT, "manage_planning")
    monkeypatch.chdir(tmp_path)
    write_planning_config(
        tmp_path,
        {
            "planning_dir": planning_dir,
            "proposal_dir": "docs/proposals",
            "design_diagram_mode": "embedded",
        },
    )
    feature_dir = tmp_path / Path(planning_dir) / "planning-workflow"
    feature_dir.mkdir(parents=True, exist_ok=True)
    planning_module.write_metadata(
        str(feature_dir), planning_module.build_metadata("planning-workflow")
    )
    planning_module.sync_registry()
    return feature_dir


def add_subfeature(tmp_path: Path, monkeypatch):
    subfeature_module = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "init-feature",
        "planning-workflow",
    ) == 0
    assert run_cli(
        subfeature_module,
        "manage_subfeatures.py",
        monkeypatch,
        "add",
        "planning-workflow",
        "reference-research-synthesis",
        "--type",
        "additive",
        "--summary",
        "Add durable reference research synthesis.",
    ) == 0


def test_research_writes_feature_local_artifact(tmp_path, monkeypatch):
    module = load_module(RESEARCH_SCRIPT, "research")
    feature_dir = setup_feature(tmp_path, monkeypatch)

    assert (
        run_cli(
            module,
            "research.py",
            monkeypatch,
            "planning-workflow",
            "--question",
            "Which upstream pattern should own durable reference synthesis?",
            "--source",
            "references/OpenHarness/: explicit workflow owner",
            "--source",
            "references/build-your-own-openclaw/: tutorial baseline",
            "--chosen-reference",
            "references/OpenHarness/",
            "--decision",
            "Use an explicit skill plus local artifact contract.",
            "--alternative",
            "references/build-your-own-openclaw/: useful context but not the primary owner",
        )
        == 0
    )

    artifact = (feature_dir / "reference-research.md").read_text(encoding="utf-8")
    assert "Target type: `feature`" in artifact
    assert "references/OpenHarness/" in artifact
    assert "Status: `deferred`" in artifact
    assert "Derived wiki root: `docs/wiki`" in artifact


def test_research_writes_subfeature_artifact_and_honors_written_wiki(tmp_path, monkeypatch):
    module = load_module(RESEARCH_SCRIPT, "research")
    feature_dir = setup_feature(tmp_path, monkeypatch, planning_dir="planning/features")
    add_subfeature(tmp_path, monkeypatch)
    wiki_root = tmp_path / "planning" / "wiki"
    wiki_root.mkdir(parents=True)

    assert (
        run_cli(
            module,
            "research.py",
            monkeypatch,
            "reference-research-synthesis",
            "--question",
            "How should subfeatures persist durable reference decisions?",
            "--source",
            "references/OpenHarness/: reusable workflow shape",
            "--chosen-reference",
            "references/OpenHarness/",
            "--decision",
            "Write reference-research.md into the subfeature folder.",
            "--wiki-status",
            "written",
            "--wiki-page",
            "concepts/reference-research-patterns.md",
        )
        == 0
    )

    artifact = (
        feature_dir
        / "subfeatures"
        / "reference-research-synthesis"
        / "reference-research.md"
    ).read_text(encoding="utf-8")
    assert "Target type: `subfeature`" in artifact
    assert "Planning path: `planning/features/planning-workflow/subfeatures/reference-research-synthesis`" in artifact
    assert "Derived wiki root: `planning/wiki`" in artifact
    assert "Status: `written`" in artifact
    assert "Page: `planning/wiki/concepts/reference-research-patterns.md`" in artifact

    wiki_page = (wiki_root / "concepts" / "reference-research-patterns.md").read_text(
        encoding="utf-8"
    )
    assert "# Reference Research Patterns" in wiki_page
    assert "Write reference-research.md into the subfeature folder." in wiki_page
    assert (
        "`planning/features/planning-workflow/subfeatures/reference-research-synthesis/reference-research.md`"
        in wiki_page
    )

    wiki_index = (wiki_root / "index.md").read_text(encoding="utf-8")
    assert "[Reference Research Patterns](planning/wiki/concepts/reference-research-patterns.md)" in wiki_index

    wiki_log = (wiki_root / "log.md").read_text(encoding="utf-8")
    assert "# Wiki Log" in wiki_log
    assert "research | reference-research-synthesis" in wiki_log
    assert "planning/wiki/concepts/reference-research-patterns.md" in wiki_log


def test_research_updates_wiki_page_and_appends_log(tmp_path, monkeypatch):
    module = load_module(RESEARCH_SCRIPT, "research")
    setup_feature(tmp_path, monkeypatch, planning_dir="planning/features")
    wiki_root = tmp_path / "planning" / "wiki"
    wiki_root.mkdir(parents=True)

    assert (
        run_cli(
            module,
            "research.py",
            monkeypatch,
            "planning-workflow",
            "--question",
            "Which reusable workflow pattern should be documented?",
            "--source",
            "references/OpenHarness/: explicit workflow owner",
            "--chosen-reference",
            "references/OpenHarness/",
            "--decision",
            "Capture the initial reusable workflow conclusion.",
            "--wiki-status",
            "written",
            "--wiki-page",
            "concepts/workflow-patterns.md",
        )
        == 0
    )
    assert (
        run_cli(
            module,
            "research.py",
            monkeypatch,
            "planning-workflow",
            "--question",
            "Which reusable workflow pattern should be documented?",
            "--source",
            "references/OpenHarness/: explicit workflow owner",
            "--chosen-reference",
            "references/OpenHarness/",
            "--decision",
            "Capture the updated reusable workflow conclusion.",
            "--wiki-status",
            "written",
            "--wiki-page",
            "concepts/workflow-patterns.md",
            "--force",
        )
        == 0
    )

    wiki_page = (wiki_root / "concepts" / "workflow-patterns.md").read_text(encoding="utf-8")
    assert "Capture the updated reusable workflow conclusion." in wiki_page
    assert "Capture the initial reusable workflow conclusion." not in wiki_page

    wiki_log = (wiki_root / "log.md").read_text(encoding="utf-8")
    assert wiki_log.count("## [") == 2


def test_research_refuses_written_wiki_without_wiki_root(tmp_path, monkeypatch, capsys):
    module = load_module(RESEARCH_SCRIPT, "research")
    setup_feature(tmp_path, monkeypatch)

    assert (
        run_cli(
            module,
            "research.py",
            monkeypatch,
            "planning-workflow",
            "--question",
            "Which reference should be preferred?",
            "--source",
            "references/OpenHarness/: explicit owner",
            "--chosen-reference",
            "references/OpenHarness/",
            "--decision",
            "Prefer OpenHarness.",
            "--wiki-status",
            "written",
            "--wiki-page",
            "docs/wiki/concepts/reference-research-patterns.md",
        )
        == 2
    )

    captured = capsys.readouterr()
    assert "derived wiki root does not exist" in captured.err
