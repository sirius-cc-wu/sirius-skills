# justfile for iterative-software-design-skills

set shell := ["bash", "-c"]

repo_root := justfile_directory()
common_flags := "--global --yes --agent github-copilot --agent codex --agent antigravity --agent antigravity-cli"

managed_skills := "iterative-up-analysis-design inception use-case-modeling domain-modeling system-sequence-diagrams operation-contracts grasp-responsibility-design use-case-realization uml-class-diagram-design design-pattern-application software-design-language-adaptation test-driven-implementation behavior-preserving-refactoring"

# Add all managed skills
install:
	#!/usr/bin/env bash
	skill_flags=$(python3 -c 'print(" ".join(f"--skill {s}" for s in "{{managed_skills}}".split()))')
	npx skills add "{{repo_root}}" {{common_flags}} $skill_flags

# Remove all installed managed skills
uninstall:
	#!/usr/bin/env bash
	installed=$(npx skills ls -g --json | python3 -c 'import json, sys; managed = set("{{managed_skills}}".split()); installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))')
	if [ -n "$installed" ]; then
		# Do not restrict agents: universal agent aliases share ~/.agents/skills.
		printf '%s\n' "$installed" | xargs npx skills remove --global --yes
	else
		echo "No managed skills installed."
	fi

# Validate skill structure and metadata
validate:
	./scripts/validate_skills.sh
