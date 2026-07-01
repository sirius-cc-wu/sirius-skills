# justfile for sirius-skills

set shell := ["bash", "-c"]

repo_root := justfile_directory()
common_flags := "--global --yes --agent github-copilot --agent codex --agent antigravity --agent antigravity-cli"

managed_skills := "autoplan audit-artifacts measure-artifacts trace-artifacts report-artifacts repair-artifacts archive-artifacts brief breakdown create-pr close-slice commit bootstrap design discover add-subfeature migrate-subfeatures migrate-slices assess guide-scope guide-planning propose blueprint reconcile-execution review-execution review-planning simplify guide-execution learn ship ship-worktree ship-slice slice ui-flow governance-update research"

# Install the python package, sync references, and add skills
install: install-python-package sync-shared-references
	#!/usr/bin/env bash
	skill_flags=$(python3 -c 'print(" ".join(f"--skill {s}" for s in "{{managed_skills}}".split()))')
	npx skills add "{{repo_root}}" {{common_flags}} $skill_flags

# Alias for install
install-packaged: install

# Install the python package in editable mode
install-python-package:
	python3 -m pip install -e .

# Sync shared references
sync-shared-references:
	sirius sync-shared-references

# Validate workflow state
validate-workflow-state:
	sirius validate-workflow-state

# Uninstall all skills and the python package
uninstall: uninstall-packaged

# Uninstall the python package and remove registered skills
uninstall-packaged: uninstall-python-package
	#!/usr/bin/env bash
	installed=$(npx skills ls -g --json | python3 -c 'import json, sys; managed = set("{{managed_skills}}".split()); installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))')
	if [ -n "$installed" ]; then
		printf '%s\n' "$installed" | xargs npx skills remove {{common_flags}}
	else
		echo "No managed skills installed."
	fi

# Uninstall the python package
uninstall-python-package:
	python3 -m pip uninstall -y sirius-skills
