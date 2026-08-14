#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_catalog="$root/catalog/skills.md"
source_catalog="$root/catalog/sources.md"
track_directory="$root/catalog/tracks"
profile_directory="$root/skill-sets"
all_profile="$profile_directory/all.txt"
retired_ledger="$root/catalog/retired-skills.tsv"

fail() {
  echo "$1" >&2
  exit 1
}

read_profile() {
  sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "$1"
}

test -f "$root/README.md" || fail "missing README.md"
test -f "$root/AGENTS.md" || fail "missing AGENTS.md"
test -f "$skill_catalog" || fail "missing $skill_catalog"
test -f "$source_catalog" || fail "missing $source_catalog"
test -d "$track_directory" || fail "missing $track_directory"
test -f "$all_profile" || fail "missing $all_profile"
test -f "$retired_ledger" || fail "missing $retired_ledger"

profiles=(
  workflow
  iterative-design
  applying-uml-and-patterns
  reverse-engineering
  all
)

for profile in "${profiles[@]}"; do
  file="$profile_directory/$profile.txt"
  test -f "$file" || fail "missing skill profile $profile"
  mapfile -t members < <(read_profile "$file")
  test "${#members[@]}" -gt 0 || fail "skill profile is empty: $profile"
  duplicates="$(printf '%s\n' "${members[@]}" | sort | uniq -d)"
  test -z "$duplicates" || fail "duplicate skills in $profile: $duplicates"
done

if ! diff -u \
  <(read_profile "$profile_directory/iterative-design.txt" | sort) \
  <(read_profile "$profile_directory/applying-uml-and-patterns.txt" | sort); then
  fail "applying-uml-and-patterns must remain an alias for iterative-design"
fi

mapfile -t expected < <(read_profile "$all_profile")
mapfile -t discovered < <(
  find "$root/skills" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -printf '%h\n' |
    sed 's#.*/##' |
    sort
)

if ! diff -u \
  <(printf '%s\n' "${expected[@]}" | sort) \
  <(printf '%s\n' "${discovered[@]}"); then
  fail "skill-sets/all.txt must list every deployable skill exactly once"
fi

declare -A managed_by_name=()
for name in "${expected[@]}"; do
  managed_by_name["$name"]=1
done

declare -A retired_by_name=()
retired_count=0
while IFS= read -r line; do
  test -n "$line" || continue
  [[ "$line" == \#* ]] && continue
  IFS=$'\t' read -r name revision extra <<< "$line"
  test -n "$name" && test -n "$revision" && test -z "${extra:-}" ||
    fail "malformed retired skill entry: $line"
  [[ "$name" =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid retired skill name: $name"
  [[ "$revision" =~ ^[0-9a-f]{40}$ ]] || fail "invalid retirement evidence revision for $name"
  test -z "${retired_by_name[$name]:-}" || fail "duplicate retired skill: $name"
  test -z "${managed_by_name[$name]:-}" || fail "active skill is also retired: $name"
  test ! -d "$root/skills/$name" || fail "retired skill still has a package: $name"
  retired_by_name["$name"]="$revision"
  retired_count=$((retired_count + 1))
done < "$retired_ledger"

test "$retired_count" -gt 0 || fail "retired skill ledger is empty"

for profile in "${profiles[@]}"; do
  while IFS= read -r name; do
    test -n "${managed_by_name[$name]:-}" || fail "$profile references unmanaged skill $name"
  done < <(read_profile "$profile_directory/$profile.txt")
done

required_tracks=(
  repository-workflow
  client-to-code
  reverse-engineering
  iterative-analysis-design
  implementation-evolution
)

for name in "${required_tracks[@]}"; do
  test -f "$track_directory/$name.md" || fail "missing workflow track $name"
done

# Universal checks apply to every independently deployable skill.
for name in "${expected[@]}"; do
  [[ "$name" =~ ^[a-z0-9-]+$ ]] || fail "invalid skill name in managed set: $name"
  file="$root/skills/$name/SKILL.md"
  test -f "$file" || fail "missing $file"
  grep -q "^name: $name$" "$file" || fail "bad or missing name in $file"
  grep -q "^description: ." "$file" || fail "bad or missing description in $file"
  grep -q "^## Workflow" "$file" || fail "missing Workflow in $file"
  grep -Fq "| \`$name\` |" "$skill_catalog" || fail "skill catalog missing $name"
done

# Shared references have one canonical owner and byte-identical packaged copies.
shared_reference="$root/docs/shared/config-surface-governance.md"
test -f "$shared_reference" || fail "missing $shared_reference"
for target in \
  "$root/skills/simplify/references/config-surface-governance.md"; do
  test -f "$target" || fail "missing $target"
  cmp -s "$shared_reference" "$target" || fail "shared reference is out of sync: $target"
done

# Documentation-producing iterative-design and reverse-engineering skills share
# durable artifact rules. Workflow skills may overlap those profiles without
# becoming documentation specialists.
mapfile -t specialist_skills < <(
  comm -23 \
    <(
      {
        read_profile "$profile_directory/iterative-design.txt"
        read_profile "$profile_directory/reverse-engineering.txt"
      } | sort -u
    ) \
    <(read_profile "$profile_directory/workflow.txt" | sort -u)
)

for name in "${specialist_skills[@]}"; do
  file="$root/skills/$name/SKILL.md"
  grep -q "^## When to Use" "$file" || fail "missing When to Use in $file"
  grep -q "artifact-selection-budget.md" "$file" || fail "missing artifact selection budget guidance in $file"
  if [[ "$name" != "select-technical-artifacts" ]]; then
    grep -q "markdown-artifact-frontmatter.md" "$file" || fail "missing Markdown artifact frontmatter guidance in $file"
  fi
  grep -q "^## Verification" "$file" || fail "missing Verification in $file"
done

up_skill="$root/skills/plan-up-iterations/SKILL.md"
up_metadata="$root/skills/plan-up-iterations/agents/openai.yaml"
iteration_skill="$root/skills/run-development-iteration/SKILL.md"
selection_skill="$root/skills/select-technical-artifacts/SKILL.md"
selection_metadata="$root/skills/select-technical-artifacts/agents/openai.yaml"
layout_skill="$root/skills/design-repository-artifact-layout/SKILL.md"
layout_reference="$root/skills/design-repository-artifact-layout/references/artifact-layouts.md"
budget_reference="$root/skills/select-technical-artifacts/references/artifact-selection-budget.md"
frontmatter_reference="$root/skills/plan-up-iterations/references/markdown-artifact-frontmatter.md"

test -f "$layout_reference" || fail "missing $layout_reference"
test -f "$budget_reference" || fail "missing $budget_reference"
test -f "$frontmatter_reference" || fail "missing $frontmatter_reference"
test -f "$up_metadata" || fail "plan-up-iterations missing agents/openai.yaml"
grep -Fq '$plan-up-iterations' "$up_metadata" || fail "UP planner metadata missing skill invocation"
grep -q "^## Multi-Iteration UP Plan$" "$up_skill" || fail "UP planner missing multi-iteration plan"
grep -q "^## Artifact Durability$" "$up_skill" || fail "UP planner missing artifact durability guidance"
grep -q "^## Execution Handoff$" "$up_skill" || fail "UP planner missing execution handoff"
grep -q "design-repository-artifact-layout" "$up_skill" || fail "UP planner missing artifact layout handoff"
grep -q "^Artifact Budget:$" "$up_skill" || fail "UP plan template missing artifact budget"
grep -q 'at least two iteration candidates' "$up_skill" || fail "UP planner missing multi-iteration safeguard"
grep -q '^## UP Roadmap Candidate Mode$' "$iteration_skill" || fail "run-development-iteration missing UP candidate mode"
grep -q 'roadmap as planning input, not blanket execution authority' "$iteration_skill" || fail "run-development-iteration missing roadmap authority safeguard"
grep -q "^## Creation Gate$" "$budget_reference" || fail "artifact budget missing creation gate"
grep -q "^## Disposition Order$" "$budget_reference" || fail "artifact budget missing disposition guidance"
test -f "$selection_metadata" || fail "select-technical-artifacts missing agents/openai.yaml"
grep -Fq '$select-technical-artifacts' "$selection_metadata" || fail "artifact selection metadata missing skill invocation"
grep -q '^## Output$' "$selection_skill" || fail "artifact selection skill missing output guidance"
grep -q '^## Boundaries$' "$selection_skill" || fail "artifact selection skill missing boundary guidance"
grep -q 'keep with implementation' "$selection_skill" || fail "artifact selection skill missing executable disposition"
grep -q 'authorizes updating an existing artifact budget or plan' "$selection_skill" || fail "artifact selection skill missing authorized budget-update mode"
grep -q "^## Output$" "$layout_skill" || fail "artifact layout skill missing output guidance"
grep -q "^## Artifact Lifecycles$" "$layout_reference" || fail "artifact layout reference missing lifecycle guidance"
grep -q "^## Layout Options$" "$layout_reference" || fail "artifact layout reference missing layout options"
grep -q "^## Proposal Placement$" "$layout_reference" || fail "artifact layout reference missing proposal placement guidance"
grep -q "^## Linking Rules$" "$layout_reference" || fail "artifact layout reference missing linking rules"
grep -q '^type: "\[Descriptive artifact type\]"$' "$frontmatter_reference" || fail "frontmatter reference missing base type field"

layout_metadata="$root/skills/design-repository-artifact-layout/agents/openai.yaml"
test -f "$layout_metadata" || fail "design-repository-artifact-layout missing agents/openai.yaml"
grep -Fq '$design-repository-artifact-layout' "$layout_metadata" || fail "artifact layout metadata missing skill invocation"

adr_skill="$root/skills/record-architecture-decision/SKILL.md"
adr_metadata="$root/skills/record-architecture-decision/agents/openai.yaml"
test -f "$adr_metadata" || fail "record-architecture-decision missing agents/openai.yaml"
grep -Fq '$record-architecture-decision' "$adr_metadata" || fail "architecture decision metadata missing skill invocation"
grep -q '^## ADR Shape$' "$adr_skill" || fail "architecture decision skill missing ADR shape"
grep -q '^## Decision Discovery Mode$' "$adr_skill" || fail "architecture decision skill missing read-only discovery mode"
grep -q '^## Discovery and Indexing$' "$adr_skill" || fail "architecture decision skill missing discovery guidance"
grep -q '^## Confidence and Reconsideration$' "$adr_skill" || fail "architecture decision template missing reconsideration guidance"
grep -q 'substantively rewrite an accepted ADR' "$adr_skill" || fail "architecture decision skill missing supersession safeguard"

recovery_evidence_reference="$root/skills/reverse-engineer-software-system/references/recovery-evidence.md"
test -f "$recovery_evidence_reference" || fail "missing $recovery_evidence_reference"

recovery_skills=(
  reverse-engineer-software-system
  survey-existing-system
  recover-system-behavior
  reconstruct-software-architecture
  reconcile-recovered-design
)

for name in "${recovery_skills[@]}"; do
  file="$root/skills/$name/SKILL.md"
  metadata="$root/skills/$name/agents/openai.yaml"
  test -f "$metadata" || fail "missing $metadata"
  grep -q "recovery-evidence.md" "$file" || fail "$name missing recovery evidence guidance"
  grep -Fq "\$$name" "$metadata" || fail "$name metadata default prompt missing skill invocation"
done

client_discovery_skills=(
  stakeholder-requirements-elicitation
  requirements-synthesis-validation
  implementation-slice-briefing
)

for name in "${client_discovery_skills[@]}"; do
  metadata="$root/skills/$name/agents/openai.yaml"
  test -f "$metadata" || fail "missing $metadata"
  grep -Fq "\$$name" "$metadata" || fail "$name metadata default prompt missing skill invocation"
done

template_types=(
  "assess-development-input|Development Input Assessment"
  "record-architecture-decision|Architecture Decision"
  "stakeholder-requirements-elicitation|Stakeholder Evidence Record"
  "requirements-synthesis-validation|Requirements Discovery Brief"
  "implementation-slice-briefing|Implementation Slice Brief"
  "reverse-engineer-software-system|Reverse Engineering Record"
  "survey-existing-system|System Survey"
  "recover-system-behavior|Recovered Behavior Model"
  "reconstruct-software-architecture|Recovered Architecture"
  "reconcile-recovered-design|Design Reconciliation"
  "plan-up-iterations|Phase Plan"
  "use-case-modeling|Use Case"
  "domain-modeling|Domain Model"
  "system-sequence-diagrams|System Sequence Diagram"
  "operation-contracts|Operation Contract"
  "grasp-responsibility-design|Responsibility Decision"
  "use-case-realization|Use-Case Realization"
  "uml-class-diagram-design|Design Class Diagram"
  "design-pattern-application|Pattern Decision"
  "design-rust-lifecycles|Rust Lifecycle Design"
  "test-driven-implementation|Behavior Slice Evidence"
  "behavior-preserving-refactoring|Refactoring Record"
)

for entry in "${template_types[@]}"; do
  name="${entry%%|*}"
  type="${entry#*|}"
  template_files=("$root/skills/$name/SKILL.md")
  if [[ -d "$root/skills/$name/references" ]]; then
    while IFS= read -r reference; do
      template_files+=("$reference")
    done < <(find "$root/skills/$name/references" -maxdepth 1 -type f -name '*.md' -print)
  fi
  grep -q "^type: \"$type\"$" "${template_files[@]}" || fail "$name template missing type: $type"
done

grep -q "^# Skill Catalog$" "$skill_catalog" || fail "skill catalog missing title"
grep -q "^# Source Catalog$" "$source_catalog" || fail "source catalog missing title"
grep -q "^## Catalog and workflow tracks$" "$root/README.md" || fail "README missing workflow tracks"
grep -q "^## Consolidation history$" "$root/README.md" || fail "README missing consolidation history"

echo "Validated ${#expected[@]} skills across ${#profiles[@]} profiles."
echo "Validated $retired_count retired skill tombstones."
