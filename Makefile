.PHONY: install uninstall install-packaged uninstall-packaged sync-shared-references sync-shared-runtime validate-workflow-state

REPO_ROOT := $(CURDIR)
COMMON_FLAGS := --global --yes --agent github-copilot --agent codex --agent antigravity --agent gemini-cli
MANAGED_SKILLS := \
	autoplan \
	audit-artifacts \
	measure-artifacts \
	trace-artifacts \
	report-artifacts \
	repair-artifacts \
	archive-artifacts \
	brief \
	breakdown \
	create-pr \
	close-slice \
	commit \
	bootstrap \
	design \
	discover \
	add-subfeature \
	migrate-subfeatures \
	assess \
	guide-scope \
	guide-planning \
	propose \
	blueprint \
	reconcile-execution \
	review-execution \
	review-planning \
	simplify \
	guide-execution \
	learn \
	ship \
	ship-worktree \
	ship-slice \
	slice \
	ui-flow \
	governance-update \
	research
MANAGED_SKILL_FLAGS := $(foreach skill,$(MANAGED_SKILLS),--skill $(skill))

install: sync-shared-runtime sync-shared-references
	npx skills add "$(REPO_ROOT)" $(COMMON_FLAGS) $(MANAGED_SKILL_FLAGS)

install-packaged: install

sync-shared-references:
	python3 scripts/sync_shared_skill_references.py

sync-shared-runtime:
	python3 scripts/sync_shared_skill_runtime.py

validate-workflow-state:
	python3 scripts/validate_workflow_state.py

uninstall: uninstall-packaged

uninstall-packaged:
	@installed="$$(npx skills ls -g --json | python3 -c 'import json, sys; managed = set("$(MANAGED_SKILLS)".split()); installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))')"; \
	if [ -n "$$installed" ]; then \
		printf '%s\n' "$$installed" | xargs npx skills remove $(COMMON_FLAGS); \
	else \
		echo "No managed skills installed."; \
	fi
