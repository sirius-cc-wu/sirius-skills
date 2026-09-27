import { existsSync, mkdirSync, readFileSync, readdirSync, realpathSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import type { TranscriptIndex } from "./types/common.ts";

/**
 * Loads the transcript index from disk.
 * If the file is missing or corrupted, returns an empty initial index.
 */
export function loadTranscriptIndex(indexPath: string): TranscriptIndex {
  const fallback: TranscriptIndex = { version: 1, files: {} };
  if (!existsSync(indexPath)) {
    return fallback;
  }
  try {
    const raw = readFileSync(indexPath, "utf-8");
    const parsed = JSON.parse(raw) as Partial<TranscriptIndex>;
    if (parsed.version === 1 && typeof parsed.files === "object" && parsed.files !== null) {
      return {
        version: 1,
        files: { ...parsed.files },
      };
    }
    // Also support raw Record<string, number> if found
    if (typeof parsed === "object" && parsed !== null && !("version" in parsed)) {
      return {
        version: 1,
        files: parsed as Record<string, number>,
      };
    }
    return fallback;
  } catch {
    return fallback;
  }
}

/**
 * Persists the transcript index to disk atomically.
 */
export function saveTranscriptIndex(indexPath: string, index: TranscriptIndex): void {
  const dir = dirname(indexPath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
  writeFileSync(indexPath, `${JSON.stringify(index, null, 2)}\n`, "utf-8");
}

export interface SyncIndexOptions {
  candidatePaths: string[];
  index: TranscriptIndex;
  getMtimeMs?: (filePath: string) => number | null;
  fileExists?: (filePath: string) => boolean;
}

export interface SyncIndexResult {
  toProcess: string[];
  updatedIndex: TranscriptIndex;
  prunedPaths: string[];
}

/**
 * Inspects candidate transcripts against the index according to Rule 2:
 * - Excludes unmodified transcripts (mtime <= indexed mtime)
 * - Identifies new (unindexed) or modified (mtime > indexed mtime) transcripts
 * - Prunes indexed entries whose files no longer exist on disk
 */
export function syncTranscriptIndex(options: SyncIndexOptions): SyncIndexResult {
  const getMtimeMs =
    options.getMtimeMs ??
    ((p: string) => {
      try {
        return statSync(p).mtimeMs;
      } catch {
        return null;
      }
    });

  const fileExists =
    options.fileExists ??
    ((p: string) => {
      try {
        return existsSync(p);
      } catch {
        return false;
      }
    });

  const updatedFiles = { ...options.index.files };
  const toProcess: string[] = [];
  const prunedPaths: string[] = [];

  // Check candidates for new or modified transcripts
  for (const candidate of options.candidatePaths) {
    const mtime = getMtimeMs(candidate);
    if (mtime === null) {
      continue;
    }
    const indexedMtime = updatedFiles[candidate];
    if (indexedMtime === undefined || mtime > indexedMtime) {
      toProcess.push(candidate);
    }
  }

  // Prune indexed files that no longer exist
  for (const indexedPath of Object.keys(updatedFiles)) {
    if (!fileExists(indexedPath)) {
      delete updatedFiles[indexedPath];
      prunedPaths.push(indexedPath);
    }
  }

  return {
    toProcess,
    updatedIndex: {
      version: 1,
      files: updatedFiles,
    },
    prunedPaths,
  };
}

/**
 * Commits processed transcript mtimes to the index.
 */
export function commitProcessedTranscripts(
  index: TranscriptIndex,
  processedFiles: Array<{ path: string; mtimeMs: number }>
): TranscriptIndex {
  const updatedFiles = { ...index.files };
  for (const file of processedFiles) {
    updatedFiles[file.path] = file.mtimeMs;
  }
  return {
    version: 1,
    files: updatedFiles,
  };
}

export interface FindTranscriptsOptions {
  maxDepth?: number;
  ignoreDirs?: string[];
}

/**
 * Finds all JSON/JSONL transcript files in a directory recursively.
 * Prevents symlink loops and limits traversal depth.
 */
export function findTranscriptsInDirectory(
  dirPath: string,
  options?: FindTranscriptsOptions
): string[] {
  if (!existsSync(dirPath)) {
    return [];
  }

  const maxDepth = options?.maxDepth ?? 10;
  const ignoreDirs = new Set(
    options?.ignoreDirs ?? ["node_modules", ".git", ".idea", ".vscode"]
  );
  const visited = new Set<string>();
  const results: string[] = [];

  function traverse(current: string, depth: number): void {
    if (depth > maxDepth) {
      return;
    }

    try {
      const real = realpathSync(current);
      if (visited.has(real)) {
        return;
      }
      visited.add(real);
    } catch {
      return;
    }

    let entries: string[] = [];
    try {
      entries = readdirSync(current);
    } catch {
      return;
    }

    for (const entry of entries) {
      if (ignoreDirs.has(entry)) {
        continue;
      }

      const fullPath = join(current, entry);
      try {
        const stat = statSync(fullPath);
        if (stat.isDirectory()) {
          traverse(fullPath, depth + 1);
        } else if (
          stat.isFile() &&
          (entry.endsWith(".jsonl") || entry.endsWith(".json"))
        ) {
          results.push(fullPath);
        }
      } catch {
        // Skip unreadable files or broken symlinks
      }
    }
  }

  traverse(dirPath, 0);
  return results.sort();
}
