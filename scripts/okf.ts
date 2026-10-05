#!/usr/bin/env bun
/**
 * Open Knowledge Format (OKF v0.2) utility for systems engineering artifacts across repositories.
 *
 * Capabilities:
 * - Validates OKF frontmatter compliance across docs/
 * - Evaluates trust tiers (unverified, machine-confirmed, human-reviewed)
 * - Generates progressive disclosure index.md files for agents and humans
 * - Displays corpus statistics and verification coverage
 */

import { readdir, readFile, writeFile, stat } from "node:fs/promises";
import { join, relative, basename, dirname, resolve } from "node:path";

export interface OkfActor {
  by: string;
  at?: string;
}

export interface OkfSource {
  id?: string;
  resource?: string;
  title?: string;
  last_modified?: string;
}

export interface OkfFrontmatter {
  type?: string;
  title?: string;
  description?: string;
  status?: string;
  id?: string;
  date?: string;
  tags?: string[];
  generated?: OkfActor;
  verified?: OkfActor | OkfActor[];
  sources?: (string | OkfSource)[];
  stale_after?: string;
  supersedes?: string;
  superseded_by?: string;
  okf_version?: string;
  [key: string]: unknown;
}

export interface ConceptDocument {
  filePath: string;
  relativePath: string;
  frontmatter: OkfFrontmatter;
  rawContent: string;
  body: string;
}

export interface ValidationIssue {
  filePath: string;
  field: string;
  message: string;
  severity: "error" | "warning";
}

export type TrustTier = "unverified" | "machine-confirmed" | "human-reviewed";

export const ALLOWED_STATUSES = new Set([
  "draft",
  "proposed",
  "accepted",
  "stable",
  "superseded",
  "deprecated",
  "completed",
  "implemented",
]);

export const ACTOR_PATTERN = /^(human:[a-zA-Z0-9_.-]+|[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+|process:[a-zA-Z0-9_.-]+)$/;
export const ISO_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$/;

/**
 * Extracts frontmatter and body from markdown content.
 */
export function parseFrontmatter(rawContent: string): { frontmatter: OkfFrontmatter | null; body: string } {
  const match = rawContent.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) {
    return { frontmatter: null, body: rawContent };
  }

  try {
    const parsed = Bun.YAML.parse(match[1]);
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      return { frontmatter: null, body: rawContent };
    }
    return { frontmatter: parsed as OkfFrontmatter, body: match[2] };
  } catch {
    return { frontmatter: null, body: rawContent };
  }
}

/**
 * Validates an actor string adhering to OKF v0.2 conventions:
 * - human:<id>
 * - <producer>/<model>
 * - process:<id>
 */
export function isValidActor(actor: string): boolean {
  if (typeof actor !== "string" || !actor.trim()) return false;
  return ACTOR_PATTERN.test(actor.trim());
}

/**
 * Computes the trust tier of an OKF concept document.
 */
export function getTrustTier(frontmatter: OkfFrontmatter): TrustTier {
  if (!frontmatter.verified || frontmatter.status === "draft") {
    return "unverified";
  }

  const verifications = Array.isArray(frontmatter.verified)
    ? frontmatter.verified
    : [frontmatter.verified];

  if (verifications.length === 0) {
    return "unverified";
  }

  // If any verifier is a human, it qualifies as human-reviewed
  for (const v of verifications) {
    if (v && typeof v.by === "string" && v.by.startsWith("human:")) {
      return "human-reviewed";
    }
  }

  return "machine-confirmed";
}

/**
 * Validates a single concept document against OKF v0.2 invariants.
 */
export function validateConcept(filePath: string, frontmatter: OkfFrontmatter | null): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  if (!frontmatter) {
    issues.push({
      filePath,
      field: "frontmatter",
      message: "Missing or unparseable YAML frontmatter",
      severity: "error",
    });
    return issues;
  }

  // Required: type
  if (!frontmatter.type || typeof frontmatter.type !== "string" || !frontmatter.type.trim()) {
    issues.push({
      filePath,
      field: "type",
      message: "Missing required frontmatter field 'type'",
      severity: "error",
    });
  }

  // Required: status
  if (!frontmatter.status || typeof frontmatter.status !== "string") {
    issues.push({
      filePath,
      field: "status",
      message: "Missing required frontmatter field 'status'",
      severity: "error",
    });
  } else if (!ALLOWED_STATUSES.has(frontmatter.status.toLowerCase())) {
    issues.push({
      filePath,
      field: "status",
      message: `Invalid status '${frontmatter.status}'. Must be one of: ${Array.from(ALLOWED_STATUSES).join(", ")}`,
      severity: "error",
    });
  }

  // Recommended: title
  if (!frontmatter.title || typeof frontmatter.title !== "string" || !frontmatter.title.trim()) {
    issues.push({
      filePath,
      field: "title",
      message: "Missing recommended frontmatter field 'title'",
      severity: "warning",
    });
  }

  // Recommended: description (crucial for progressive disclosure in index.md)
  if (!frontmatter.description || typeof frontmatter.description !== "string" || !frontmatter.description.trim()) {
    issues.push({
      filePath,
      field: "description",
      message: "Missing recommended frontmatter field 'description' (needed for index.md summary)",
      severity: "warning",
    });
  }

  // Date format checks
  if (frontmatter.date && !ISO_DATE_PATTERN.test(String(frontmatter.date))) {
    issues.push({
      filePath,
      field: "date",
      message: `Invalid date format '${frontmatter.date}'. Must be ISO-8601 (YYYY-MM-DD or full timestamp)`,
      severity: "error",
    });
  }

  if (frontmatter.stale_after && !ISO_DATE_PATTERN.test(String(frontmatter.stale_after))) {
    issues.push({
      filePath,
      field: "stale_after",
      message: `Invalid stale_after format '${frontmatter.stale_after}'. Must be ISO-8601`,
      severity: "error",
    });
  }

  // Generated validation
  if (frontmatter.generated) {
    if (typeof frontmatter.generated !== "object") {
      issues.push({
        filePath,
        field: "generated",
        message: "'generated' must be an object with 'by' and optional 'at'",
        severity: "error",
      });
    } else {
      if (!frontmatter.generated.by || !isValidActor(frontmatter.generated.by)) {
        issues.push({
          filePath,
          field: "generated.by",
          message: `Invalid actor format '${frontmatter.generated.by}'. Expected human:<id>, <producer>/<model>, or process:<id>`,
          severity: "error",
        });
      }
      if (frontmatter.generated.at && !ISO_DATE_PATTERN.test(String(frontmatter.generated.at))) {
        issues.push({
          filePath,
          field: "generated.at",
          message: `Invalid timestamp '${frontmatter.generated.at}' in generated.at`,
          severity: "error",
        });
      }
    }
  }

  // Verified validation
  if (frontmatter.verified) {
    const list = Array.isArray(frontmatter.verified) ? frontmatter.verified : [frontmatter.verified];
    for (const v of list) {
      if (typeof v !== "object" || v === null) {
        issues.push({
          filePath,
          field: "verified",
          message: "Verification entry must be an object with 'by' and optional 'at'",
          severity: "error",
        });
      } else {
        if (!v.by || !isValidActor(v.by)) {
          issues.push({
            filePath,
            field: "verified.by",
            message: `Invalid actor format '${v.by}'. Expected human:<id>, <producer>/<model>, or process:<id>`,
            severity: "error",
          });
        }
        if (v.at && !ISO_DATE_PATTERN.test(String(v.at))) {
          issues.push({
            filePath,
            field: "verified.at",
            message: `Invalid timestamp '${v.at}' in verified.at`,
            severity: "error",
          });
        }
      }
    }
  }

  // Invariant: superseded status should point to successor
  if ((frontmatter.status === "superseded" || frontmatter.status === "deprecated") && !frontmatter.superseded_by) {
    issues.push({
      filePath,
      field: "superseded_by",
      message: `Document has status '${frontmatter.status}' but does not specify 'superseded_by'`,
      severity: "warning",
    });
  }

  return issues;
}

/**
 * Scans a directory recursively for markdown concept documents (skipping README.md and index.md).
 */
export async function scanConcepts(dirPath: string): Promise<ConceptDocument[]> {
  const documents: ConceptDocument[] = [];

  async function walk(currentDir: string) {
    let entries;
    try {
      entries = await readdir(currentDir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      const fullPath = join(currentDir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
        await walk(fullPath);
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        const lower = entry.name.toLowerCase();
        // Skip README and index when gathering primary concept items
        if (lower === "readme.md" || lower === "index.md") continue;

        const rawContent = await readFile(fullPath, "utf-8");
        const { frontmatter, body } = parseFrontmatter(rawContent);
        if (frontmatter) {
          documents.push({
            filePath: fullPath,
            relativePath: relative(dirPath, fullPath),
            frontmatter,
            rawContent,
            body,
          });
        }
      }
    }
  }

  await walk(dirPath);
  return documents;
}

/**
 * Generates an index.md file for a stage directory using OKF progressive disclosure.
 */
export function formatStageIndex(
  stageName: string,
  stageDescription: string,
  concepts: ConceptDocument[],
  stageRelPath: string = "."
): string {
  const header = `---
okf_version: "0.2"
title: "${stageName}"
description: "${stageDescription}"
---

# ${stageName}

${stageDescription}

## Concepts

`;

  if (concepts.length === 0) {
    return header + "_No active concept documents recorded in this stage._\n";
  }

  // Sort concepts by id or title or relativePath
  const sorted = [...concepts].sort((a, b) => {
    const idA = a.frontmatter.id || a.frontmatter.title || a.relativePath;
    const idB = b.frontmatter.id || b.frontmatter.title || b.relativePath;
    return idA.localeCompare(idB);
  });

  const lines = sorted.map((doc) => {
    const title = doc.frontmatter.title || doc.frontmatter.id || basename(doc.filePath, ".md");
    const desc = doc.frontmatter.description || "No description provided.";
    const status = doc.frontmatter.status || "draft";
    const tier = getTrustTier(doc.frontmatter);
    const fileName = basename(doc.filePath);
    return `* [${title}](${fileName}) - ${desc} \`[${status} | ${tier}]\``;
  });

  return header + lines.join("\n") + "\n";
}

/**
 * Formats a display-friendly bundle name from raw name.
 */
export function formatBundleName(raw: string): string {
  if (!raw || raw === ".") return "Knowledge Bundle";
  if (raw.toLowerCase() === "foxpilot") return "FoxPilot";
  if (raw.toLowerCase() === "thinker") return "Thinker";
  return raw.charAt(0).toUpperCase() + raw.slice(1);
}

/**
 * Generates the master root docs/index.md for the entire knowledge bundle.
 */
export function formatMasterIndex(
  stages: { name: string; dir: string; desc: string; count: number }[],
  bundleName: string = "Knowledge Bundle"
): string {
  const displayTitle = bundleName === "Knowledge Bundle"
    ? "Systems Engineering Knowledge Bundle"
    : `${bundleName} Systems Engineering Knowledge Bundle`;

  const lines = [
    `---`,
    `okf_version: "0.2"`,
    `title: "${displayTitle}"`,
    `description: "Authoritative requirements, behavioral contracts, architecture decisions, and qualification records for ${bundleName}."`,
    `---`,
    ``,
    `# ${bundleName} Knowledge Bundle (OKF v0.2)`,
    ``,
    `This directory contains the authoritative 5-stage systems engineering artifacts for ${bundleName}, structured according to Google Cloud's [Open Knowledge Format (OKF v0.2)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).`,
    ``,
    `## Progressive Disclosure & Navigation`,
    ``,
    `To minimize cognitive load and conserve AI agent context windows, explore stage directories via their \`index.md\` catalogs before reading full specifications:`,
    ``,
  ];

  for (const stage of stages) {
    lines.push(`* [**${stage.name}**](${stage.dir}/index.md) (${stage.count} concepts) - ${stage.desc}`);
  }

  lines.push(``);
  lines.push(`## Trust Tiers`);
  lines.push(`* **Human-Reviewed**: Explicitly signed off by a human authority (\`human:<id>\`).`);
  lines.push(`* **Machine-Confirmed**: Verified by automated test suites or compiler receipts (\`process:<id>\`).`);
  lines.push(`* **Unverified**: Draft proposals or specifications pending verification.`);
  lines.push(``);

  return lines.join("\n");
}

/**
 * Main execution dispatcher for CLI.
 */
async function main() {
  const rawArgs = process.argv.slice(2);
  let bundleOverride: string | null = null;
  const filteredArgs: string[] = [];

  for (let i = 0; i < rawArgs.length; i++) {
    if (rawArgs[i] === "--bundle" || rawArgs[i] === "-b") {
      bundleOverride = rawArgs[++i] || null;
    } else {
      filteredArgs.push(rawArgs[i]);
    }
  }

  const command = filteredArgs[0] || "help";
  const targetDir = filteredArgs[1] || "docs";

  const resolvedTarget = resolve(targetDir);
  const parentDir = dirname(resolvedTarget);
  const rawBundleName = basename(resolvedTarget) === "docs" ? basename(parentDir) : basename(resolvedTarget);
  const bundleName = bundleOverride || formatBundleName(rawBundleName);

  if (command === "validate") {
    const concepts = await scanConcepts(targetDir);
    let totalErrors = 0;
    let totalWarnings = 0;

    console.log(`Auditing ${concepts.length} concept documents in '${targetDir}' for OKF compliance...\n`);

    for (const doc of concepts) {
      const issues = validateConcept(doc.filePath, doc.frontmatter);
      const errors = issues.filter((i) => i.severity === "error");
      const warnings = issues.filter((i) => i.severity === "warning");

      if (errors.length > 0 || warnings.length > 0) {
        console.log(`📄 ${doc.relativePath}:`);
        for (const issue of errors) {
          console.log(`   ❌ [${issue.field}]: ${issue.message}`);
          totalErrors++;
        }
        for (const issue of warnings) {
          console.log(`   ⚠️  [${issue.field}]: ${issue.message}`);
          totalWarnings++;
        }
      }
    }

    console.log(`\nOKF Validation Summary: ${concepts.length} checked, ${totalErrors} errors, ${totalWarnings} warnings.`);
    if (totalErrors > 0) {
      process.exit(1);
    }
  } else if (command === "index") {
    console.log(`Updating OKF progressive disclosure indexes in '${targetDir}' for ${bundleName}...`);

    const stageConfigs = [
      {
        dir: "requirements",
        name: "Stage 1: Requirements (Problem Space)",
        desc: "User journeys, problem statements, and Example Mapping business rules.",
      },
      {
        dir: "contracts",
        name: "Stage 2: Contracts (External Boundary)",
        desc: "System Sequence Diagrams (SSDs) and normative operation contracts.",
      },
      {
        dir: "architecture",
        name: "Stage 3: Architecture (Solution Space)",
        desc: "Component layering, crate boundaries, and domain models.",
      },
      {
        dir: "decisions",
        name: "Stage 3 Decisions: Architecture Decision Records",
        desc: "Upfront binding architectural law, invariants, and accepted trade-offs.",
      },
      {
        dir: "execution",
        name: "Stage 4: Execution (Work Decomposition & Plans)",
        desc: "Vertical TDD slice plans, runbooks, and implementation tasks.",
      },
      {
        dir: "verification",
        name: "Stage 5: Verification (Quality & Audit)",
        desc: "Formal specification qualification audits and binding verdicts.",
      },
    ];

    const stageStats: { name: string; dir: string; desc: string; count: number }[] = [];

    for (const stage of stageConfigs) {
      const fullStageDir = join(targetDir, stage.dir);
      try {
        await stat(fullStageDir);
      } catch {
        continue;
      }

      const concepts = await scanConcepts(fullStageDir);
      const indexContent = formatStageIndex(stage.name, stage.desc, concepts, stage.dir);
      const indexPath = join(fullStageDir, "index.md");
      await writeFile(indexPath, indexContent, "utf-8");
      console.log(`  ✓ Generated ${indexPath} (${concepts.length} concepts)`);

      stageStats.push({
        name: stage.name,
        dir: stage.dir,
        desc: stage.desc,
        count: concepts.length,
      });
    }

    // Generate root docs/index.md
    const masterIndexContent = formatMasterIndex(stageStats, bundleName);
    const masterIndexPath = join(targetDir, "index.md");
    await writeFile(masterIndexPath, masterIndexContent, "utf-8");
    console.log(`  ✓ Generated master index at ${masterIndexPath}`);
    console.log(`\nOKF indexing complete.`);
  } else if (command === "stats") {
    const concepts = await scanConcepts(targetDir);
    const byType = new Map<string, number>();
    const byStatus = new Map<string, number>();
    const byTrust = new Map<string, number>();

    for (const doc of concepts) {
      const type = doc.frontmatter.type || "unknown";
      const status = doc.frontmatter.status || "draft";
      const trust = getTrustTier(doc.frontmatter);

      byType.set(type, (byType.get(type) || 0) + 1);
      byStatus.set(status, (byStatus.get(status) || 0) + 1);
      byTrust.set(trust, (byTrust.get(trust) || 0) + 1);
    }

    console.log(`\n${bundleName} OKF Knowledge Corpus Statistics (${concepts.length} total concepts):`);
    console.log(`\nBy Concept Type:`);
    for (const [type, count] of byType.entries()) {
      console.log(`  - ${type}: ${count}`);
    }
    console.log(`\nBy Lifecycle Status:`);
    for (const [status, count] of byStatus.entries()) {
      console.log(`  - ${status}: ${count}`);
    }
    console.log(`\nBy Trust Tier:`);
    for (const [trust, count] of byTrust.entries()) {
      console.log(`  - ${trust}: ${count}`);
    }
    console.log();
  } else {
    console.log(`Usage: bun scripts/okf.ts <command> [dir] [options]

Commands:
  validate [dir]   Validate OKF frontmatter compliance across documents (default: docs)
  index [dir]      Generate/update progressive disclosure index.md files (default: docs)
  stats [dir]      Display concept types, lifecycle status, and trust tier metrics
  help             Show this help message

Options:
  -b, --bundle <name>  Override the knowledge bundle display name (e.g. "Thinker")
`);
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.error("Fatal error:", err);
    process.exit(1);
  });
}
