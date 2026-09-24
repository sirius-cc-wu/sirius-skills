import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  runContinualLearningLoop,
  extractUpdatesFromTranscripts,
} from "../src/runner.ts";
import { INITIAL_STATE } from "../src/types/common.ts";
import { mkdtempSync, readFileSync, rmSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

describe("Continual Learning Runner (src/runner.ts)", () => {
  const INITIAL_AGENTS_MD = `# Project Guidelines

## Core Rules
- Always use tabs for indentation in YAML
- Run linter before commit
`;

  it("extractUpdatesFromTranscripts parses structured JSON updates", () => {
    const raw = JSON.stringify({
      bulletsToUpdate: [
        { targetPattern: "tabs", replacement: "- Always use 2 spaces" },
      ],
      bulletsToAdd: [
        { category: "Core Rules", bullet: "- Do not force push to main" },
      ],
    });

    const res = extractUpdatesFromTranscripts([{ path: "test.json", content: raw }]);
    assert.equal(res.bulletsToUpdate.length, 1);
    assert.equal(res.bulletsToUpdate[0].targetPattern, "tabs");
    assert.equal(res.bulletsToAdd.length, 1);
    assert.equal(res.bulletsToAdd[0].bullet, "- Do not force push to main");
  });

  it("extractUpdatesFromTranscripts parses heuristic text corrections and facts", () => {
    const content = `
Correction: replace "tabs" with "- Always use 2 spaces"
Preference: Never write console.log in production
Fact: [Architecture] Uses SQLite for persistence
`;
    const res = extractUpdatesFromTranscripts([{ path: "chat.log", content }]);
    assert.equal(res.bulletsToUpdate.length, 1);
    assert.equal(res.bulletsToUpdate[0].targetPattern, "tabs");
    assert.equal(res.bulletsToAdd.length, 2);
    assert.equal(res.bulletsToAdd[0].bullet, "Never write console.log in production");
    assert.equal(res.bulletsToAdd[1].category, "Architecture");
    assert.equal(res.bulletsToAdd[1].bullet, "Uses SQLite for persistence");
  });

  it("executes continual learning loop, updates index and AGENTS.md, and advances state", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "runner-test-"));
    try {
      const agentsPath = join(tempDir, "AGENTS.md");
      const indexPath = join(tempDir, "continual-learning-index.json");
      writeFileSync(agentsPath, INITIAL_AGENTS_MD, "utf-8");

      // Create transcript directory and file
      const transcriptsDir = join(tempDir, "transcripts");
      mkdirSync(transcriptsDir, { recursive: true });
      const transcriptFile = join(transcriptsDir, "session-1.jsonl");

      const updateData = JSON.stringify({
        bulletsToUpdate: [
          {
            targetPattern: "use tabs for indentation in YAML",
            replacement: "- Always use 2 spaces for indentation in YAML",
          },
        ],
        bulletsToAdd: [
          {
            category: "Core Rules",
            bullet: "- Never push directly to main branch",
          },
        ],
      });
      writeFileSync(transcriptFile, `${updateData}\n`, "utf-8");

      const state = { ...INITIAL_STATE };

      const result = runContinualLearningLoop(tempDir, state, {
        agentsPath,
        indexPath,
        transcriptsDir,
      });

      assert.equal(result.success, true);
      assert.equal(result.memoryUpdated, true);
      assert.equal(result.transcriptsProcessed.includes(transcriptFile), true);

      // Check AGENTS.md was patched on disk
      const updatedAgents = readFileSync(agentsPath, "utf-8");
      assert.equal(
        updatedAgents.includes("- Always use 2 spaces for indentation in YAML"),
        true
      );
      assert.equal(
        updatedAgents.includes("- Always use tabs for indentation in YAML"),
        false
      );
      assert.equal(
        updatedAgents.includes("- Never push directly to main branch"),
        true
      );

      // Check continual-learning-index.json was saved on disk
      assert.equal(existsSync(indexPath), true);
      const savedIndex = JSON.parse(readFileSync(indexPath, "utf-8"));
      assert.equal(typeof savedIndex.files[transcriptFile], "number");

      // Check state.lastTranscriptMtimeMs was updated
      assert.equal(typeof state.lastTranscriptMtimeMs, "number");
      assert.equal((state.lastTranscriptMtimeMs ?? 0) > 0, true);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("handles transcripts with no updates without modifying AGENTS.md, but updating index", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "runner-noop-"));
    try {
      const agentsPath = join(tempDir, "AGENTS.md");
      const indexPath = join(tempDir, "continual-learning-index.json");
      writeFileSync(agentsPath, INITIAL_AGENTS_MD, "utf-8");

      const transcriptFile = join(tempDir, "chat.jsonl");
      writeFileSync(transcriptFile, '{"role": "user", "content": "Hello world"}\n', "utf-8");

      const state = { ...INITIAL_STATE };

      const result = runContinualLearningLoop(tempDir, state, {
        agentsPath,
        indexPath,
        candidatePaths: [transcriptFile],
      });

      assert.equal(result.success, true);
      assert.equal(result.memoryUpdated, false);
      assert.equal(result.message, "No high-signal memory updates");

      // AGENTS.md is unchanged
      const agentsContent = readFileSync(agentsPath, "utf-8");
      assert.equal(agentsContent, INITIAL_AGENTS_MD);

      // But index is recorded
      assert.equal(existsSync(indexPath), true);
      const savedIndex = JSON.parse(readFileSync(indexPath, "utf-8"));
      assert.equal(typeof savedIndex.files[transcriptFile], "number");
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
