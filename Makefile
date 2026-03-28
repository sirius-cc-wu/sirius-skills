.PHONY: install uninstall

REPO_ROOT := $(CURDIR)
COMMON_FLAGS := --global --yes --agent github-copilot --agent codex --agent antigravity --agent gemini-cli
MANAGED_SKILLS := \
	breakdown \
	close-slice \
	commit \
	configure-project \
	design \
	discover \
	evolve-feature \
	assess \
	reconcile-feature \
	guide-planning \
	propose \
	blueprint \
	review-execution \
	review-planning \
	simplify \
	guide-execution \
	slice \
	ui-flow

install:
	npx skills add "$(REPO_ROOT)/skills/guide-execution" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/brief" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/blueprint" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/guide-planning" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/propose" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/discover" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/evolve-feature" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/assess" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/reconcile-feature" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/design" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/ui-flow" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/breakdown" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/review-planning" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/slice" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/close-slice" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/review-execution" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/commit" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/configure-project" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/simplify" $(COMMON_FLAGS)

uninstall:
	@installed="$$(npx skills ls -g --json | python3 -c 'import json, sys; managed = set("$(MANAGED_SKILLS)".split()); installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))')"; \
	if [ -n "$$installed" ]; then \
		printf '%s\n' "$$installed" | xargs npx skills remove $(COMMON_FLAGS); \
	else \
		echo "No managed skills installed."; \
	fi
