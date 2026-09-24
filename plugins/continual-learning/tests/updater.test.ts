import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { patchAgentsMemory, patchAgentsContent, escapeRegExp } from "../src/updater.ts";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

describe("In-Place AGENTS.md Memory Updater (Rule 3)", () => {
  const SAMPLE_AGENTS_MD = `# Project Guidelines

Here is the introduction.

## Core Rules
- Always run tests before committing
- Always use tabs for indentation in YAML
- Follow standard project conventions

## Other Notes
Some other details here.
`;

  it("Rule 3.1: matching bullet is replaced in-place and surrounding text remains byte-identical", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "updater-test-"));
    try {
      const agentsPath = join(tempDir, "AGENTS.md");
      writeFileSync(agentsPath, SAMPLE_AGENTS_MD, "utf-8");

      const result = patchAgentsMemory(agentsPath, {
        bulletsToUpdate: [
          {
            targetPattern: /use tabs for indentation in YAML/i,
            replacement: "- Always use 2 spaces for indentation in YAML",
          },
        ],
        bulletsToAdd: [],
      });

      assert.equal(result.modified, true);

      const updated = readFileSync(agentsPath, "utf-8");

      // Verify the replaced line is present
      assert.equal(updated.includes("- Always use 2 spaces for indentation in YAML"), true);
      assert.equal(updated.includes("- Always use tabs for indentation in YAML"), false);

      // Verify surrounding text is byte-identical
      const expected = SAMPLE_AGENTS_MD.replace(
        "- Always use tabs for indentation in YAML",
        "- Always use 2 spaces for indentation in YAML"
      );
      assert.equal(updated, expected);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("Rule 3.2: new invariant is appended to existing category without adding redundant headings", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "updater-test-"));
    try {
      const agentsPath = join(tempDir, "AGENTS.md");
      writeFileSync(agentsPath, SAMPLE_AGENTS_MD, "utf-8");

      const result = patchAgentsMemory(agentsPath, {
        bulletsToUpdate: [],
        bulletsToAdd: [
          {
            category: "Core Rules",
            bullet: "- Never commit directly to main branch",
          },
        ],
      });

      assert.equal(result.modified, true);

      const updated = readFileSync(agentsPath, "utf-8");

      // New bullet is in Core Rules
      assert.equal(updated.includes("- Never commit directly to main branch"), true);

      // No redundant headings
      const headingMatches = updated.match(/## Core Rules/g);
      assert.equal(headingMatches?.length, 1);

      // Bullet appears before ## Other Notes
      const coreRulesIdx = updated.indexOf("## Core Rules");
      const bulletIdx = updated.indexOf("- Never commit directly to main branch");
      const otherNotesIdx = updated.indexOf("## Other Notes");

      assert.equal(coreRulesIdx < bulletIdx, true);
      assert.equal(bulletIdx < otherNotesIdx, true);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("Rule 3.3: zero-change returns 'No high-signal memory updates' and leaves file untouched", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "updater-test-"));
    try {
      const agentsPath = join(tempDir, "AGENTS.md");
      writeFileSync(agentsPath, SAMPLE_AGENTS_MD, "utf-8");

      const before = readFileSync(agentsPath, "utf-8");

      const result = patchAgentsMemory(agentsPath, {
        bulletsToUpdate: [],
        bulletsToAdd: [],
      });

      assert.equal(result.modified, false);
      assert.equal(result.message, "No high-signal memory updates");

      const after = readFileSync(agentsPath, "utf-8");
      assert.equal(before, after);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("deduplicates already existing bullets", () => {
    const content = SAMPLE_AGENTS_MD;
    const result = patchAgentsContent(content, {
      bulletsToUpdate: [],
      bulletsToAdd: [
        {
          category: "Core Rules",
          bullet: "- Always run tests before committing", // already exists
        },
      ],
    });

    assert.equal(result.modified, false);
    assert.equal(result.message, "No high-signal memory updates");
  });

  it("creates category heading if category does not yet exist", () => {
    const content = `# Project Guidelines\n\n## Core Rules\n- Rule 1\n`;
    const result = patchAgentsContent(content, {
      bulletsToUpdate: [],
      bulletsToAdd: [
        {
          category: "Learned Workspace Facts",
          bullet: "- The repository uses pnpm for dependency management",
        },
      ],
    });

    assert.equal(result.modified, true);
    assert.equal(result.updatedContent?.includes("## Learned Workspace Facts"), true);
    assert.equal(
      result.updatedContent?.includes("- The repository uses pnpm for dependency management"),
      true
    );
  });

  it("preserves CRLF line endings when present", () => {
    const crlfContent = "# Title\r\n\r\n## Core Rules\r\n- Old rule\r\n";
    const result = patchAgentsContent(crlfContent, {
      bulletsToUpdate: [
        {
          targetPattern: /Old rule/,
          replacement: "- New rule",
        },
      ],
      bulletsToAdd: [],
    });

    assert.equal(result.modified, true);
    assert.equal(result.updatedContent?.includes("\r\n"), true);
    assert.equal(result.updatedContent, "# Title\r\n\r\n## Core Rules\r\n- New rule\r\n");
  });

  it("escapeRegExp escapes all regex metacharacters properly", () => {
    const raw = ".*+?^${}()|[]\\";
    const escaped = escapeRegExp(raw);
    assert.equal(escaped, "\\.\\*\\+\\?\\^\\$\\{\\}\\(\\)\\|\\[\\]\\\\");
  });

  it("handles bullet update with regex metacharacters in targetPattern string safely", () => {
    const content = "# Guidelines\n\n## Core Rules\n- Node.js [v24] + C++ (x86_64) is required\n";
    const result = patchAgentsContent(content, {
      bulletsToUpdate: [
        {
          targetPattern: "Node.js [v24] + C++ (x86_64)",
          replacement: "- Node.js [v24] (LTS) + C++20 is required",
        },
      ],
      bulletsToAdd: [],
    });

    assert.equal(result.modified, true);
    assert.equal(
      result.updatedContent?.includes("- Node.js [v24] (LTS) + C++20 is required"),
      true
    );
  });

  it("handles category heading containing regex metacharacters safely", () => {
    const content = "# Guidelines\n\n## C++ & Node.js [v24]\n- Initial bullet\n";
    const result = patchAgentsContent(content, {
      bulletsToUpdate: [],
      bulletsToAdd: [
        {
          category: "C++ & Node.js [v24]",
          bullet: "- Added bullet with regex metacharacters",
        },
      ],
    });

    assert.equal(result.modified, true);
    assert.equal(
      result.updatedContent?.includes("- Added bullet with regex metacharacters"),
      true
    );
    // Ensure no duplicate heading was created
    const headingMatches = result.updatedContent?.match(/## C\+\+ & Node\.js \[v24\]/g);
    assert.equal(headingMatches?.length, 1);
  });
});
