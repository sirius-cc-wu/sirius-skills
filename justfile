# justfile for sirius-skills

set shell := ["bash", "-c"]

repo_root := justfile_directory()
common_flags := "--global --yes --agent github-copilot --agent codex --agent antigravity --agent antigravity-cli"

managed_skills := "simplify create-pr commit governance-update"

# Sync references and add the managed skills
install: sync-shared-references
	#!/usr/bin/env bash
	skill_flags=$(python3 -c 'print(" ".join(f"--skill {s}" for s in "{{managed_skills}}".split()))')
	npx skills add "{{repo_root}}" {{common_flags}} $skill_flags

# Alias for install
install-packaged: install

# Sync shared references
sync-shared-references:
	env PYTHONPATH="{{repo_root}}/src" python3 -c 'from sirius_skills.commands.sync_shared_references import main; raise SystemExit(main([]))'

# Uninstall all managed skills
uninstall: uninstall-packaged

# Remove registered managed skills
uninstall-packaged:
	#!/usr/bin/env bash
	installed=$(npx skills ls -g --json | python3 -c 'import json, sys; managed = set("{{managed_skills}}".split()); installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))')
	if [ -n "$installed" ]; then
		printf '%s\n' "$installed" | xargs npx skills remove {{common_flags}}
	else
		echo "No managed skills installed."
	fi
