# justfile for iterative-software-design-skills

set shell := ["bash", "-c"]

repo_root := justfile_directory()
common_flags := "--global --yes --agent github-copilot --agent codex --agent antigravity --agent antigravity-cli"

managed_skills_file := repo_root + "/skill-sets/all.txt"

# Add all managed skills
install:
	#!/usr/bin/env bash
	mapfile -t skills < <(sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "{{managed_skills_file}}")
	skill_flags=()
	for skill in "${skills[@]}"; do
		skill_flags+=(--skill "$skill")
	done
	npx skills add "{{repo_root}}" {{common_flags}} "${skill_flags[@]}"

# Remove all installed managed skills
uninstall:
	#!/usr/bin/env bash
	installed=$(npx skills ls -g --json | python3 -c 'import json, pathlib, sys; managed = {line.strip() for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")}; installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))' "{{managed_skills_file}}")
	if [ -n "$installed" ]; then
		# Do not restrict agents: universal agent aliases share ~/.agents/skills.
		printf '%s\n' "$installed" | xargs npx skills remove --global --yes
	else
		echo "No managed skills installed."
	fi

# Validate skill structure and metadata
validate:
	./scripts/validate_skills.sh
