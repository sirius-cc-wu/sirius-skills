import type { ExtensionAPI, ExtensionContext, Theme } from "@earendil-works/pi-coding-agent";
import {
	Editor,
	type EditorTheme,
	Key,
	matchesKey,
	Text,
	truncateToWidth,
	visibleWidth,
	wrapTextWithAnsi,
	type Component,
	type TUI,
} from "@earendil-works/pi-tui";
import { Type, type Static } from "typebox";

const VERDICTS = ["In vision", "Off mission", "Conditional"] as const;
type Verdict = (typeof VERDICTS)[number];

const ReviewCardSchema = Type.Object({
	id: Type.String({ minLength: 1, description: "Stable hypothetical identifier" }),
	title: Type.String({ minLength: 1, description: "Short hypothetical title" }),
	proposal: Type.String({ minLength: 1, description: "Concrete change proposal" }),
	tests: Type.String({ minLength: 1, description: "Vision principle or boundary being tested" }),
	why: Type.String({ minLength: 1, description: "Why both answers are defensible" }),
});

type ReviewCard = Static<typeof ReviewCardSchema>;

const VisionReviewParamsSchema = Type.Object({
	project: Type.String({ minLength: 1, description: "Repository or project name" }),
	draft: Type.String({ minLength: 1, description: "Complete current VISION.md draft" }),
	cards: Type.Array(ReviewCardSchema, {
		minItems: 1,
		maxItems: 12,
		description: "Fault-line hypotheticals to present to the author",
	}),
});

type VisionReviewParams = Static<typeof VisionReviewParamsSchema>;

const VisionApprovalParamsSchema = Type.Object({
	project: Type.String({ minLength: 1, description: "Repository or project name" }),
	draft: Type.String({ minLength: 1, description: "Complete candidate VISION.md text" }),
});

type VisionApprovalParams = Static<typeof VisionApprovalParamsSchema>;

interface VerdictRecord {
	id: string;
	title: string;
	verdict: Verdict;
	reasoning: string;
}

interface ReviewResult {
	cancelled: boolean;
	verdicts: VerdictRecord[];
}

interface ApprovalResult {
	cancelled: boolean;
	approved: boolean;
	draft: string;
}

const VISION_WORKFLOW_PROMPT = [
	"Run the native Pi vision workflow for this repository.",
	"",
	"Treat VISION.md as the canonical project vision when it exists.",
	"If it exists, use delta mode and never replace it without explicit author approval.",
	"Otherwise use from-scratch mode.",
	"",
	"Read the nearest AGENTS.md and README.md before drafting.",
	"Mine real repository evidence from files, tests, and git history.",
	"Use plain git history or the ordinary gh CLI when available.",
	"Do not depend on gh-axi, lavish-axi, a browser board, or invented evidence.",
	"",
	"Draft a concise, testable acceptance policy with an identity opener, three to six principles, explicit non-goals, and positive and negative alignment tests.",
	"Keep each sentence on one line and keep the draft roughly 40 to 70 lines.",
	"Create eight to twelve hard, non-predictable hypotheticals with a proposal, tested principle, and steelman for both answers.",
	"",
	"Call the vision_review tool with the complete draft and all hypotheticals.",
	"Fold every returned verdict into the draft and record the verdict and reasoning in VISION-answers.md.",
	"Keep the hypothetical set in VISION-hypotheticals.md and maintain VISION-changelog.md with traced edits.",
	"After the draft has incorporated the verdicts, call vision_approve.",
	"Only write or update VISION.md after vision_approve reports approved=true.",
	"Never approve on the author's behalf and never treat cancellation as approval.",
].join("\n");

function wrap(text: string, width: number): string[] {
	const safeWidth = Math.max(1, width);
	if (text.length === 0) return [""];
	return wrapTextWithAnsi(text, safeWidth);
}

function padLine(line: string, width: number): string {
	if (width <= 0) return "";
	const truncated = truncateToWidth(line, width, "");
	return truncated + " ".repeat(Math.max(0, width - visibleWidth(truncated)));
}

function styleDraftLine(line: string, theme: Theme): string {
	const trimmed = line.trimStart();
	if (trimmed.startsWith("#")) return theme.fg("accent", theme.bold(line));
	if (trimmed.startsWith("---")) return theme.fg("dim", line);
	return theme.fg("text", line);
}

function renderDraftPane(draft: string, width: number, theme: Theme): string[] {
	const lines: string[] = [theme.fg("muted", "latest draft · full text"), ""];
	for (const line of draft.split(/\r?\n/)) {
		lines.push(...wrap(styleDraftLine(line, theme), width));
	}
	return lines;
}

function renderCardPane(
	card: ReviewCard,
	cardIndex: number,
	totalCards: number,
	width: number,
	theme: Theme,
	selectedVerdict: number,
	focus: "verdict" | "reason",
	editor: Editor,
): string[] {
	const lines: string[] = [];
	const add = (text: string) => lines.push(...wrap(text, width));
	const addSection = (label: string, value: string) => {
		lines.push(theme.fg("muted", label));
		lines.push(...wrap(theme.fg("text", value), width));
		lines.push("");
	};

	lines.push(theme.fg("muted", `${card.id} · ${cardIndex + 1}/${totalCards}`));
	lines.push(theme.fg("accent", theme.bold(card.title)));
	lines.push("");
	addSection("Proposal", card.proposal);
	addSection("Tests", card.tests);
	addSection("Why the answer is not obvious", card.why);

	lines.push(theme.fg("muted", "Verdict"));
	for (let i = 0; i < VERDICTS.length; i++) {
		const label = `${selectedVerdict === i ? "●" : "○"} ${VERDICTS[i]}`;
		lines.push(
			selectedVerdict === i
				? theme.bg("selectedBg", theme.fg("text", label))
				: theme.fg("text", label),
		);
	}
	lines.push("");

	if (focus === "reason") {
		lines.push(theme.fg("muted", "Reasoning"));
		for (const line of editor.render(Math.max(1, width - 2))) {
			lines.push(` ${line}`);
		}
		lines.push(theme.fg("dim", "Enter record · Esc return to verdict"));
	} else {
		add("↑↓ choose a verdict · Tab or Enter add reasoning");
		add("Esc cancel the review");
	}

	return lines;
}

function createReviewBoard(
	tui: TUI,
	theme: Theme,
	draft: string,
	cards: ReviewCard[],
	done: (result: ReviewResult) => void,
): Component {
	let currentCard = 0;
	let selectedVerdict = 0;
	let focus: "verdict" | "reason" = "verdict";
	let closed = false;
	let cachedWidth: number | undefined;
	let cachedLines: string[] | undefined;
	const verdicts: VerdictRecord[] = [];

	const editorTheme: EditorTheme = {
		borderColor: (s: string) => theme.fg("accent", s),
		selectList: {
			selectedPrefix: (t: string) => theme.fg("accent", t),
			selectedText: (t: string) => theme.fg("accent", t),
			description: (t: string) => theme.fg("muted", t),
			scrollInfo: (t: string) => theme.fg("dim", t),
			noMatch: (t: string) => theme.fg("warning", t),
		},
	};
	const editor = new Editor(tui, editorTheme);

	const finish = (result: ReviewResult) => {
		if (closed) return;
		closed = true;
		done(result);
	};

	const refresh = () => {
		cachedWidth = undefined;
		cachedLines = undefined;
		tui.requestRender();
	};

	const commit = (reasoning: string) => {
		const card = cards[currentCard];
		verdicts.push({
			id: card.id,
			title: card.title,
			verdict: VERDICTS[selectedVerdict],
			reasoning: reasoning.trim(),
		});

		if (currentCard === cards.length - 1) {
			finish({ cancelled: false, verdicts: [...verdicts] });
			return;
		}

		currentCard += 1;
		selectedVerdict = 0;
		focus = "verdict";
		editor.setText("");
		refresh();
	};

	editor.onSubmit = (value: string) => {
		if (focus === "reason") commit(value);
	};

	const handleInput = (data: string) => {
		if (closed) return;
		if (matchesKey(data, Key.ctrl("c"))) {
			finish({ cancelled: true, verdicts: [...verdicts] });
			return;
		}

		if (focus === "reason") {
			if (matchesKey(data, Key.escape) || matchesKey(data, Key.tab)) {
				focus = "verdict";
				refresh();
				return;
			}
			editor.handleInput(data);
			refresh();
			return;
		}

		if (matchesKey(data, Key.up)) {
			selectedVerdict = Math.max(0, selectedVerdict - 1);
			refresh();
			return;
		}
		if (matchesKey(data, Key.down)) {
			selectedVerdict = Math.min(VERDICTS.length - 1, selectedVerdict + 1);
			refresh();
			return;
		}
		if (matchesKey(data, Key.tab) || matchesKey(data, Key.enter)) {
			focus = "reason";
			refresh();
			return;
		}
		if (matchesKey(data, Key.escape)) {
			finish({ cancelled: true, verdicts: [...verdicts] });
		}
	};

	const render = (width: number): string[] => {
		if (cachedLines && cachedWidth === width) return cachedLines;

		const safeWidth = Math.max(1, width);
		const card = cards[currentCard];
		const draftWidth = Math.max(1, Math.floor((safeWidth - 3) * 0.58));
		const cardWidth = Math.max(1, safeWidth - draftWidth - 3);
		const draftLines = renderDraftPane(draft, draftWidth, theme);
		const cardLines = renderCardPane(
			card,
			currentCard,
			cards.length,
			cardWidth,
			theme,
			selectedVerdict,
			focus,
			editor,
		);

		if (safeWidth < 100) {
			cachedLines = [
				theme.fg("accent", "─".repeat(safeWidth)),
				...renderDraftPane(draft, safeWidth, theme),
				"",
				...renderCardPane(
					card,
					currentCard,
					cards.length,
					safeWidth,
					theme,
					selectedVerdict,
					focus,
					editor,
				),
				theme.fg("accent", "─".repeat(safeWidth)),
			];
		} else {
			const separator = theme.fg("muted", " │ ");
			const rowCount = Math.max(draftLines.length, cardLines.length);
			cachedLines = [theme.fg("accent", "─".repeat(safeWidth))];
			for (let i = 0; i < rowCount; i++) {
				cachedLines.push(
					`${padLine(draftLines[i] ?? "", draftWidth)}${separator}${padLine(cardLines[i] ?? "", cardWidth)}`,
				);
			}
			cachedLines.push(theme.fg("accent", "─".repeat(safeWidth)));
		}

		cachedWidth = width;
		return cachedLines;
	};

	return {
		render,
		handleInput,
		invalidate: () => {
			cachedWidth = undefined;
			cachedLines = undefined;
		},
	};
}

async function reviewWithDialogs(
	ctx: ExtensionContext,
	params: VisionReviewParams,
): Promise<ReviewResult> {
	const verdicts: VerdictRecord[] = [];

	for (const [index, card] of params.cards.entries()) {
		ctx.ui.notify(
			`${card.id} · ${index + 1}/${params.cards.length}\n\n${card.title}\n\n${card.proposal}\n\nTests: ${card.tests}\n\nWhy the answer is not obvious: ${card.why}`,
			"info",
		);
		const verdict = await ctx.ui.select(`Verdict for ${card.id}`, [...VERDICTS]);
		if (!verdict) return { cancelled: true, verdicts };
		const reasoning = await ctx.ui.input("Reasoning", "Why this verdict?");
		if (reasoning === undefined) return { cancelled: true, verdicts };
		verdicts.push({
			id: card.id,
			title: card.title,
			verdict: verdict as Verdict,
			reasoning,
		});
	}

	return { cancelled: false, verdicts };
}

function reviewContent(result: ReviewResult): string {
	if (result.cancelled) {
		return `Vision review cancelled after ${result.verdicts.length} verdict(s).`;
	}
	if (result.verdicts.length === 0) return "Vision review recorded no verdicts.";
	return [
		`Vision review recorded ${result.verdicts.length} verdict(s).`,
		...result.verdicts.map(
			(item) => `${item.id} (${item.title}): ${item.verdict}.${item.reasoning ? ` Reasoning: ${item.reasoning}` : ""}`,
		),
	].join("\n");
}

async function approveVision(ctx: ExtensionContext, params: VisionApprovalParams): Promise<ApprovalResult> {
	if (!ctx.hasUI) return { cancelled: true, approved: false, draft: params.draft };

	const editedDraft = await ctx.ui.editor("Review final VISION.md", params.draft);
	if (editedDraft === undefined || editedDraft.trim().length === 0) {
		return { cancelled: true, approved: false, draft: params.draft };
	}

	const approved = await ctx.ui.confirm(
		"Approve VISION.md?",
		`The approved draft for ${params.project} may now be written to VISION.md.`,
	);
	return { cancelled: !approved, approved, draft: editedDraft };
}

function approvalContent(result: ApprovalResult): string {
	if (result.cancelled) return "VISION.md approval was cancelled or declined.";
	return [
		"VISION.md was approved. Write exactly the following draft to VISION.md now:",
		"",
		result.draft,
	].join("\n");
}

export default function visionExtension(pi: ExtensionAPI) {
	pi.registerCommand("vision", {
		description: "Start an evidence-mined, author-approved VISION.md workflow",
		handler: async (args, ctx) => {
			const target = args.trim();
			const targetNote = target ? `\nRequested target or focus: ${target}` : "";
			const prompt = `${VISION_WORKFLOW_PROMPT}${targetNote}`;
			const options = ctx.isIdle() ? undefined : { deliverAs: "followUp" as const };
			pi.sendUserMessage(prompt, options);
			ctx.ui.notify("Vision workflow queued for the agent.", "info");
		},
	});

	pi.registerTool({
		name: "vision_review",
		label: "Vision Review",
		description:
			"Present a complete VISION.md draft and its fault-line hypotheticals to the author, then collect one structured verdict and reasoning for each card.",
			promptSnippet: "Review a VISION.md draft with the author using a native interactive board",
			promptGuidelines: [
				"Use vision_review only after mining real repository evidence and drafting the complete VISION.md candidate.",
				"Use vision_review instead of asking the author to review hypotheticals in an unstructured paragraph.",
			],
		parameters: VisionReviewParamsSchema,
		executionMode: "sequential",

		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			if (!ctx.hasUI) {
				return {
					content: [{ type: "text", text: "Vision review requires an interactive UI." }],
					details: { cancelled: true, verdicts: [] } satisfies ReviewResult,
				};
			}

			const result =
				ctx.mode === "tui"
					? await ctx.ui.custom<ReviewResult>((tui, theme, _keybindings, done) =>
							createReviewBoard(tui, theme, params.draft, params.cards, done),
						)
					: await reviewWithDialogs(ctx, params);

			return {
				content: [{ type: "text", text: reviewContent(result) }],
				details: result,
			};
		},

		renderCall(args, theme) {
			const count = Array.isArray(args.cards) ? args.cards.length : 0;
			return new Text(
				theme.fg("toolTitle", theme.bold("vision_review ")) +
					theme.fg("muted", `${args.project} · ${count} hypothetical${count === 1 ? "" : "s"}`),
				0,
				0,
			);
		},

		renderResult(result, _options, theme) {
			const details = result.details as ReviewResult | undefined;
			if (!details) return new Text(theme.fg("muted", "Vision review finished"), 0, 0);
			if (details.cancelled) {
				return new Text(theme.fg("warning", `Review cancelled after ${details.verdicts.length} verdict(s)`), 0, 0);
			}
			return new Text(theme.fg("success", `✓ ${details.verdicts.length} verdict(s) recorded`), 0, 0);
		},
	});

	pi.registerTool({
		name: "vision_approve",
		label: "Approve Vision",
		description:
			"Let the author edit and explicitly approve the final VISION.md draft before the agent writes it.",
			promptSnippet: "Ask the author to edit and explicitly approve the final VISION.md",
			promptGuidelines: [
				"Call vision_approve only after incorporating all vision_review verdicts and recording the changelog.",
				"Write VISION.md only when vision_approve returns approved=true.",
			],
		parameters: VisionApprovalParamsSchema,
		executionMode: "sequential",

		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			if (!ctx.hasUI) {
				return {
					content: [{ type: "text", text: "Vision approval requires an interactive UI." }],
					details: { cancelled: true, approved: false, draft: params.draft } satisfies ApprovalResult,
				};
			}

			const result = await approveVision(ctx, params);
			return {
				content: [{ type: "text", text: approvalContent(result) }],
				details: result,
			};
		},

		renderCall(args, theme) {
			return new Text(
				theme.fg("toolTitle", theme.bold("vision_approve ")) + theme.fg("muted", args.project),
				0,
				0,
			);
		},

		renderResult(result, _options, theme) {
			const details = result.details as ApprovalResult | undefined;
			if (!details || details.cancelled) return new Text(theme.fg("warning", "Approval declined"), 0, 0);
			return new Text(theme.fg("success", "✓ VISION.md approved"), 0, 0);
		},
	});
}
