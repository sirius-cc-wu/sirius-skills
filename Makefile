.PHONY: install uninstall

REPO_ROOT := $(CURDIR)
COMMON_FLAGS := --global --yes --agent github-copilot --agent codex --agent antigravity --agent gemini-cli
MANAGED_SKILLS := \
	breakdown \
	close-track \
	commit \
	design \
	design-md \
	discover \
	planning-driver \
	dioxus-stitch \
	dioxus-ui-ux \
	enhance-prompt \
	plan \
	review-execution \
	review-planning \
	react:components \
	remotion \
	shadcn-ui \
	simplify \
	define \
	execution-driver \
	stitch-design \
	stitch-loop \
	track \
	ui-flow

install:
	npx skills add "$(REPO_ROOT)/skills/execution-driver" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/define" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/plan" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/planning-driver" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/discover" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/design" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/ui-flow" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/breakdown" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/review-planning" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/track" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/close-track" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/review-execution" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/commit" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/simplify" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/dioxus-ui-ux" $(COMMON_FLAGS)
	npx skills add "$(REPO_ROOT)/skills/dioxus-stitch" $(COMMON_FLAGS)
	npx skills add https://github.com/google-labs-code/stitch-skills --skill '*' $(COMMON_FLAGS)

uninstall:
	@installed="$$(npx skills ls -g --json | python3 -c 'import json, sys; managed = set("$(MANAGED_SKILLS)".split()); installed = [item["name"] for item in json.load(sys.stdin) if item.get("name") in managed]; print("\n".join(installed))')"; \
	if [ -n "$$installed" ]; then \
		printf '%s\n' "$$installed" | xargs npx skills remove $(COMMON_FLAGS); \
	else \
		echo "No managed skills installed."; \
	fi
