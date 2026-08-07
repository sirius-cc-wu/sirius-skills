# justfile for sirius-skills

set shell := ["bash", "-c"]

repo_root := justfile_directory()
common_flags := "--global --yes --agent github-copilot --agent codex --agent antigravity --agent antigravity-cli"
retired_ledger := repo_root / "catalog/retired-skills.tsv"

# Install the workflow profile by default, or one named profile.
install skill_set="workflow": sync-shared-references
	#!/usr/bin/env bash
	set -euo pipefail
	skill_set={{quote(skill_set)}}
	skill_set_file="{{repo_root}}/skill-sets/${skill_set}.txt"
	if [[ ! "$skill_set" =~ ^[a-z0-9][a-z0-9-]*$ || ! -f "$skill_set_file" ]]; then
		echo "Unknown skill set: $skill_set" >&2
		echo "Available skill sets:" >&2
		find "{{repo_root}}/skill-sets" -maxdepth 1 -type f -name '*.txt' -printf '  %f\n' \
			| sed 's/\.txt$//' \
			| sort >&2
		exit 1
	fi
	just --justfile "{{repo_root}}/justfile" prune-retired

	mapfile -t skills < <(sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "$skill_set_file")
	skill_flags=()
	for skill in "${skills[@]}"; do
		skill_flags+=(--skill "$skill")
	done
	npx --yes skills add "{{repo_root}}" {{common_flags}} "${skill_flags[@]}"
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		link-profile --profile "$skill_set_file"
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		record-installed --profile "$skill_set_file"

# Compatibility alias for profile installation.
install-packaged skill_set="workflow": (install skill_set)

# Sync canonical shared references into self-contained skill packages.
sync-shared-references:
	env PYTHONPATH="{{repo_root}}/src" python3 -c 'from sirius_skills.commands.sync_shared_references import main; raise SystemExit(main([]))'

# Remove retired skills whose installation is recorded as owned by Sirius.
prune-retired:
	#!/usr/bin/env bash
	set -euo pipefail
	retired=$(npx --yes skills ls -g --json | \
		env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
			select-retired --ledger "{{retired_ledger}}")
	if [ -n "$retired" ]; then
		mapfile -t retired_skills <<< "$retired"
		npx --yes skills remove "${retired_skills[@]}" --global --yes
	else
		echo "No owned retired Sirius skills found."
	fi
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		unlink-retired --ledger "{{retired_ledger}}"
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		forget-retired --ledger "{{retired_ledger}}"

# Explicit migration for installations created before ownership state existed.
prune-retired-legacy:
	#!/usr/bin/env bash
	set -euo pipefail
	retired=$(npx --yes skills ls -g --json | \
		env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
			select-retired --ledger "{{retired_ledger}}" --include-unowned)
	if [ -n "$retired" ]; then
		mapfile -t retired_skills <<< "$retired"
		npx --yes skills remove "${retired_skills[@]}" --global --yes
	else
		echo "No retired Sirius skill names found."
	fi
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		unlink-retired --ledger "{{retired_ledger}}" --include-unowned
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		forget-retired --ledger "{{retired_ledger}}"

# Remove installed skills belonging to the selected profile.
uninstall skill_set="workflow":
	#!/usr/bin/env bash
	set -euo pipefail
	skill_set={{quote(skill_set)}}
	skill_set_file="{{repo_root}}/skill-sets/${skill_set}.txt"
	if [[ ! "$skill_set" =~ ^[a-z0-9][a-z0-9-]*$ || ! -f "$skill_set_file" ]]; then
		echo "Unknown skill set: $skill_set" >&2
		exit 1
	fi
	just --justfile "{{repo_root}}/justfile" prune-retired

	installed=$(npx --yes skills ls -g --json | python3 -c 'import json, pathlib, sys; managed = {line.strip() for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")}; installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))' "$skill_set_file")
	if [ -n "$installed" ]; then
		mapfile -t installed_skills <<< "$installed"
		# Global agent aliases share the universal skill directory, so removal
		# must not retain entries through agents outside the install target list.
		npx --yes skills remove "${installed_skills[@]}" --global --yes
	else
		echo "No installed skills found for profile: $skill_set"
	fi
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		unlink-profile --profile "$skill_set_file"
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		forget-profile --profile "$skill_set_file"

# Compatibility alias for profile removal.
uninstall-packaged skill_set="workflow": (uninstall skill_set)

# Validate all skills, profiles, catalogs, and collection-specific contracts.
validate: eval-routing
	./scripts/validate_skills.sh

# Run free, deterministic skill-description routing checks.
eval-routing:
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.run_evals --root "{{repo_root}}"

# Print a behavioral eval plan without invoking Codex or spending tokens.
eval-behavior-dry-run skill case repeat="1":
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.run_evals --root "{{repo_root}}" --behavioral {{quote(skill)}} --case {{quote(case)}} --repeat {{quote(repeat)}} --dry-run

# Run an explicitly selected behavioral case through Codex one or more times.
eval-behavior skill case repeat="1":
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.run_evals --root "{{repo_root}}" --behavioral {{quote(skill)}} --case {{quote(case)}} --repeat {{quote(repeat)}}

# Add an opt-in, non-gating semantic judge to a behavioral case.
eval-behavior-judged skill case repeat="1":
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.run_evals --root "{{repo_root}}" --behavioral {{quote(skill)}} --case {{quote(case)}} --repeat {{quote(repeat)}} --judge

# Check a judge repeatedly against declared positive and negative controls.
eval-judge-calibration skill case repeat="1":
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.run_evals --root "{{repo_root}}" --behavioral {{quote(skill)}} --case {{quote(case)}} --calibrate-judge --repeat {{quote(repeat)}}

# Compare the same calibration controls across two judge models.
eval-judge-comparison skill case base_model compare_model repeat="1":
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.run_evals --root "{{repo_root}}" --behavioral {{quote(skill)}} --case {{quote(case)}} --calibrate-judge --judge-model {{quote(base_model)}} --compare-judge-model {{quote(compare_model)}} --repeat {{quote(repeat)}}
