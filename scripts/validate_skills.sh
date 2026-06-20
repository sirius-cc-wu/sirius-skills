#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

test -f "$root/README.md" || { echo "missing README.md" >&2; exit 1; }
test -f "$root/skill-inventory.md" || { echo "missing skill-inventory.md" >&2; exit 1; }
grep -q "Recommended Sequence" "$root/README.md" || { echo "README missing recommended sequence" >&2; exit 1; }
grep -q "Skill Inventory" "$root/skill-inventory.md" || { echo "inventory missing title" >&2; exit 1; }

expected=(
  use-case-modeling
  domain-modeling
  system-sequence-diagrams
  operation-contracts
  grasp-responsibility-design
  use-case-realization
  uml-class-diagram-design
  design-pattern-application
  iterative-up-analysis-design
)

for name in "${expected[@]}"; do
  file="$root/skills/$name/SKILL.md"
  test -f "$file" || { echo "missing $file" >&2; exit 1; }
  grep -q "^name: $name$" "$file" || { echo "bad or missing name in $file" >&2; exit 1; }
  grep -q "^description: .*Use when" "$file" || { echo "description must include Use when in $file" >&2; exit 1; }
  grep -q "^## When to Use" "$file" || { echo "missing When to Use in $file" >&2; exit 1; }
  grep -q "^## Workflow" "$file" || { echo "missing Workflow in $file" >&2; exit 1; }
  grep -q "^## Verification" "$file" || { echo "missing Verification in $file" >&2; exit 1; }
done

echo "Validated ${#expected[@]} skills and collection metadata."
