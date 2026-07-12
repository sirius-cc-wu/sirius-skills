import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "ship_worktree.py"
PLANNING_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_planning.py"
)
SUBFEATURE_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_subfeatures.py"
)
EXECUTION_SCRIPT = (
    Path(__file__).resolve().parents[3] / "src" / "sirius_skills" / "commands" / "manage_execution.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_cli(module, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["ship_worktree.py", *args])
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
    subprocess.run(["git", "config", "user.name", "Copilot Test"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "copilot@example.test"],
        cwd=root,
        check=True,
    )


def git_commit_all(root: Path, message: str):
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", message], cwd=root, check=True)


def install_treehouse_stub(module, monkeypatch, repo_root: Path, worktree_path: Path):
    original_run_command = module.run_command
    gh_state = {"created": False}

    def fake_run_command(command, *, cwd):
        if command[:3] == ["treehouse", "get", "--lease"]:
            worktree_path.parent.mkdir(parents=True, exist_ok=True)
            if not worktree_path.exists():
                subprocess.run(
                    ["git", "worktree", "add", "--detach", str(worktree_path), "HEAD"],
                    cwd=repo_root,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            return subprocess.CompletedProcess(command, 0, f"{worktree_path}\n", "")
        if command[:2] == ["treehouse", "return"]:
            if worktree_path.exists():
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(worktree_path)],
                    cwd=repo_root,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            return subprocess.CompletedProcess(command, 0, "", "")
        if command[:2] == ["git", "push"]:
            return subprocess.CompletedProcess(command, 0, "", "")
        if command[:4] == ["gh", "pr", "list", "--state"]:
            if not gh_state["created"]:
                return subprocess.CompletedProcess(command, 0, "[]\n", "")
            return subprocess.CompletedProcess(
                command,
                0,
                json.dumps(
                    [
                        {
                            "number": 42,
                            "url": "https://example.test/pr/42",
                            "state": "OPEN",
                            "title": "feature: Implement execution-workflow",
                            "isDraft": True,
                        }
                    ]
                )
                + "\n",
                "",
            )
        if command[:3] == ["gh", "pr", "create"]:
            gh_state["created"] = True
            return subprocess.CompletedProcess(
                command,
                0,
                "https://example.test/pr/42\n",
                "",
            )
        return original_run_command(command, cwd=cwd)

    monkeypatch.setattr(module, "run_command", fake_run_command)
    return gh_state


def treehouse_worktree_path(repo_root: Path) -> Path:
    return repo_root.parent / f"treehouse-worktrees-{repo_root.name}" / "execution-workflow"


def setup_repo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)

    planning = load_module(PLANNING_SCRIPT, "ship_worktree_manage_planning")
    subfeatures = load_module(SUBFEATURE_SCRIPT, "ship_worktree_manage_subfeatures")
    execution = load_module(EXECUTION_SCRIPT, "ship_worktree_manage_execution")
    module = load_module(SCRIPT_PATH, "ship_worktree")

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
        "Execute all planned slices in a dedicated worktree.",
        scope_context,
    )
    subfeature_path = Path(subfeature_dir)
    write_file(subfeature_path / "discover.md", "# Discover\n")
    write_file(subfeature_path / "system-design.md", "# Design\n")

    git_commit_all(tmp_path, "fixture: initialize repo")
    return {
        "planning": planning,
        "execution": execution,
        "module": module,
        "feature_path": feature_path,
        "subfeature_path": subfeature_path,
    }


def mark_feature_reviewed(env):
    planning = env["planning"]
    feature_path = env["feature_path"]

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
| EW-01 | M | Summary | I1 | mse-scope-and-backlog-resolution | area |  |  | Notes |
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
    git_commit_all(feature_path.parents[2], "fixture: mark feature reviewed")


def mark_feature_implemented(env):
    planning = env["planning"]
    execution = env["execution"]
    feature_path = env["feature_path"]

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
        execution_rows,
        slice_row,
        "closed",
        force=True,
    )
    assert success, message
    git_commit_all(feature_path.parents[2], "fixture: mark feature implemented")


def test_ship_worktree_creates_target_named_worktree(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    mark_feature_reviewed(env)
    module = env["module"]
    worktree_path = treehouse_worktree_path(tmp_path)
    install_treehouse_stub(module, monkeypatch, tmp_path, worktree_path)

    assert run_cli(module, monkeypatch, "execution-workflow", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "worktree_ready"
    assert payload["next_owner"] == "ship"
    assert payload["worktree_branch"] == "wt/execution-workflow"
    assert payload["worktree_created"] is True
    assert Path(payload["worktree_path"]) == worktree_path
    assert Path(payload["worktree_path"]).is_dir()
    assert Path(payload["record_path"]).is_file()


def test_ship_worktree_resume_runs_ship_inside_worktree(tmp_path, monkeypatch, capsys):
    env = setup_repo(tmp_path, monkeypatch)
    mark_feature_reviewed(env)
    module = env["module"]
    worktree_path = treehouse_worktree_path(tmp_path)
    install_treehouse_stub(module, monkeypatch, tmp_path, worktree_path)

    assert run_cli(module, monkeypatch, "execution-workflow", "--resume", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["action"] == "bootstrap_next_slice"
    assert payload["ship_result"]["action"] == "bootstrap_next_slice"
    assert payload["ship_result"]["bootstrapped_slice_id"] == "mse-scope-and-backlog-resolution"
    assert payload["next_owner"] == "blueprint"
    assert Path(payload["worktree_path"]) == worktree_path


def test_ship_worktree_create_pr_blocks_when_worktree_is_dirty(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    mark_feature_implemented(env)
    module = env["module"]
    worktree_path = treehouse_worktree_path(tmp_path)
    install_treehouse_stub(module, monkeypatch, tmp_path, worktree_path)

    assert run_cli(module, monkeypatch, "execution-workflow", "--json") == 0
    payload = json.loads(capsys.readouterr().out)
    worktree_path = Path(payload["worktree_path"])

    write_file(worktree_path / "notes.txt", "dirty\n")

    assert run_cli(module, monkeypatch, "execution-workflow", "--create-pr", "--json") == 0
    blocked = json.loads(capsys.readouterr().out)

    assert blocked["action"] == "pull_request_blocked"
    assert blocked["blocked_reason"] == "commit_checkpoint"
    assert blocked["next_owner"] == "commit"
    assert any("notes.txt" in line for line in blocked["dirty_worktree_paths"])


def test_ship_worktree_create_pr_reuses_or_creates_review_branch(
    tmp_path, monkeypatch, capsys
):
    env = setup_repo(tmp_path, monkeypatch)
    mark_feature_implemented(env)
    module = env["module"]
    worktree_path = treehouse_worktree_path(tmp_path)
    install_treehouse_stub(module, monkeypatch, tmp_path, worktree_path)

    assert run_cli(module, monkeypatch, "execution-workflow", "--json") == 0
    payload = json.loads(capsys.readouterr().out)
    worktree_path = Path(payload["worktree_path"])

    write_file(worktree_path / "implementation.txt", "done\n")
    git_commit_all(worktree_path, "feature: implement target")

    original_run_command = module.run_command
    gh_state = {"created": False}

    def fake_run_command(command, *, cwd):
        if command[:4] == ["git", "push", "-u", "origin"]:
            return subprocess.CompletedProcess(command, 0, "", "")
        if command[:4] == ["gh", "pr", "list", "--state"]:
            if not gh_state["created"]:
                return subprocess.CompletedProcess(command, 0, "[]\n", "")
            return subprocess.CompletedProcess(
                command,
                0,
                json.dumps(
                    [
                        {
                            "number": 42,
                            "url": "https://example.test/pr/42",
                            "state": "OPEN",
                            "title": "feature: Implement execution-workflow",
                            "isDraft": True,
                        }
                    ]
                )
                + "\n",
                "",
            )
        if command[:3] == ["gh", "pr", "create"]:
            gh_state["created"] = True
            return subprocess.CompletedProcess(
                command,
                0,
                "https://example.test/pr/42\n",
                "",
            )
        return original_run_command(command, cwd=cwd)

    monkeypatch.setattr(module, "run_command", fake_run_command)

    assert run_cli(module, monkeypatch, "execution-workflow", "--create-pr", "--json") == 0
    created = json.loads(capsys.readouterr().out)

    assert created["action"] == "pull_request_created"
    assert created["next_owner"] == "none"
    assert created["pull_request"]["number"] == 42
    assert created["pull_request"]["url"] == "https://example.test/pr/42"
    assert not Path(created["record_path"]).exists()
    assert not worktree_path.exists()
