#!/usr/bin/env python3

"""
Skill initializer - creates a new skill from a template.

Usage:
    python init_skill.py <skill-name> --path <path>

Examples:
    python init_skill.py my-new-skill --path skills/public
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SKILL_TEMPLATE = """---
name: {skill_name}
description: TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: CSV-Processor skill with "Workflow Decision Tree" → "Ingestion" → "Cleaning" → "Analysis"
- Structure: ## Overview → ## Workflow Decision Tree → ## Step 1 → ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" → "Merge PDFs" → "Split PDFs" → "Extract Text"
- Structure: ## Overview → ## Quick Start → ## Task Category 1 → ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" → "Colors" → "Typography" → "Features"
- Structure: ## Overview → ## Guidelines → ## Specifications → ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" → numbered capability list
- Structure: ## Overview → ## Core Capabilities → ### 1. Feature → ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed
- Explanations of why important steps matter, not just what to do
- Variant-specific details moved into references/ when the skill supports multiple frameworks, domains, or output modes]

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: fill_fillable_fields.py, extract_form_field_info.py - utilities for PDF manipulation
- CSV skill: normalize_schema.py, merge_datasets.py - utilities for tabular data manipulation

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Gemini CLI for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Gemini CLI's process and thinking.

**Examples from other skills:**
- Product management: communication.md, context_building.md - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Gemini CLI should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Gemini CLI produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

### Iteration notes

- If the skill has objectively verifiable behavior, keep a local `evals/` folder with representative prompts, example inputs, and expected outcomes while iterating.
- The packaged `.skill` file should stay focused on the actual skill. Local `evals/` directories are for development and are excluded by the packager.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
"""

EXAMPLE_SCRIPT = """#!/usr/bin/env python3

\"\"\"
Example helper script for {skill_name}

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.

Example real scripts from other skills:
- pdf/scripts/fill_fillable_fields.py - Fills PDF form fields
- pdf/scripts/convert_pdf_to_images.py - Converts PDF pages to images

Agentic Ergonomics:
- Suppress tracebacks.
- Return clean success/failure strings.
- Truncate long outputs.
\"\"\"

import sys


def main() -> int:
    try:
        # TODO: Add actual script logic here.
        # This could be data processing, file conversion, API calls, etc.
        print("Success: Processed the task.")
        return 0
    except Exception as exc:
        print(f"Failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
"""

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

## Structure Suggestions

### API Reference Example
- Overview
- Authentication
- Endpoints with examples
- Error codes

### Workflow Guide Example
- Prerequisites
- Step-by-step instructions
- Best practices
"""


def title_case(name: str) -> str:
    return " ".join(word[:1].upper() + word[1:] for word in name.split("-"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new skill directory from the skill-creator template."
    )
    parser.add_argument("skill_name", help="Skill name, usually in hyphen-case.")
    parser.add_argument("--path", required=True, help="Base directory for the new skill.")
    return parser.parse_args()


def validate_skill_name(skill_name: str) -> str:
    if "/" in skill_name or "\\" in skill_name or Path(skill_name).name != skill_name:
        raise ValueError("Skill name cannot contain path separators.")
    return skill_name


def initialize_skill(skill_name: str, base_path: Path) -> Path:
    skill_dir = base_path / skill_name
    if skill_dir.exists():
        raise FileExistsError(f"Skill directory already exists: {skill_dir}")

    skill_title = title_case(skill_name)
    (skill_dir / "scripts").mkdir(parents=True)
    (skill_dir / "references").mkdir()
    (skill_dir / "assets").mkdir()

    (skill_dir / "SKILL.md").write_text(
        SKILL_TEMPLATE.replace("{skill_name}", skill_name).replace(
            "{skill_title}", skill_title
        ),
        encoding="utf-8",
    )

    example_script_path = skill_dir / "scripts" / "example_script.py"
    example_script_path.write_text(
        EXAMPLE_SCRIPT.replace("{skill_name}", skill_name),
        encoding="utf-8",
    )
    example_script_path.chmod(0o755)

    (skill_dir / "references" / "example_reference.md").write_text(
        EXAMPLE_REFERENCE.replace("{skill_title}", skill_title),
        encoding="utf-8",
    )
    (skill_dir / "assets" / "example_asset.txt").write_text(
        "Placeholder for assets.",
        encoding="utf-8",
    )

    return skill_dir


def main() -> int:
    args = parse_args()
    try:
        skill_name = validate_skill_name(args.skill_name)
        base_path = Path(args.path).expanduser().resolve()
        skill_dir = initialize_skill(skill_name, base_path)
    except (FileExistsError, OSError, ValueError) as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        return 1

    print(f"✅ Skill '{skill_name}' initialized at {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
