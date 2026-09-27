import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  syncTranscriptIndex,
  commitProcessedTranscripts,
  loadTranscriptIndex,
  saveTranscriptIndex,
  findTranscriptsInDirectory,
} from "../src/indexer.ts";
import type { TranscriptIndex } from "../src/types/common.ts";
import { mkdtempSync, rmSync, writeFileSync, existsSync, mkdirSync, symlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

describe("Incremental Transcript Indexer (Rule 2: Incremental Transcript Processing)", () => {
  it("Rule 2.1: unmodified transcript is excluded from processing", () => {
    const transcriptPath = "/path/to/transcript-123.jsonl";
    const currentIndex: TranscriptIndex = {
      version: 1,
      files: {
        [transcriptPath]: 1000,
      },
    };

    const result = syncTranscriptIndex({
      candidatePaths: [transcriptPath],
      index: currentIndex,
      getMtimeMs: (p) => (p === transcriptPath ? 1000 : null),
      fileExists: (p) => p === transcriptPath,
    });

    assert.equal(result.toProcess.includes(transcriptPath), false);
    assert.deepEqual(result.toProcess, []);
    assert.equal(result.updatedIndex.files[transcriptPath], 1000);
  });

  it("Rule 2.2: new or modified transcript is marked for analysis and updated upon completion", () => {
    const unindexedPath = "/path/to/transcript-new.jsonl";
    const modifiedPath = "/path/to/transcript-456.jsonl";

    const currentIndex: TranscriptIndex = {
      version: 1,
      files: {
        [modifiedPath]: 1500,
      },
    };

    const mockMtimes: Record<string, number> = {
      [unindexedPath]: 2000,
      [modifiedPath]: 2500,
    };

    const result = syncTranscriptIndex({
      candidatePaths: [unindexedPath, modifiedPath],
      index: currentIndex,
      getMtimeMs: (p) => mockMtimes[p] ?? null,
      fileExists: (p) => p in mockMtimes,
    });

    assert.equal(result.toProcess.includes(unindexedPath), true);
    assert.equal(result.toProcess.includes(modifiedPath), true);

    // Commit processed transcripts
    const committed = commitProcessedTranscripts(result.updatedIndex, [
      { path: unindexedPath, mtimeMs: 2000 },
      { path: modifiedPath, mtimeMs: 2500 },
    ]);

    assert.equal(committed.files[unindexedPath], 2000);
    assert.equal(committed.files[modifiedPath], 2500);
  });

  it("Rule 2.3: stale indexed file that no longer exists on disk is pruned", () => {
    const activePath = "/path/to/active.jsonl";
    const stalePath = "/path/to/transcript-old.jsonl";

    const currentIndex: TranscriptIndex = {
      version: 1,
      files: {
        [activePath]: 1000,
        [stalePath]: 800,
      },
    };

    const result = syncTranscriptIndex({
      candidatePaths: [activePath],
      index: currentIndex,
      getMtimeMs: (p) => (p === activePath ? 1000 : null),
      fileExists: (p) => p === activePath, // stalePath does not exist
    });

    assert.equal(stalePath in result.updatedIndex.files, false);
    assert.deepEqual(result.prunedPaths, [stalePath]);
    assert.equal(result.updatedIndex.files[activePath], 1000);
  });

  it("loads and saves index to disk correctly", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "indexer-test-"));
    try {
      const indexPath = join(tempDir, "continual-learning-index.json");

      // Non-existent file loads empty index
      const empty = loadTranscriptIndex(indexPath);
      assert.equal(empty.version, 1);
      assert.deepEqual(empty.files, {});

      // Save index
      const toSave: TranscriptIndex = {
        version: 1,
        files: {
          "/work/t1.jsonl": 12345,
        },
      };
      saveTranscriptIndex(indexPath, toSave);
      assert.equal(existsSync(indexPath), true);

      // Load saved index
      const loaded = loadTranscriptIndex(indexPath);
      assert.equal(loaded.version, 1);
      assert.equal(loaded.files["/work/t1.jsonl"], 12345);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  describe("findTranscriptsInDirectory", () => {
    it("returns empty array when directory does not exist", () => {
      const nonExistent = join(tmpdir(), "does-not-exist-" + Date.now());
      assert.deepEqual(findTranscriptsInDirectory(nonExistent), []);
    });

    it("recursively discovers .json and .jsonl files while ignoring other files and ignored directories", () => {
      const tempDir = mkdtempSync(join(tmpdir(), "find-transcripts-"));
      try {
        const subDir = join(tempDir, "sub");
        const nodeModulesDir = join(tempDir, "node_modules");
        mkdirSync(subDir, { recursive: true });
        mkdirSync(nodeModulesDir, { recursive: true });

        const t1 = join(tempDir, "transcript1.jsonl");
        const t2 = join(subDir, "transcript2.json");
        const ignoredTxt = join(tempDir, "notes.txt");
        const ignoredModuleFile = join(nodeModulesDir, "mod.json");

        writeFileSync(t1, "{}", "utf-8");
        writeFileSync(t2, "{}", "utf-8");
        writeFileSync(ignoredTxt, "notes", "utf-8");
        writeFileSync(ignoredModuleFile, "{}", "utf-8");

        const found = findTranscriptsInDirectory(tempDir);
        assert.equal(found.length, 2);
        assert.equal(found.includes(t1), true);
        assert.equal(found.includes(t2), true);
        assert.equal(found.includes(ignoredTxt), false);
        assert.equal(found.includes(ignoredModuleFile), false);
      } finally {
        rmSync(tempDir, { recursive: true, force: true });
      }
    });

    it("prevents circular symlink traversal loops", () => {
      const tempDir = mkdtempSync(join(tmpdir(), "symlink-loop-"));
      try {
        const sub = join(tempDir, "sub");
        mkdirSync(sub, { recursive: true });
        const file = join(sub, "t.jsonl");
        writeFileSync(file, "{}", "utf-8");

        // Create circular symlink: sub/loop -> tempDir
        try {
          symlinkSync(tempDir, join(sub, "loop"));
        } catch {
          // In case symlinks are unsupported in test environment, skip
          return;
        }

        const found = findTranscriptsInDirectory(tempDir);
        assert.equal(found.includes(file), true);
        // Traversal terminates without stack overflow
        assert.equal(found.length >= 1, true);
      } finally {
        rmSync(tempDir, { recursive: true, force: true });
      }
    });
  });
});
