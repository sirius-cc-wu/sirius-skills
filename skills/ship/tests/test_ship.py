import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ship.py"
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[2] / "guide-planning" / "scripts" / "manage_planning.py"
)
SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[2] / "add-subfeature" / "scripts" / "manage_subfeatures.py"
)
EXECUTION_SCRIPT = (
    Path(__file__).resolve().parents[2] / "guide-execution" / "scripts" / "manage_execution.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["ship.py", *args])
    return module.main()


def write_scope_config(root: Path, filename: str, payload: dict):
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(payload) + "\n", encoding="utf-8")


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_git_repo(root: Path):
    subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Copilot Test"],
        cwd=root,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "copilot@example.test"],
        cwd=root,
        check=True,
    )


def git_commit_all(root: Path, message: str):
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", message], cwd=root, check=True)


def setup_repo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)
    planning = load_module(PLANNING_SCRIPT, "manage_planning")
    subfeatures = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
    execution = load_module(EXECUTION_SCRIPT, "manage_execution")
    ship_module = load_module(SCRIPT_PATH, "ship")

    write_scope_config(
        tmp_path,
        "planning.json",
        {"planning_dir": "docs/features", "proposal_dir": "docs/proposals"},
    )
    write_scope_config(
        tmp_path,
        "execution.json",
        {
            "slice_dir": "slices",
            "preferred_workflow": "TDD",
            "auto_start_implementation": True,
        },
    )

    feature_dir, _ = planning.create_feature("execution-workflow")
    feature_path = Path(feature_dir)
    write_file(feature_path / "discover.md", "# Discover\n")
    write_file(feature_path / "system-design.md", "# Design\n")
    write_file(feature_path / "user-stories.md", "# Stories\n")

    subfeatures.ensure_subfeature_registry(feature_dir)
    scope_context = planning.SCOPE_RUNTIME.resolve_scope_context()
    subfeature_dir, _ = subfeatures.create_subfeature(
        planning,
        feature_dir,
        "execution-workflow",
        "multi-slice-execution",
        "additive",
        "Execute all planned slices for a feature or subfeature in dependency order, committing each completed slice separately.",
        scope_context,
    )

    subfeature_path = Path(subfeature_dir)
    write_file(subfeature_path / "discover.md", "# Discover\n")
    write_file(subfeature_path / "impact-analysis.md", "# Impact\n")
    write_file(subfeature_path / "system-design.md", "# Design\n")
    git_commit_all(tmp_path, "fixture: initialize repo")

    return {
        "planning": planning,
        "subfeatures": subfeatures,
        "execution": execution,
        "module": ship_module,
        "feature_path": feature_path,
        "subfeature_path": subfeature_path,
    }


def test_resolve_feature_scope_returns_first_ready_planned_slice(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-03 | Resume backlog | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution, mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution -> mse-sequential-slice-orchestration |  | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["target_type"] == "feature"
    assert payload["ready_next"] == ["mse-scope-and-backlog-resolution"]
    assert payload["readiness"]["can_proceed"] is True
    assert payload["readiness"]["next_owner"] == "brief"
    assert payload["readiness"]["blocked_by"] == []
    states = {entry["planned_slice_id"]: entry["state"] for entry in payload["entries"]}
    assert states["mse-scope-and-backlog-resolution"] == "ready"
    assert states["mse-sequential-slice-orchestration"] == "blocked"


def test_runtime_foundation_ready_slice_is_reported(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Runtime foundation | TAW-03 | taw-runtime-foundation | test | Notes |

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| taw-runtime-foundation | TAW-03 | Add runtime support | Summary | area | primary | test | create slice |  | yes |
| taw-learn-skill | TAW-04 | Add learn skill | Summary | area | primary | test | create slice | taw-runtime-foundation | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TAW-03 | L | Runtime support | I1 | taw-runtime-foundation | area |  |  | Notes |
| TAW-04 | M | Learn skill | I1 | taw-learn-skill | area | taw-runtime-foundation |  | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["current_increment"] == "I1"
    assert payload["ready_next"] == ["taw-runtime-foundation"]


def test_resolve_backlog_defers_ready_slice_in_later_increment_until_earlier_increment_completes(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | First increment | EW-01 | mse-scope-and-backlog-resolution | test | Notes |
| I2 | Second increment | EW-02 | mse-sequential-slice-orchestration | test | Notes |

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-02 | Orchestrate backlog | Summary | area | primary | test | create slice |  | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  |  | Notes |
| EW-02 | M | Summary | I2 | mse-sequential-slice-orchestration | area |  |  | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["increment_order"] == ["I1", "I2"]
    assert payload["current_increment"] == "I1"
    assert payload["ready_next"] == ["mse-scope-and-backlog-resolution"]
    states = {entry["planned_slice_id"]: entry["state"] for entry in payload["entries"]}
    assert states["mse-scope-and-backlog-resolution"] == "ready"
    assert states["mse-sequential-slice-orchestration"] == "deferred"


def test_resolve_subfeature_scope_uses_closed_execution_slice_lineage(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    subfeatures = env["subfeatures"]
    feature_path = env["feature_path"]
    subfeature_path = env["subfeature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        subfeature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = subfeatures.load_registry(str(feature_path))
    subfeature = subfeatures.find_subfeature(rows, "multi-slice-execution")
    assert subfeature is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        subfeature,
        "reviewed",
        env["planning"].SCOPE_RUNTIME.resolve_scope_context(),
        force=True,
        review_note="ready",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-01"],
    )
    assert success, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "multi-slice-execution"
    )
    assert created
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "mse-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "closed", force=True
    )
    assert success, message

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["target_type"] == "subfeature"
    assert payload["ready_next"] == ["mse-sequential-slice-orchestration"]
    states = {entry["planned_slice_id"]: entry["state"] for entry in payload["entries"]}
    assert states["mse-scope-and-backlog-resolution"] == "completed"
    assert states["mse-sequential-slice-orchestration"] == "ready"


def test_resolve_subfeature_scope_allows_finalized_sibling_subfeature_dependency(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    subfeatures = env["subfeatures"]
    feature_path = env["feature_path"]
    subfeature_path = env["subfeature_path"]
    module = env["module"]

    scope_context = env["planning"].SCOPE_RUNTIME.resolve_scope_context()
    sibling_dir, created = subfeatures.create_subfeature(
        env["planning"],
        str(feature_path),
        "execution-workflow",
        "environment-injection",
        "additive",
        "Provide an already-finalized sibling prerequisite.",
        scope_context,
    )
    assert created

    write_file(Path(sibling_dir) / "discover.md", "# Discover\n")
    write_file(Path(sibling_dir) / "impact-analysis.md", "# Impact\n")
    write_file(Path(sibling_dir) / "system-design.md", "# Design\n")
    write_file(Path(sibling_dir) / "slice-planning.md", "# Slice Planning\n")
    write_file(Path(sibling_dir) / "slice-traceability.md", "# Slice Traceability\n")

    sibling_rows = subfeatures.load_registry(str(feature_path))
    sibling = subfeatures.find_subfeature(sibling_rows, "environment-injection")
    assert sibling is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        sibling,
        "finalized",
        scope_context,
        force=True,
        review_note="done",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-00"],
        affected_slice_ids=["EW-ENV-01"],
    )
    assert success, message

    write_file(
        subfeature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice | environment-injection finalized | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area | environment-injection finalized |  | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = subfeatures.load_registry(str(feature_path))
    target_subfeature = subfeatures.find_subfeature(rows, "multi-slice-execution")
    assert target_subfeature is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        target_subfeature,
        "reviewed",
        scope_context,
        force=True,
        review_note="ready",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-01"],
    )
    assert success, message

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["ready_next"] == ["mse-scope-and-backlog-resolution"]
    states = {entry["planned_slice_id"]: entry["state"] for entry in payload["entries"]}
    assert states["mse-scope-and-backlog-resolution"] == "ready"
    assert states["mse-sequential-slice-orchestration"] == "blocked"


def test_resolve_backlog_rejects_unreviewed_targets(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    module = env["module"]

    assert run_cli(module, monkeypatch, "multi-slice-execution") == 2
    assert (
        "must be in 'planning_reviewed', 'slice_ready', or 'implemented'"
        in capsys.readouterr().err
    )


def test_bootstrap_next_creates_first_ready_slice_and_updates_traceability(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate backlog | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  |  | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--bootstrap-next", "--json") == 0
    payload = json.loads(capsys.readouterr().out)
    registry_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(registry_rows, "mse-scope-and-backlog-resolution")

    assert payload["bootstrapped_slice_id"] == "mse-scope-and-backlog-resolution"
    assert payload["next_owner"] == "brief"
    assert payload["active_slice_handoff"]["next_owner"] == "brief"
    assert payload["active_slice_handoff"]["next_action"] == "create_or_update_brief"
    assert payload["active_slice_handoff"]["validation_hint"] == "test"
    assert slice_row is not None
    assert slice_row["status"] == "draft"
    traceability = (feature_path / "slice-traceability.md").read_text(encoding="utf-8")
    assert "| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |" in traceability


def test_bootstrap_next_refuses_when_mapped_execution_slice_is_active(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    subfeatures = env["subfeatures"]
    feature_path = env["feature_path"]
    subfeature_path = env["subfeature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        subfeature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = subfeatures.load_registry(str(feature_path))
    subfeature = subfeatures.find_subfeature(rows, "multi-slice-execution")
    assert subfeature is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        subfeature,
        "reviewed",
        env["planning"].SCOPE_RUNTIME.resolve_scope_context(),
        force=True,
        review_note="ready",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-01"],
    )
    assert success, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve scope"
    )
    assert created

    assert (
        run_cli(module, monkeypatch, "multi-slice-execution", "--bootstrap-next") == 2
    )
    assert "another mapped execution slice is still active" in capsys.readouterr().err


def test_resume_returns_active_mapped_slice_and_next_owner(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    subfeatures = env["subfeatures"]
    feature_path = env["feature_path"]
    subfeature_path = env["subfeature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        subfeature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = subfeatures.load_registry(str(feature_path))
    subfeature = subfeatures.find_subfeature(rows, "multi-slice-execution")
    assert subfeature is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        subfeature,
        "reviewed",
        env["planning"].SCOPE_RUNTIME.resolve_scope_context(),
        force=True,
        review_note="ready",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-01"],
    )
    assert success, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve scope"
    )
    assert created

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "resume_active_slice"
    assert payload["bootstrapped_slice_id"] == "mse-scope-and-backlog-resolution"
    assert payload["next_owner"] == "brief"
    assert payload["readiness"]["can_proceed"] is True
    assert payload["readiness"]["blocked_by"] == []
    assert payload["active_slice_handoff"]["next_owner"] == "brief"
    assert payload["active_slice_handoff"]["downstream_owners"] == [
        "blueprint",
        "implementation",
        "review-execution",
        "close-slice",
        "commit",
    ]
    assert payload["slice_status"] == "draft"


def test_resume_bootstraps_next_ready_slice_after_completed_predecessor(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    subfeatures = env["subfeatures"]
    feature_path = env["feature_path"]
    subfeature_path = env["subfeature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        subfeature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = subfeatures.load_registry(str(feature_path))
    subfeature = subfeatures.find_subfeature(rows, "multi-slice-execution")
    assert subfeature is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        subfeature,
        "reviewed",
        env["planning"].SCOPE_RUNTIME.resolve_scope_context(),
        force=True,
        review_note="ready",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-01"],
    )
    assert success, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve scope"
    )
    assert created
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "mse-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "closed", force=True
    )
    assert success, message
    git_commit_all(tmp_path, "fixture: close first slice")

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "bootstrap_next_slice"
    assert payload["bootstrapped_slice_id"] == "mse-sequential-slice-orchestration"
    assert payload["next_owner"] == "brief"


def test_resume_routes_brief_ready_slice_to_blueprint_and_emits_handoff_payload(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | pytest -q tests/test_demo.py | create slice |  | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve backlog"
    )
    assert created
    slice_dir = tmp_path / "slices" / "mse-scope-and-backlog-resolution-resolve-backlog"
    write_file(slice_dir / "brief.md", "# brief\n")
    write_file(slice_dir / "checklists" / "requirements.md", "- [x] requirements complete\n")
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "mse-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "brief_ready"
    )
    assert success, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["next_owner"] == "blueprint"
    assert payload["active_slice_handoff"]["next_owner"] == "blueprint"
    assert payload["active_slice_handoff"]["next_action"] == "create_or_update_blueprint"
    assert payload["active_slice_handoff"]["validation_hint"] == "pytest -q tests/test_demo.py"
    assert payload["handoff_payload"] == {
        "action": "resume_active_slice",
        "execution_slice_id": "mse-scope-and-backlog-resolution",
        "execution_slice_path": "slices/mse-scope-and-backlog-resolution-resolve-backlog/",
        "next_owner": "blueprint",
        "planned_slice_id": "mse-scope-and-backlog-resolution",
        "slice_status": "brief_ready",
        "target_id": "execution-workflow",
        "target_type": "feature",
    }


def test_resume_routes_execution_ready_slice_to_implementation_with_handoff_payload(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | pytest -q tests/test_demo.py | create slice |  | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve backlog"
    )
    assert created
    slice_dir = tmp_path / "slices" / "mse-scope-and-backlog-resolution-resolve-backlog"
    write_file(slice_dir / "brief.md", "# brief\n")
    write_file(slice_dir / "checklists" / "requirements.md", "- [x] requirements complete\n")
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "mse-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "brief_ready"
    )
    assert success, message
    write_file(slice_dir / "blueprint.md", "# plan\n")
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "mse-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "blueprint_ready"
    )
    assert success, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["slice_status"] == "execution_ready"
    assert payload["next_owner"] == "implementation"
    assert payload["readiness"]["can_proceed"] is True
    assert payload["readiness"]["blocked_by"] == []
    assert payload["active_slice_handoff"]["next_owner"] == "implementation"
    assert payload["active_slice_handoff"]["downstream_owners"] == [
        "review-execution",
        "close-slice",
        "commit",
    ]
    assert payload["handoff_payload"]["next_owner"] == "implementation"
    assert payload["handoff_payload"]["slice_status"] == "execution_ready"
    assert payload["active_slice_handoff"]["handoff_payload"] == payload["handoff_payload"]


def test_resolve_backlog_reports_completed_and_current_increments_in_text_output(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    subfeatures = env["subfeatures"]
    feature_path = env["feature_path"]
    subfeature_path = env["subfeature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        subfeature_path / "slice-planning.md",
        """# Slice Planning

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | First increment | EW-01 | mse-scope-and-backlog-resolution | test | Notes |
| I2 | Second increment | EW-01 | mse-sequential-slice-orchestration | test | Notes |

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = subfeatures.load_registry(str(feature_path))
    subfeature = subfeatures.find_subfeature(rows, "multi-slice-execution")
    assert subfeature is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        subfeature,
        "reviewed",
        env["planning"].SCOPE_RUNTIME.resolve_scope_context(),
        force=True,
        review_note="ready",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-01"],
    )
    assert success, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve scope"
    )
    assert created
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "mse-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "closed", force=True
    )
    assert success, message

    assert run_cli(module, monkeypatch, "multi-slice-execution") == 0
    output = capsys.readouterr().out

    assert "Current increment: I2" in output
    assert "Completed increments: I1" in output
    assert "- mse-sequential-slice-orchestration [increments: I2]: ready" in output


def test_resume_rejects_blocked_unfinished_backlog_without_ready_slice(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate backlog | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--resume") == 2
    assert "No ready planned slice remains while unfinished slices are blocked" in capsys.readouterr().err


def test_resume_requires_commit_checkpoint_before_next_slice(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    subfeatures = env["subfeatures"]
    feature_path = env["feature_path"]
    subfeature_path = env["subfeature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        subfeature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| mse-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | mse-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | mse-sequential-slice-orchestration | area | mse-scope-and-backlog-resolution |  | Notes |
""",
    )

    rows = subfeatures.load_registry(str(feature_path))
    subfeature = subfeatures.find_subfeature(rows, "multi-slice-execution")
    assert subfeature is not None
    success, message = subfeatures.update_subfeature_status(
        env["planning"],
        str(feature_path),
        subfeature,
        "reviewed",
        env["planning"].SCOPE_RUNTIME.resolve_scope_context(),
        force=True,
        review_note="ready",
        affected_artifacts=[
            "docs/features/execution-workflow/discover.md",
            "docs/features/execution-workflow/system-design.md",
            "docs/features/execution-workflow/user-stories.md",
        ],
        affected_story_ids=["EW-01"],
    )
    assert success, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve scope"
    )
    assert created
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "mse-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "closed", force=True
    )
    assert success, message
    write_file(tmp_path / "scratch.txt", "tracked\n")
    git_commit_all(tmp_path, "fixture: close first slice")
    write_file(tmp_path / "scratch.txt", "dirty\n")

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "commit_checkpoint_required"
    assert payload["checkpoint_slice_id"] == "mse-scope-and-backlog-resolution"
    assert payload["next_owner"] == "commit"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["commit_checkpoint"]
    assert payload["readiness"]["commit_checkpoint"]["required"] is True
    assert any("scratch.txt" in entry for entry in payload["dirty_worktree_paths"])


def test_resume_delegation_routes_active_slice_through_ship_slice(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]
    execution = env["execution"]

    write_scope_config(
        tmp_path,
        "execution.json",
        {
            "slice_dir": "slices",
            "preferred_workflow": "TDD",
            "auto_start_implementation": True,
            "accelerators": {
                "ship": {"delegate_to_ship_slice": True},
            },
        },
    )
    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve backlog"
    )
    assert created

    assert run_cli(
        module, monkeypatch, "execution-workflow", "--approve", "--json"
    ) == 0
    approval_payload = json.loads(capsys.readouterr().out)
    assert approval_payload["approval_recorded"]["recorded"] is True

    assert run_cli(module, monkeypatch, "execution-workflow", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "delegated_to_ship_slice"
    assert payload["next_owner"] == "brief"
    assert payload["readiness"]["can_proceed"] is True
    assert payload["readiness"]["blocked_by"] == []
    assert payload["delegate_result"]["next_owner"] == "brief"
    assert payload["delegate_result"]["handoff_payload"]["execution_slice_id"] == (
        "mse-scope-and-backlog-resolution"
    )


def test_resume_delegation_requires_explicit_approval(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]
    execution = env["execution"]

    write_scope_config(
        tmp_path,
        "execution.json",
        {
            "slice_dir": "slices",
            "preferred_workflow": "TDD",
            "auto_start_implementation": True,
            "accelerators": {
                "ship": {"delegate_to_ship_slice": True},
            },
        },
    )
    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve backlog"
    )
    assert created

    assert run_cli(module, monkeypatch, "execution-workflow", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "approval_required"
    assert payload["next_owner"] == "approval"
    assert payload["approval_gate"]["required"] is True
    assert payload["approval_gate"]["decision"] == "waiting_approval"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_required"]
    assert payload["readiness"]["approval_gate"]["state"] == "waiting_approval"


def test_resume_delegation_invalidates_approval_when_planning_changes(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]
    execution = env["execution"]

    write_scope_config(
        tmp_path,
        "execution.json",
        {
            "slice_dir": "slices",
            "preferred_workflow": "TDD",
            "auto_start_implementation": True,
            "accelerators": {
                "ship": {"delegate_to_ship_slice": True},
            },
        },
    )
    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "planning_reviewed",
        force=True,
        review_note="ready",
    )
    assert ok, message

    _, created = execution.create_slice(
        "mse-scope-and-backlog-resolution", "Resolve backlog"
    )
    assert created

    assert run_cli(
        module, monkeypatch, "execution-workflow", "--approve", "--json"
    ) == 0
    _ = capsys.readouterr().out

    write_file(feature_path / "discover.md", "# Discover\nChanged after approval\n")

    assert run_cli(module, monkeypatch, "execution-workflow", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "approval_required"
    assert payload["next_owner"] == "approval"
    assert payload["approval_gate"]["decision"] == "invalidated"
    assert payload["approval_gate"]["reason"] == "planning_artifacts_changed"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["blocked_by"] == ["approval_required"]
    assert payload["readiness"]["approval_gate"]["state"] == "invalidated"


def test_resolve_backlog_allows_implemented_target(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    planning = env["planning"]
    feature_path = env["feature_path"]
    module = env["module"]
    execution = env["execution"]

    write_file(
        feature_path / "slice-planning.md",
        """# Slice Planning

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mse-scope-and-backlog-resolution | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  | mse-scope-and-backlog-resolution | Notes |
""",
    )

    rows = planning.parse_registry()
    feature = planning.find_feature(rows, "execution-workflow")
    assert feature is not None
    ok, message = planning.update_feature_status(
        rows,
        feature,
        "implemented",
        force=True,
        review_note="done",
    )
    assert ok, message

    _, created = execution.create_slice("mse-scope-and-backlog-resolution", "Resolve backlog")
    assert created
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(execution_rows, "mse-scope-and-backlog-resolution")
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "closed", force=True
    )
    assert success, message

    assert run_cli(module, monkeypatch, "execution-workflow", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["planning_status"] == "implemented"
    assert payload["ready_next"] == []
    assert payload["entries"][0]["state"] == "completed"
    assert payload["readiness"]["can_proceed"] is False
    assert payload["readiness"]["next_owner"] == "none"
    assert payload["readiness"]["blocked_by"] == ["completed"]
