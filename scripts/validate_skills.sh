#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

test -f "$root/README.md" || { echo "missing README.md" >&2; exit 1; }
skill_catalog="$root/catalog/skills.md"
source_catalog="$root/catalog/sources.md"
track_directory="$root/catalog/tracks"
managed_skill_set="$root/skill-sets/all.txt"
test -f "$skill_catalog" || { echo "missing $skill_catalog" >&2; exit 1; }
test -f "$source_catalog" || { echo "missing $source_catalog" >&2; exit 1; }
test -d "$track_directory" || { echo "missing $track_directory" >&2; exit 1; }
test -f "$managed_skill_set" || { echo "missing $managed_skill_set" >&2; exit 1; }
grep -q "Workflow Tracks" "$root/README.md" || { echo "README missing workflow tracks" >&2; exit 1; }
grep -q "^# Skill Catalog$" "$skill_catalog" || { echo "skill catalog missing title" >&2; exit 1; }
grep -q "^# Source Catalog$" "$source_catalog" || { echo "source catalog missing title" >&2; exit 1; }

required_tracks=(
  client-to-code
  reverse-engineering
  iterative-analysis-design
  implementation-evolution
)

for name in "${required_tracks[@]}"; do
  test -f "$track_directory/$name.md" || { echo "missing workflow track $name" >&2; exit 1; }
done

up_skill="$root/skills/iterative-up-analysis-design/SKILL.md"
layout_reference="$root/skills/iterative-up-analysis-design/references/artifact-layouts.md"
frontmatter_reference="$root/skills/iterative-up-analysis-design/references/markdown-artifact-frontmatter.md"
readability_reference="$root/skills/iterative-up-analysis-design/references/readable-technical-artifacts.md"
test -f "$layout_reference" || { echo "missing $layout_reference" >&2; exit 1; }
test -f "$frontmatter_reference" || { echo "missing $frontmatter_reference" >&2; exit 1; }
test -f "$readability_reference" || { echo "missing $readability_reference" >&2; exit 1; }
grep -q "references/artifact-layouts.md" "$up_skill" || { echo "iterative UP skill missing artifact layout reference" >&2; exit 1; }
grep -q "references/markdown-artifact-frontmatter.md" "$up_skill" || { echo "iterative UP skill missing Markdown frontmatter reference" >&2; exit 1; }
grep -q "references/readable-technical-artifacts.md" "$up_skill" || { echo "iterative UP skill missing readable artifact reference" >&2; exit 1; }
grep -q "^## Artifact Durability$" "$up_skill" || { echo "iterative UP skill missing artifact durability guidance" >&2; exit 1; }
grep -q "^Artifact Outcomes:$" "$up_skill" || { echo "iteration template missing artifact outcomes" >&2; exit 1; }
grep -q "^## Artifact Lifecycles$" "$layout_reference" || { echo "artifact layout reference missing lifecycle guidance" >&2; exit 1; }
grep -q "^## Layout Options$" "$layout_reference" || { echo "artifact layout reference missing layout options" >&2; exit 1; }
grep -q "^## Linking Rules$" "$layout_reference" || { echo "artifact layout reference missing linking rules" >&2; exit 1; }
grep -q "markdown-artifact-frontmatter.md" "$layout_reference" || { echo "artifact layout reference missing Markdown metadata guidance" >&2; exit 1; }
grep -q '^type: "\[Descriptive artifact type\]"$' "$frontmatter_reference" || { echo "frontmatter reference missing base type field" >&2; exit 1; }
grep -q '^## Reserved Files$' "$frontmatter_reference" || { echo "frontmatter reference missing reserved-file guidance" >&2; exit 1; }
grep -q '^## Writing Flow$' "$readability_reference" || { echo "readability reference missing writing flow" >&2; exit 1; }
grep -q '^## Preserve Meaning$' "$readability_reference" || { echo "readability reference missing meaning-preservation guidance" >&2; exit 1; }
grep -q "^## Artifact Durability and Layouts$" "$root/README.md" || { echo "README missing artifact durability section" >&2; exit 1; }
grep -q "artifact-layouts.md" "$root/README.md" || { echo "README missing artifact layout reference" >&2; exit 1; }
grep -q "durable design artifacts" "$skill_catalog" || { echo "skill catalog missing artifact durability boundary" >&2; exit 1; }

mapfile -t expected < <(
  sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "$managed_skill_set"
)
test "${#expected[@]}" -gt 0 || { echo "managed skill set is empty" >&2; exit 1; }

duplicates="$(
  printf '%s\n' "${expected[@]}" |
    sort |
    uniq -d
)"
test -z "$duplicates" || { echo "duplicate managed skills: $duplicates" >&2; exit 1; }

mapfile -t discovered < <(
  find "$root/skills" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -printf '%h\n' |
    sed 's#.*/##' |
    sort
)

if ! diff -u \
  <(printf '%s\n' "${expected[@]}" | sort) \
  <(printf '%s\n' "${discovered[@]}"); then
  echo "skill-sets/all.txt must list every deployable skill exactly once" >&2
  exit 1
fi

declare -A managed_by_name=()
for name in "${expected[@]}"; do
  managed_by_name["$name"]=1
done

for set_file in "$root"/skill-sets/*.txt; do
  while IFS= read -r name; do
    [[ "$name" =~ ^[[:space:]]*(#|$) ]] && continue
    test -n "${managed_by_name[$name]:-}" || {
      echo "$(basename "$set_file") references unmanaged skill $name" >&2
      exit 1
    }
  done < "$set_file"
done

for name in "${expected[@]}"; do
  [[ "$name" =~ ^[a-z0-9-]+$ ]] || { echo "invalid skill name in managed set: $name" >&2; exit 1; }
  file="$root/skills/$name/SKILL.md"
  test -f "$file" || { echo "missing $file" >&2; exit 1; }
  grep -q "^name: $name$" "$file" || { echo "bad or missing name in $file" >&2; exit 1; }
  grep -q "^description: .*Use when" "$file" || { echo "description must include Use when in $file" >&2; exit 1; }
  grep -Fq "| \`$name\` |" "$skill_catalog" || { echo "skill catalog missing $name" >&2; exit 1; }
  grep -q "^## When to Use" "$file" || { echo "missing When to Use in $file" >&2; exit 1; }
  grep -q "^## Workflow" "$file" || { echo "missing Workflow in $file" >&2; exit 1; }
  grep -q "markdown-artifact-frontmatter.md" "$file" || { echo "missing Markdown artifact frontmatter guidance in $file" >&2; exit 1; }
  grep -q "readable-technical-artifacts.md" "$file" || { echo "missing readable technical artifact guidance in $file" >&2; exit 1; }
  grep -q "^## Verification" "$file" || { echo "missing Verification in $file" >&2; exit 1; }
done

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

recovery_evidence_reference="$root/skills/reverse-engineer-software-system/references/recovery-evidence.md"
test -f "$recovery_evidence_reference" || { echo "missing $recovery_evidence_reference" >&2; exit 1; }

reverse_engineering_skills=(
  reverse-engineer-software-system
  survey-existing-system
  recover-system-behavior
  reconstruct-software-architecture
  reconcile-recovered-design
)

for name in "${reverse_engineering_skills[@]}"; do
  file="$root/skills/$name/SKILL.md"
  metadata="$root/skills/$name/agents/openai.yaml"
  test -f "$metadata" || { echo "missing $metadata" >&2; exit 1; }
  grep -q "recovery-evidence.md" "$file" || { echo "$name missing recovery evidence guidance" >&2; exit 1; }
  grep -Fq "\$$name" "$metadata" || { echo "$name metadata default prompt missing skill invocation" >&2; exit 1; }
done

rewrite_metadata="$root/skills/rewrite-technical-artifacts/agents/openai.yaml"
test -f "$rewrite_metadata" || { echo "rewrite-technical-artifacts missing agents/openai.yaml" >&2; exit 1; }
grep -Fq '$rewrite-technical-artifacts' "$rewrite_metadata" || {
  echo "rewrite-technical-artifacts metadata default prompt missing skill invocation" >&2
  exit 1
}

for entry in "${template_types[@]}"; do
  name="${entry%%|*}"
  type="${entry#*|}"
  file="$root/skills/$name/SKILL.md"
  grep -q "^type: \"$type\"$" "$file" || { echo "$name template missing type: $type" >&2; exit 1; }
done

echo "Validated ${#expected[@]} skills and collection metadata."
