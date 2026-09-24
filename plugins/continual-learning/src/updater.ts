import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { randomBytes } from "node:crypto";
import type { BulletAdd, BulletUpdate, PatchResult } from "./types/common.ts";

export interface PatchOptions {
  bulletsToUpdate: BulletUpdate[];
  bulletsToAdd: Array<BulletAdd | string>;
}

/**
 * Normalizes bullet string ensuring a leading "- " marker.
 */
function normalizeBullet(raw: string): string {
  const trimmed = raw.trim();
  if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
    return trimmed;
  }
  return `- ${trimmed}`;
}

/**
 * Extracts bullet text without marker for deduplication checks.
 */
function extractBulletText(bullet: string): string {
  return bullet.replace(/^[-*]\s+/, "").trim();
}

/**
 * Escapes regex metacharacters in a string to prevent ReDoS and syntax errors.
 */
export function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Pure surgical memory update logic on string content.
 * Guarantees that unrelated sections, headers, and comments remain byte-identical.
 */
export function patchAgentsContent(
  content: string,
  options: PatchOptions
): PatchResult {
  const isCrlf = content.includes("\r\n");
  const newline = isCrlf ? "\r\n" : "\n";

  let lines = content.split(/\r?\n/);
  // Track trailing newline if original content ended with one
  const hasTrailingNewline = content.endsWith("\n");
  if (hasTrailingNewline && lines[lines.length - 1] === "") {
    lines.pop();
  }

  let modified = false;

  // 1. In-place bullet updates
  for (const update of options.bulletsToUpdate) {
    const pattern =
      typeof update.targetPattern === "string"
        ? new RegExp(escapeRegExp(update.targetPattern), "i")
        : update.targetPattern;

    for (let i = 0; i < lines.length; i++) {
      if (pattern.test(lines[i])) {
        // Detect indentation of target line
        const indentMatch = lines[i].match(/^(\s*)/);
        const indent = indentMatch ? indentMatch[1] : "";
        const formattedReplacement = `${indent}${normalizeBullet(update.replacement)}`;

        if (lines[i] !== formattedReplacement) {
          lines[i] = formattedReplacement;
          modified = true;
        }
        break; // Replace first matching bullet
      }
    }
  }

  // 2. Surgical bullet additions to category
  for (const item of options.bulletsToAdd) {
    const category =
      typeof item === "string" ? "Learned Workspace Facts" : (item.category ?? "Learned Workspace Facts");
    const rawBullet = typeof item === "string" ? item : item.bullet;
    const formattedBullet = normalizeBullet(rawBullet);
    const bulletText = extractBulletText(formattedBullet);

    // Deduplication check: check if file content already contains this bullet
    const alreadyExists = lines.some((line) => {
      const lineText = extractBulletText(line);
      return lineText === bulletText && (line.trim().startsWith("-") || line.trim().startsWith("*"));
    });

    if (alreadyExists) {
      continue;
    }

    // Locate category heading: e.g. "## Core Rules"
    const headingRegex = new RegExp(`^#{1,6}\\s+${escapeRegExp(category.trim())}\\s*$`, "i");
    const headingIndex = lines.findIndex((line) => headingRegex.test(line));

    if (headingIndex !== -1) {
      // Find insertion point: end of category section (before next heading or at end of lines)
      let nextHeadingIndex = -1;
      for (let i = headingIndex + 1; i < lines.length; i++) {
        if (/^#{1,6}\s+/.test(lines[i])) {
          nextHeadingIndex = i;
          break;
        }
      }

      const searchEnd = nextHeadingIndex !== -1 ? nextHeadingIndex : lines.length;

      // Find the last bullet or non-empty line in this section
      let insertIndex = searchEnd;
      // If there is an empty line before next heading, insert before trailing blank line
      let lastContentIndex = headingIndex;
      for (let i = searchEnd - 1; i > headingIndex; i--) {
        if (lines[i].trim().length > 0) {
          lastContentIndex = i;
          break;
        }
      }

      insertIndex = lastContentIndex + 1;
      lines.splice(insertIndex, 0, formattedBullet);
      modified = true;
    } else {
      // Heading does not exist; append new category heading and bullet
      if (lines.length > 0 && lines[lines.length - 1].trim() !== "") {
        lines.push("");
      }
      lines.push(`## ${category}`);
      lines.push(formattedBullet);
      modified = true;
    }
  }

  if (!modified) {
    return {
      modified: false,
      message: "No high-signal memory updates",
    };
  }

  let updatedContent = lines.join(newline);
  if (hasTrailingNewline) {
    updatedContent += newline;
  }

  return {
    modified: true,
    message: "Memory updated successfully",
    updatedContent,
  };
}

/**
 * In-place memory patcher reading and writing AGENTS.md according to Rule 3.
 */
export function patchAgentsMemory(
  agentsPath: string,
  options: PatchOptions
): PatchResult {
  let content = "";
  if (existsSync(agentsPath)) {
    content = readFileSync(agentsPath, "utf-8");
  } else {
    // If AGENTS.md doesn't exist, create initial scaffolding
    content = `# AGENTS.md\n\n## Learned User Preferences\n\n## Learned Workspace Facts\n`;
  }

  const result = patchAgentsContent(content, options);

  if (!result.modified || !result.updatedContent) {
    return result;
  }

  // Atomic write via temp file
  const dir = dirname(agentsPath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }

  const tempPath = join(
    dir,
    `.AGENTS.md.tmp.${randomBytes(6).toString("hex")}`
  );
  writeFileSync(tempPath, result.updatedContent, "utf-8");
  renameSync(tempPath, agentsPath);

  return result;
}
