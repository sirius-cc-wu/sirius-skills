import { existsSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import {
  loadTranscriptIndex,
  saveTranscriptIndex,
  syncTranscriptIndex,
  commitProcessedTranscripts,
  findTranscriptsInDirectory,
} from "./indexer.ts";
import { patchAgentsMemory } from "./updater.ts";
import type {
  BulletAdd,
  BulletUpdate,
  ContinuousLearningState,
  PatchResult,
} from "./types/common.ts";

export interface ContinualLearningRunnerOptions {
  indexPath?: string;
  agentsPath?: string;
  statePath?: string;
  candidatePaths?: string[];
  transcriptPath?: string | null;
  transcriptsDir?: string;
  now?: number;
  extractor?: (transcripts: Array<{ path: string; content: string }>) => {
    bulletsToUpdate?: BulletUpdate[];
    bulletsToAdd?: Array<BulletAdd | string>;
  };
  updates?: {
    bulletsToUpdate?: BulletUpdate[];
    bulletsToAdd?: Array<BulletAdd | string>;
  };
}

export interface ContinualLearningRunnerResult {
  success: boolean;
  transcriptsProcessed: string[];
  prunedTranscripts: string[];
  memoryUpdated: boolean;
  indexPath: string;
  agentsPath: string;
  message: string;
  patchResult?: PatchResult;
}

/**
 * Extracts memory updates (bullets to update or add) from transcript contents.
 * Supports structured JSON/JSONL with `bulletsToUpdate` / `bulletsToAdd`,
 * event-based JSON entries, and text heuristics for user corrections and facts.
 */
export function extractUpdatesFromTranscripts(
  transcripts: Array<{ path: string; content: string }>
): {
  bulletsToUpdate: BulletUpdate[];
  bulletsToAdd: BulletAdd[];
} {
  const bulletsToUpdate: BulletUpdate[] = [];
  const bulletsToAdd: BulletAdd[] = [];

  for (const item of transcripts) {
    const content = item.content.trim();
    if (!content) continue;

    // Check if entire content is a single JSON object
    if (content.startsWith("{") && content.endsWith("}")) {
      try {
        const parsed = JSON.parse(content);
        if (Array.isArray(parsed.bulletsToUpdate) || Array.isArray(parsed.bulletsToAdd)) {
          if (Array.isArray(parsed.bulletsToUpdate)) {
            bulletsToUpdate.push(...parsed.bulletsToUpdate);
          }
          if (Array.isArray(parsed.bulletsToAdd)) {
            for (const add of parsed.bulletsToAdd) {
              if (typeof add === "string") {
                bulletsToAdd.push({ category: "Learned Workspace Facts", bullet: add });
              } else if (add && typeof add.bullet === "string") {
                bulletsToAdd.push(add);
              }
            }
          }
          continue;
        }
      } catch {
        // Fall through to line-by-line parsing
      }
    }

    // Line-by-line inspection (supports JSONL and plain text)
    const lines = content.split(/\r?\n/);
    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line) continue;

      let textToInspect = line;

      // If line is JSON, check structured keys or text property
      if (line.startsWith("{") && line.endsWith("}")) {
        try {
          const entry = JSON.parse(line);
          if (Array.isArray(entry.bulletsToUpdate)) {
            bulletsToUpdate.push(...entry.bulletsToUpdate);
          }
          if (Array.isArray(entry.bulletsToAdd)) {
            for (const add of entry.bulletsToAdd) {
              if (typeof add === "string") {
                bulletsToAdd.push({ category: "Learned Workspace Facts", bullet: add });
              } else if (add && typeof add.bullet === "string") {
                bulletsToAdd.push(add);
              }
            }
          }
          if (entry.targetPattern && entry.replacement) {
            bulletsToUpdate.push({
              targetPattern: entry.targetPattern,
              replacement: entry.replacement,
            });
          }
          if (entry.bullet) {
            bulletsToAdd.push({
              category: entry.category,
              bullet: entry.bullet,
            });
          }

          if (typeof entry.content === "string") {
            textToInspect = entry.content;
          } else if (typeof entry.message === "string") {
            textToInspect = entry.message;
          } else if (typeof entry.text === "string") {
            textToInspect = entry.text;
          } else {
            continue;
          }
        } catch {
          textToInspect = line;
        }
      }

      // Check regex heuristics on textToInspect:
      // Pattern A: "replace <target> with <replacement>"
      const replaceMatch = textToInspect.match(
        /^(?:Correction:\s*)?replace\s+["']?([^"']+)["']?\s+with\s+["']?([^"']+)["']?$/i
      );
      if (replaceMatch) {
        bulletsToUpdate.push({
          targetPattern: replaceMatch[1].trim(),
          replacement: replaceMatch[2].trim(),
        });
        continue;
      }

      // Pattern B: Correction indicator: "Correction: <replacement>"
      const correctionMatch = textToInspect.match(/^Correction:\s+(.+)$/i);
      if (correctionMatch) {
        bulletsToAdd.push({
          category: "Learned User Preferences",
          bullet: correctionMatch[1].trim(),
        });
        continue;
      }

      // Pattern C: Preference indicator: "Preference: <text>"
      const prefMatch = textToInspect.match(/^Preference:\s+(.+)$/i);
      if (prefMatch) {
        bulletsToAdd.push({
          category: "Learned User Preferences",
          bullet: prefMatch[1].trim(),
        });
        continue;
      }

      // Pattern D: Categorized fact / rule: "Fact: [Category] <text>" or "Rule: [Category] <text>"
      const factMatch = textToInspect.match(
        /^(?:Fact|Rule|Learned):\s*(?:\[([^\]]+)\]\s*)?(.+)$/i
      );
      if (factMatch) {
        bulletsToAdd.push({
          category: factMatch[1]?.trim() || "Learned Workspace Facts",
          bullet: factMatch[2].trim(),
        });
        continue;
      }
    }
  }

  return { bulletsToUpdate, bulletsToAdd };
}

/**
 * Executes the continual learning loop:
 * 1. Synchronizes transcript index using indexer.ts
 * 2. Extracts memory updates from new/modified transcripts
 * 3. In-place patches AGENTS.md using updater.ts
 * 4. Commits processed transcripts to index file
 * 5. Updates state.lastTranscriptMtimeMs
 */
export function runContinualLearningLoop(
  workspacePath: string,
  state: ContinuousLearningState,
  options?: ContinualLearningRunnerOptions
): ContinualLearningRunnerResult {
  const rootDir = workspacePath || process.cwd();

  // 1. Resolve agentsPath
  const agentsPath = options?.agentsPath ?? resolve(rootDir, "AGENTS.md");

  // 2. Resolve indexPath
  let indexPath = options?.indexPath;
  if (!indexPath) {
    if (options?.statePath) {
      indexPath = resolve(dirname(options.statePath), "continual-learning-index.json");
    } else {
      const rootIndex = resolve(rootDir, "continual-learning-index.json");
      const copilotIndex = resolve(rootDir, ".copilot/state/continual-learning-index.json");
      const geminiIndex = resolve(rootDir, ".gemini/state/continual-learning-index.json");
      if (existsSync(rootIndex)) {
        indexPath = rootIndex;
      } else if (existsSync(copilotIndex)) {
        indexPath = copilotIndex;
      } else if (existsSync(geminiIndex)) {
        indexPath = geminiIndex;
      } else {
        indexPath = copilotIndex;
      }
    }
  }

  // 3. Gather candidate transcript paths
  const candidateSet = new Set<string>();

  if (options?.candidatePaths) {
    for (const p of options.candidatePaths) {
      if (existsSync(p)) candidateSet.add(resolve(p));
    }
  }

  if (options?.transcriptPath && existsSync(options.transcriptPath)) {
    candidateSet.add(resolve(options.transcriptPath));
  }

  // Scan potential transcript directories
  const candidateDirs: string[] = [];
  if (options?.transcriptsDir && existsSync(options.transcriptsDir)) {
    candidateDirs.push(options.transcriptsDir);
  }
  const defaultDirs = [
    resolve(rootDir, ".copilot/transcripts"),
    resolve(rootDir, ".copilot/session-logs"),
    resolve(rootDir, ".gemini/transcripts"),
    resolve(rootDir, "transcripts"),
  ];
  for (const d of defaultDirs) {
    if (existsSync(d)) {
      candidateDirs.push(d);
    }
  }

  for (const dir of candidateDirs) {
    const found = findTranscriptsInDirectory(dir);
    for (const file of found) {
      candidateSet.add(resolve(file));
    }
  }

  const candidatePaths = Array.from(candidateSet);

  // 4. Load & sync index
  const currentIndex = loadTranscriptIndex(indexPath);
  const syncResult = syncTranscriptIndex({
    candidatePaths,
    index: currentIndex,
  });

  const { toProcess, updatedIndex, prunedPaths } = syncResult;

  let memoryUpdated = false;
  let patchResult: PatchResult | undefined;
  const processedFiles: Array<{ path: string; mtimeMs: number }> = [];

  // 5. Process new/modified transcripts
  if (toProcess.length > 0) {
    const transcriptData: Array<{ path: string; content: string }> = [];
    for (const filePath of toProcess) {
      try {
        const content = readFileSync(filePath, "utf-8");
        transcriptData.push({ path: filePath, content });
        const stat = statSync(filePath);
        processedFiles.push({ path: filePath, mtimeMs: stat.mtimeMs });
      } catch {
        // Skip unreadable files
      }
    }

    const updates =
      options?.updates ??
      (options?.extractor
        ? options.extractor(transcriptData)
        : extractUpdatesFromTranscripts(transcriptData));

    const bulletsToUpdate = updates.bulletsToUpdate ?? [];
    const bulletsToAdd = updates.bulletsToAdd ?? [];

    if (bulletsToUpdate.length > 0 || bulletsToAdd.length > 0) {
      patchResult = patchAgentsMemory(agentsPath, {
        bulletsToUpdate,
        bulletsToAdd,
      });
      memoryUpdated = patchResult.modified;
    } else {
      patchResult = {
        modified: false,
        message: "No high-signal memory updates",
      };
    }

    // Commit processed transcript mtimes into index
    const finalIndex = commitProcessedTranscripts(updatedIndex, processedFiles);
    saveTranscriptIndex(indexPath, finalIndex);

    // Update state's lastTranscriptMtimeMs
    if (processedFiles.length > 0) {
      const maxMtime = Math.max(...processedFiles.map((f) => f.mtimeMs));
      state.lastTranscriptMtimeMs = maxMtime;
    }
  } else if (prunedPaths.length > 0) {
    saveTranscriptIndex(indexPath, updatedIndex);
  }

  const message = memoryUpdated
    ? (patchResult?.message ?? "Memory updated successfully")
    : "No high-signal memory updates";

  return {
    success: true,
    transcriptsProcessed: toProcess,
    prunedTranscripts: prunedPaths,
    memoryUpdated,
    indexPath,
    agentsPath,
    message,
    patchResult,
  };
}
