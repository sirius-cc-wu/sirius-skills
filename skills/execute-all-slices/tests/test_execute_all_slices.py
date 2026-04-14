import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "execute_all_slices.py"
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
    monkeypatch.setattr(sys, "argv", ["execute_all_slices.py", *args])
    return module.main()


def write_scope_config(root: Path, filename: str, payload: dict):
    skills_dir = root / ".skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / filename).write_text(json.dumps(payload) + "\n", encoding="utf-8")


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def setup_repo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    planning = load_module(PLANNING_SCRIPT, "manage_planning")
    subfeatures = load_module(SUBFEATURE_SCRIPT, "manage_subfeatures")
    execution = load_module(EXECUTION_SCRIPT, "manage_execution")
    execute_all_slices = load_module(SCRIPT_PATH, "execute_all_slices")

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

    return {
        "planning": planning,
        "subfeatures": subfeatures,
        "execution": execution,
        "module": execute_all_slices,
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
| EW-MSE-01 | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
| EW-MSE-02 | EW-03 | Resume backlog | Summary | area | primary | test | create slice | EW-MSE-01 | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | EW-MSE-01, EW-MSE-02 | area | EW-MSE-01 -> EW-MSE-02 |  | Notes |
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
    assert payload["ready_next"] == ["EW-MSE-01"]
    states = {entry["planned_slice_id"]: entry["state"] for entry in payload["entries"]}
    assert states["EW-MSE-01"] == "ready"
    assert states["EW-MSE-02"] == "blocked"


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
| EW-MSE-01-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| EW-MSE-02-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | EW-MSE-01-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | EW-MSE-01-scope-and-backlog-resolution | area |  | EW-MSE-01-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | EW-MSE-02-sequential-slice-orchestration | area | EW-MSE-01-scope-and-backlog-resolution |  | Notes |
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
        "EW-MSE-01-scope-and-backlog-resolution", "multi-slice-execution"
    )
    assert created
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "EW-MSE-01-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "closed", force=True
    )
    assert success, message

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["target_type"] == "subfeature"
    assert payload["ready_next"] == ["EW-MSE-02-sequential-slice-orchestration"]
    states = {entry["planned_slice_id"]: entry["state"] for entry in payload["entries"]}
    assert states["EW-MSE-01-scope-and-backlog-resolution"] == "completed"
    assert states["EW-MSE-02-sequential-slice-orchestration"] == "ready"


def test_resolve_backlog_rejects_unreviewed_targets(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    module = env["module"]

    assert run_cli(module, monkeypatch, "multi-slice-execution") == 2
    assert "must be in 'planning_reviewed' or 'slice_ready'" in capsys.readouterr().err


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
| EW-MSE-01 | EW-01 | Resolve backlog | Summary | area | primary | test | create slice |  | yes |
| EW-MSE-02 | EW-01 | Orchestrate backlog | Summary | area | primary | test | create slice | EW-MSE-01 | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | EW-MSE-01 | area |  |  | Notes |
| EW-01 | M | Summary | I2 | EW-MSE-02 | area | EW-MSE-01 |  | Notes |
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
    slice_row = execution.resolve_slice(registry_rows, "EW-MSE-01")

    assert payload["bootstrapped_slice_id"] == "EW-MSE-01"
    assert payload["next_owner"] == "guide-execution"
    assert slice_row is not None
    assert slice_row["status"] == "draft"
    traceability = (feature_path / "slice-traceability.md").read_text(encoding="utf-8")
    assert "| EW-01 | M | Summary | I1 | EW-MSE-01 | area |  | EW-MSE-01 | Notes |" in traceability


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
| EW-MSE-01-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| EW-MSE-02-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | EW-MSE-01-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | EW-MSE-01-scope-and-backlog-resolution | area |  | EW-MSE-01-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | EW-MSE-02-sequential-slice-orchestration | area | EW-MSE-01-scope-and-backlog-resolution |  | Notes |
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
        "EW-MSE-01-scope-and-backlog-resolution", "Resolve scope"
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
| EW-MSE-01-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| EW-MSE-02-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | EW-MSE-01-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | EW-MSE-01-scope-and-backlog-resolution | area |  | EW-MSE-01-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | EW-MSE-02-sequential-slice-orchestration | area | EW-MSE-01-scope-and-backlog-resolution |  | Notes |
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
        "EW-MSE-01-scope-and-backlog-resolution", "Resolve scope"
    )
    assert created

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "resume_active_slice"
    assert payload["bootstrapped_slice_id"] == "EW-MSE-01-scope-and-backlog-resolution"
    assert payload["next_owner"] == "guide-execution"
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
| EW-MSE-01-scope-and-backlog-resolution | EW-01 | Resolve scope | Summary | area | primary | test | create slice |  | yes |
| EW-MSE-02-sequential-slice-orchestration | EW-01 | Orchestrate slices | Summary | area | primary | test | create slice | EW-MSE-01-scope-and-backlog-resolution | yes |
""",
    )
    write_file(
        subfeature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I1 | EW-MSE-01-scope-and-backlog-resolution | area |  | EW-MSE-01-scope-and-backlog-resolution | Notes |
| EW-01 | M | Summary | I2 | EW-MSE-02-sequential-slice-orchestration | area | EW-MSE-01-scope-and-backlog-resolution |  | Notes |
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
        "EW-MSE-01-scope-and-backlog-resolution", "Resolve scope"
    )
    assert created
    execution_rows = execution.parse_registry()
    slice_row = execution.resolve_slice(
        execution_rows, "EW-MSE-01-scope-and-backlog-resolution"
    )
    assert slice_row is not None
    success, message = execution.update_slice_status(
        execution_rows, slice_row, "closed", force=True
    )
    assert success, message

    assert run_cli(module, monkeypatch, "multi-slice-execution", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "bootstrap_next_slice"
    assert payload["bootstrapped_slice_id"] == "EW-MSE-02-sequential-slice-orchestration"
    assert payload["next_owner"] == "guide-execution"


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
| EW-MSE-02 | EW-01 | Orchestrate backlog | Summary | area | primary | test | create slice | EW-MSE-01 | yes |
""",
    )
    write_file(
        feature_path / "slice-traceability.md",
        """# Slice Traceability

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01 | M | Summary | I2 | EW-MSE-02 | area | EW-MSE-01 |  | Notes |
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
