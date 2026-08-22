#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_catalog="$root/catalog/skills.md"
source_catalog="$root/catalog/sources.md"
track_directory="$root/catalog/tracks"
profile_directory="$root/skill-sets"
all_profile="$profile_directory/all.txt"
retired_ledger="$root/catalog/retired-skills.tsv"
external_addy_profile="$root/catalog/external-skill-sets/addy-osmani.txt"

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
test -f "$external_addy_profile" || fail "missing external Addy skill profile"
mapfile -t external_addy_skills < <(read_profile "$external_addy_profile")
test "${#external_addy_skills[@]}" -gt 0 || fail "external Addy skill profile is empty"
declare -A external_addy_by_name=()
for name in "${external_addy_skills[@]}"; do
  [[ "$name" =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid external skill name: $name"
  test -z "${external_addy_by_name[$name]:-}" || fail "duplicate external skill: $name"
  test -z "${managed_by_name[$name]:-}" || fail "external skill is active in Sirius catalog: $name"
  test -z "${retired_by_name[$name]:-}" || fail "external skill is retired in Sirius ledger: $name"
  external_addy_by_name["$name"]=1
done

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
  description="$(sed -n 's/^description: //p' "$file" | head -n 1)"
  [[ "$description" != *": "* || "$description" =~ ^\".*\"$ || "$description" =~ ^\'.*\'$ ]] ||
    fail "description containing ': ' must be YAML-quoted in $file"
  grep -q "^## Workflow" "$file" || fail "missing Workflow in $file"
  grep -Fq "| \`$name\` |" "$skill_catalog" || fail "skill catalog missing $name"
done

# Shared references have one canonical owner and byte-identical packaged copies.
shared_reference="$root/docs/shared/config-surface-governance.md"
test -f "$shared_reference" || fail "missing $shared_reference"
for target in \
  "$root/skills/behavior-preserving-refactoring/references/config-surface-governance.md"; do
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

development_skill="$root/skills/iterative-risk-driven-development/SKILL.md"
development_metadata="$root/skills/iterative-risk-driven-development/agents/openai.yaml"
selection_skill="$root/skills/select-technical-artifacts/SKILL.md"
selection_metadata="$root/skills/select-technical-artifacts/agents/openai.yaml"
layout_skill="$root/skills/design-repository-artifact-layout/SKILL.md"
layout_reference="$root/skills/design-repository-artifact-layout/references/artifact-layouts.md"
budget_reference="$root/skills/select-technical-artifacts/references/artifact-selection-budget.md"
frontmatter_reference="$root/skills/iterative-risk-driven-development/references/markdown-artifact-frontmatter.md"
responsibility_skill="$root/skills/grasp-responsibility-design/SKILL.md"
rust_lifecycle_skill="$root/skills/design-rust-lifecycles/SKILL.md"
rust_lifecycle_template="$root/skills/design-rust-lifecycles/assets/rust-lifecycle-design.md"
refactoring_skill="$root/skills/behavior-preserving-refactoring/SKILL.md"

test -f "$layout_reference" || fail "missing $layout_reference"
test -f "$budget_reference" || fail "missing $budget_reference"
test -f "$frontmatter_reference" || fail "missing $frontmatter_reference"
test -f "$development_metadata" || fail "iterative-risk-driven-development missing agents/openai.yaml"
grep -Fq '$iterative-risk-driven-development' "$development_metadata" || fail "iterative development metadata missing skill invocation"
grep -q "^## Execution Modes$" "$development_skill" || fail "iterative development skill missing execution modes"
grep -q "^## Boundary-Sensitive Refactoring Gate$" "$development_skill" || fail "iterative development skill missing boundary-sensitive refactoring gate"
grep -q "representative end-to-end" "$development_skill" || fail "iterative development skill missing vertical outcome safeguard"
grep -q "^## Rust Ownership and Lifecycle Design$" "$development_skill" || fail "iterative development skill missing Rust lifecycle guidance"
grep -q "^## Iteration Record Template$" "$development_skill" || fail "iterative development skill missing iteration record template"
grep -q "design-rust-lifecycles" "$development_skill" || fail "iterative development skill missing Rust specialist handoff"
grep -q "language-native" "$responsibility_skill" || fail "responsibility design skill missing native owner guidance"
grep -q "^## Boundaries$" "$responsibility_skill" || fail "responsibility design skill missing boundary guidance"
grep -q "representative scenario" "$rust_lifecycle_skill" || fail "Rust lifecycle skill missing system-context input"
grep -q "^## Design Context and Responsibility Inputs$" "$rust_lifecycle_template" || fail "Rust lifecycle template missing responsibility inputs"
grep -q "^## Completion Boundary$" "$rust_lifecycle_template" || fail "Rust lifecycle template missing completion boundary"
grep -q "Classify boundary impact" "$refactoring_skill" || fail "refactoring skill missing boundary-impact classification"
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
grep -q "^## Idea Placement$" "$layout_reference" || fail "artifact layout reference missing idea placement guidance"
grep -q "^## Linking Rules$" "$layout_reference" || fail "artifact layout reference missing linking rules"
grep -q '^type: "\[Descriptive artifact type\]"$' "$frontmatter_reference" || fail "frontmatter reference missing base type field"

layout_metadata="$root/skills/design-repository-artifact-layout/agents/openai.yaml"
test -f "$layout_metadata" || fail "design-repository-artifact-layout missing agents/openai.yaml"
grep -Fq '$design-repository-artifact-layout' "$layout_metadata" || fail "artifact layout metadata missing skill invocation"

template_types=(
  "assess-development-input|Development Input Assessment"
  "iterative-risk-driven-development|Iteration Record"
  "use-case-modeling|Use Case"
  "domain-modeling|Domain Model"
  "system-sequence-diagrams|System Sequence Diagram"
  "operation-contracts|Operation Contract"
  "grasp-responsibility-design|Responsibility Decision"
  "use-case-realization|Use-Case Realization"
  "uml-class-diagram-design|Design Class Diagram"
  "design-pattern-application|Pattern Decision"
  "design-rust-lifecycles|Rust Lifecycle Design"
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
echo "Validated ${#external_addy_skills[@]} external Addy add-on skills."
echo "Validated $retired_count retired skill tombstones."
