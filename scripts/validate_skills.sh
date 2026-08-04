#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_catalog="$root/catalog/skills.md"
source_catalog="$root/catalog/sources.md"
track_directory="$root/catalog/tracks"
profile_directory="$root/skill-sets"
all_profile="$profile_directory/all.txt"

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
  "$root/skills/governance-update/references/config-surface-governance.md" \
  "$root/skills/simplify/references/config-surface-governance.md"; do
  test -f "$target" || fail "missing $target"
  cmp -s "$shared_reference" "$target" || fail "shared reference is out of sync: $target"
done

# Iterative-design and reverse-engineering skills share durable artifact rules.
mapfile -t specialist_skills < <(
  {
    read_profile "$profile_directory/iterative-design.txt"
    read_profile "$profile_directory/reverse-engineering.txt"
  } | sort -u
)

for name in "${specialist_skills[@]}"; do
  file="$root/skills/$name/SKILL.md"
  grep -q "^## When to Use" "$file" || fail "missing When to Use in $file"
  grep -q "markdown-artifact-frontmatter.md" "$file" || fail "missing Markdown artifact frontmatter guidance in $file"
  grep -q "readable-technical-artifacts.md" "$file" || fail "missing readable technical artifact guidance in $file"
  grep -q "^## Verification" "$file" || fail "missing Verification in $file"
done

up_skill="$root/skills/iterative-up-analysis-design/SKILL.md"
layout_reference="$root/skills/iterative-up-analysis-design/references/artifact-layouts.md"
frontmatter_reference="$root/skills/iterative-up-analysis-design/references/markdown-artifact-frontmatter.md"
readability_reference="$root/skills/iterative-up-analysis-design/references/readable-technical-artifacts.md"

test -f "$layout_reference" || fail "missing $layout_reference"
test -f "$frontmatter_reference" || fail "missing $frontmatter_reference"
test -f "$readability_reference" || fail "missing $readability_reference"
grep -q "^## Artifact Durability$" "$up_skill" || fail "iterative UP skill missing artifact durability guidance"
grep -q "^Artifact Outcomes:$" "$up_skill" || fail "iteration template missing artifact outcomes"
grep -q "^## Artifact Lifecycles$" "$layout_reference" || fail "artifact layout reference missing lifecycle guidance"
grep -q "^## Layout Options$" "$layout_reference" || fail "artifact layout reference missing layout options"
grep -q "^## Linking Rules$" "$layout_reference" || fail "artifact layout reference missing linking rules"
grep -q '^type: "\[Descriptive artifact type\]"$' "$frontmatter_reference" || fail "frontmatter reference missing base type field"
grep -q '^## Writing Flow$' "$readability_reference" || fail "readability reference missing writing flow"
grep -q '^## Preserve Meaning$' "$readability_reference" || fail "readability reference missing meaning-preservation guidance"

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

rewrite_metadata="$root/skills/rewrite-technical-artifacts/agents/openai.yaml"
rewrite_skill="$root/skills/rewrite-technical-artifacts/SKILL.md"
test -f "$rewrite_metadata" || fail "rewrite-technical-artifacts missing agents/openai.yaml"
grep -Fq '$rewrite-technical-artifacts' "$rewrite_metadata" || fail "rewrite metadata missing skill invocation"
grep -q '^## Diff-Focused Review Mode$' "$rewrite_skill" || fail "rewrite skill missing diff-focused review mode"
grep -q '^## Final Editorial Pass$' "$readability_reference" || fail "readability reference missing final editorial handoff"

template_types=(
  "reverse-engineer-software-system|Reverse Engineering Record"
  "survey-existing-system|System Survey"
  "recover-system-behavior|Recovered Behavior Model"
  "reconstruct-software-architecture|Recovered Architecture"
  "reconcile-recovered-design|Design Reconciliation"
  "iterative-up-analysis-design|Iteration Record"
  "use-case-modeling|Use Case"
  "domain-modeling|Domain Model"
  "system-sequence-diagrams|System Sequence Diagram"
  "operation-contracts|Operation Contract"
  "grasp-responsibility-design|Responsibility Decision"
  "use-case-realization|Use-Case Realization"
  "uml-class-diagram-design|Design Class Diagram"
  "design-pattern-application|Pattern Decision"
  "test-driven-implementation|Behavior Slice Evidence"
  "behavior-preserving-refactoring|Refactoring Record"
)

for entry in "${template_types[@]}"; do
  name="${entry%%|*}"
  type="${entry#*|}"
  grep -q "^type: \"$type\"$" "$root/skills/$name/SKILL.md" || fail "$name template missing type: $type"
done

grep -q "^# Skill Catalog$" "$skill_catalog" || fail "skill catalog missing title"
grep -q "^# Source Catalog$" "$source_catalog" || fail "source catalog missing title"
grep -q "^## Catalog and workflow tracks$" "$root/README.md" || fail "README missing workflow tracks"
grep -q "^## Consolidation history$" "$root/README.md" || fail "README missing consolidation history"

echo "Validated ${#expected[@]} skills across ${#profiles[@]} profiles."
