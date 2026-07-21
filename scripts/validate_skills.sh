#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

test -f "$root/README.md" || { echo "missing README.md" >&2; exit 1; }
test -f "$root/skill-inventory.md" || { echo "missing skill-inventory.md" >&2; exit 1; }
grep -q "Recommended Sequence" "$root/README.md" || { echo "README missing recommended sequence" >&2; exit 1; }
grep -q "Skill Inventory" "$root/skill-inventory.md" || { echo "inventory missing title" >&2; exit 1; }

up_skill="$root/skills/iterative-up-analysis-design/SKILL.md"
layout_reference="$root/skills/iterative-up-analysis-design/references/artifact-layouts.md"
frontmatter_reference="$root/skills/iterative-up-analysis-design/references/markdown-artifact-frontmatter.md"
test -f "$layout_reference" || { echo "missing $layout_reference" >&2; exit 1; }
test -f "$frontmatter_reference" || { echo "missing $frontmatter_reference" >&2; exit 1; }
grep -q "references/artifact-layouts.md" "$up_skill" || { echo "iterative UP skill missing artifact layout reference" >&2; exit 1; }
grep -q "references/markdown-artifact-frontmatter.md" "$up_skill" || { echo "iterative UP skill missing Markdown frontmatter reference" >&2; exit 1; }
grep -q "^## Artifact Durability$" "$up_skill" || { echo "iterative UP skill missing artifact durability guidance" >&2; exit 1; }
grep -q "^Artifact Outcomes:$" "$up_skill" || { echo "iteration template missing artifact outcomes" >&2; exit 1; }
grep -q "^## Artifact Lifecycles$" "$layout_reference" || { echo "artifact layout reference missing lifecycle guidance" >&2; exit 1; }
grep -q "^## Layout Options$" "$layout_reference" || { echo "artifact layout reference missing layout options" >&2; exit 1; }
grep -q "^## Linking Rules$" "$layout_reference" || { echo "artifact layout reference missing linking rules" >&2; exit 1; }
grep -q "markdown-artifact-frontmatter.md" "$layout_reference" || { echo "artifact layout reference missing Markdown metadata guidance" >&2; exit 1; }
grep -q '^type: "\[Descriptive artifact type\]"$' "$frontmatter_reference" || { echo "frontmatter reference missing base type field" >&2; exit 1; }
grep -q '^## Reserved Files$' "$frontmatter_reference" || { echo "frontmatter reference missing reserved-file guidance" >&2; exit 1; }
grep -q "^## Artifact Durability and Layouts$" "$root/README.md" || { echo "README missing artifact durability section" >&2; exit 1; }
grep -q "artifact-layouts.md" "$root/README.md" || { echo "README missing artifact layout reference" >&2; exit 1; }
grep -q "durable design artifacts" "$root/skill-inventory.md" || { echo "inventory missing artifact durability boundary" >&2; exit 1; }

expected=(
  use-case-modeling
  domain-modeling
  system-sequence-diagrams
  operation-contracts
  grasp-responsibility-design
  use-case-realization
  uml-class-diagram-design
  design-pattern-application
  software-design-language-adaptation
  test-driven-implementation
  behavior-preserving-refactoring
  iterative-up-analysis-design
  inception
)

for name in "${expected[@]}"; do
  file="$root/skills/$name/SKILL.md"
  test -f "$file" || { echo "missing $file" >&2; exit 1; }
  grep -q "^name: $name$" "$file" || { echo "bad or missing name in $file" >&2; exit 1; }
  grep -q "^description: .*Use when" "$file" || { echo "description must include Use when in $file" >&2; exit 1; }
  grep -q "^## When to Use" "$file" || { echo "missing When to Use in $file" >&2; exit 1; }
  grep -q "^## Workflow" "$file" || { echo "missing Workflow in $file" >&2; exit 1; }
  grep -q "markdown-artifact-frontmatter.md" "$file" || { echo "missing Markdown artifact frontmatter guidance in $file" >&2; exit 1; }
  grep -q "^## Verification" "$file" || { echo "missing Verification in $file" >&2; exit 1; }
done

template_types=(
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
  file="$root/skills/$name/SKILL.md"
  grep -q "^type: \"$type\"$" "$file" || { echo "$name template missing type: $type" >&2; exit 1; }
done

echo "Validated ${#expected[@]} skills and collection metadata."
