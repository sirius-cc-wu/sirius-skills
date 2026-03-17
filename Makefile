.PHONY: install uninstall

REPO_ROOT := $(CURDIR)
COMMON_FLAGS := --global --yes --agent github-copilot --agent codex --agent antigravity --agent gemini-cli
MANAGED_SKILLS := \
	batch \
	close-track \
	commit \
	design-md \
	dioxus-stitch \
	dioxus-ui-ux \
	enhance-prompt \
	plan \
	react:components \
	remotion \
	sb-tracker \
	shadcn-ui \
	simplify \
	spec-driver \
	specify \
	stitch-design \
	stitch-loop \
	tasks

install:
	npx skills add "$(REPO_ROOT)/skills/spec-driver" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/specify" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/plan" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/tasks" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/close-track" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/commit" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/simplify" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/batch" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/dioxus-ui-ux" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/dioxus-stitch" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/sb-tracker/skills/sb-tracker" $(COMMON_FLAGS)
	npx skills add https://github.com/google-labs-code/stitch-skills --skill '*' $(COMMON_FLAGS)

uninstall:
	@installed="$$(npx skills ls -g --json | python3 -c 'import json, sys; managed = set("$(MANAGED_SKILLS)".split()); installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))')"; \
	if [ -n "$$installed" ]; then \
		printf '%s\n' "$$installed" | xargs npx skills remove $(COMMON_FLAGS); \
	else \
		echo "No managed skills installed."; \
	fi
