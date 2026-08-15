# justfile for sirius-skills

set shell := ["bash", "-c"]

repo_root := justfile_directory()
agent_flags := "--yes --agent github-copilot --agent codex --agent antigravity --agent antigravity-cli"
retired_ledger := repo_root / "catalog/retired-skills.tsv"
addy_source := "https://github.com/addyosmani/agent-skills/archive/5a1b82d6445d1e2f0abeea1072851419a50c0e5c.tar.gz"
addy_profile := repo_root / "catalog/external-skill-sets/addy-osmani.txt"
addy_lock_source := "addyosmani/agent-skills"
source_skills_dir := repo_root / "skills"

# Install a source-linked profile into a target project by default.
install target_dir skill_set="workflow": (install-local target_dir skill_set)

# Install into a target project; all also installs the local Addy add-ons.
install-local target_dir skill_set="workflow": sync-shared-references
	#!/usr/bin/env bash
	set -euo pipefail
	target_dir={{quote(target_dir)}}
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
	if [[ ! -d "$target_dir" ]]; then
		echo "Target project is not a directory: $target_dir" >&2
		exit 1
	fi
	target_dir=$(realpath -e -- "$target_dir")
	target_skills_dir="$target_dir/.agents/skills"
	just --justfile "{{repo_root}}/justfile" prune-retired-local "$target_dir"

	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		link-profile --profile "$skill_set_file" \
		--source-dir "{{source_skills_dir}}" --target-dir "$target_skills_dir"
	if [[ "$skill_set" == "all" ]]; then
		mapfile -t external_skills < <(sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "{{addy_profile}}")
		external_skill_flags=()
		for skill in "${external_skills[@]}"; do
			external_skill_flags+=(--skill "$skill")
		done
		(
			cd "$target_dir"
			npx --yes skills add "{{addy_source}}" {{agent_flags}} "${external_skill_flags[@]}"
		)
	fi

# Preserve the packaged global installation as an explicit command.
install-global skill_set="workflow": sync-shared-references
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

	combined_profile=$(mktemp)
	trap 'rm -f "$combined_profile"' EXIT
	cat "$skill_set_file" > "$combined_profile"
	if [[ "$skill_set" == "all" ]]; then
		test -f "{{addy_profile}}"
		cat "{{addy_profile}}" >> "$combined_profile"
	fi

	mapfile -t skills < <(sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "$skill_set_file")
	skill_flags=()
	for skill in "${skills[@]}"; do
		skill_flags+=(--skill "$skill")
	done
	npx --yes skills add "{{repo_root}}" --global {{agent_flags}} "${skill_flags[@]}"
	if [[ "$skill_set" == "all" ]]; then
		mapfile -t external_skills < <(sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "{{addy_profile}}")
		external_skill_flags=()
		for skill in "${external_skills[@]}"; do
			external_skill_flags+=(--skill "$skill")
		done
		npx --yes skills add "{{addy_source}}" --global {{agent_flags}} "${external_skill_flags[@]}"
	fi
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		link-profile --profile "$combined_profile"
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		record-installed --profile "$combined_profile"
# Compatibility alias for the packaged global installation.
install-packaged skill_set="workflow": (install-global skill_set)

# Sync canonical shared references into self-contained skill packages.
sync-shared-references:
	env PYTHONPATH="{{repo_root}}/src" python3 -c 'from sirius_skills.commands.sync_shared_references import main; raise SystemExit(main([]))'

# Remove retired target-project links that still point into this checkout.
prune-retired-local target_dir:
	#!/usr/bin/env bash
	set -euo pipefail
	target_dir={{quote(target_dir)}}
	if [[ ! -d "$target_dir" ]]; then
		echo "Target project is not a directory: $target_dir" >&2
		exit 1
	fi
	target_dir=$(realpath -e -- "$target_dir")
	target_skills_dir="$target_dir/.agents/skills"
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		unlink-retired --ledger "{{retired_ledger}}" --include-unowned \
		--source-dir "{{source_skills_dir}}" --target-dir "$target_skills_dir"

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

# Remove a source-linked profile from a target project by default.
uninstall target_dir skill_set="workflow": (uninstall-local target_dir skill_set)

# Remove from a target project; all also removes the local Addy add-ons.
uninstall-local target_dir skill_set="workflow":
	#!/usr/bin/env bash
	set -euo pipefail
	target_dir={{quote(target_dir)}}
	skill_set={{quote(skill_set)}}
	skill_set_file="{{repo_root}}/skill-sets/${skill_set}.txt"
	if [[ ! "$skill_set" =~ ^[a-z0-9][a-z0-9-]*$ || ! -f "$skill_set_file" ]]; then
		echo "Unknown skill set: $skill_set" >&2
		exit 1
	fi
	if [[ ! -d "$target_dir" ]]; then
		echo "Target project is not a directory: $target_dir" >&2
		exit 1
	fi
	target_dir=$(realpath -e -- "$target_dir")
	target_skills_dir="$target_dir/.agents/skills"
	just --justfile "{{repo_root}}/justfile" prune-retired-local "$target_dir"

	if [[ "$skill_set" == "all" ]]; then
		env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
			remove-locked-profile --profile "{{addy_profile}}" \
			--lock "$target_dir/skills-lock.json" --skills-dir "$target_skills_dir" \
			--source "{{addy_lock_source}}"
	fi
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		unlink-profile --profile "$skill_set_file" \
		--source-dir "{{source_skills_dir}}" --target-dir "$target_skills_dir"

# Preserve owned global removal as an explicit command.
uninstall-global skill_set="workflow":
	#!/usr/bin/env bash
	set -euo pipefail
	skill_set={{quote(skill_set)}}
	skill_set_file="{{repo_root}}/skill-sets/${skill_set}.txt"
	if [[ ! "$skill_set" =~ ^[a-z0-9][a-z0-9-]*$ || ! -f "$skill_set_file" ]]; then
		echo "Unknown skill set: $skill_set" >&2
		exit 1
	fi
	just --justfile "{{repo_root}}/justfile" prune-retired

	combined_profile=$(mktemp)
	trap 'rm -f "$combined_profile"' EXIT
	cat "$skill_set_file" > "$combined_profile"
	if [[ "$skill_set" == "all" ]]; then
		test -f "{{addy_profile}}"
		cat "{{addy_profile}}" >> "$combined_profile"
	fi

	installed=$(npx --yes skills ls -g --json | python3 -c 'import json, pathlib, sys; managed = {line.strip() for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")}; installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))' "$combined_profile")
	if [ -n "$installed" ]; then
		mapfile -t installed_skills <<< "$installed"
		# Global agent aliases share the universal skill directory, so removal
		# must not retain entries through agents outside the install target list.
		npx --yes skills remove "${installed_skills[@]}" --global --yes
	else
		echo "No installed skills found for profile: $skill_set"
	fi
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		unlink-profile --profile "$combined_profile"
	env PYTHONPATH="{{repo_root}}/src" python3 -m sirius_skills.commands.manage_installed_skills \
		forget-profile --profile "$combined_profile"
# Compatibility alias for packaged global removal.
uninstall-packaged skill_set="workflow": (uninstall-global skill_set)

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
