# Native Vision Extension

This project-local Pi extension provides an evidence-driven `VISION.md` review workflow without `axi` packages or a browser board.

## Use

Start Pi from the repository root:

```bash
pi -e ./.pi/extensions/vision.ts
```

Then run:

```text
/vision
```

The command asks the agent to mine repository evidence, draft or update `VISION.md`, generate fault-line hypotheticals, call the native review tool, and request explicit final approval before writing the file.

## Interactive review

In TUI mode, `vision_review` shows the complete draft beside one hypothetical at a time.
Use the arrow keys to choose a verdict, `Tab` or `Enter` to enter reasoning, `Enter` to record, and `Esc` to cancel.

In RPC mode, the extension falls back to Pi's `select`, `input`, `editor`, and `confirm` dialogs.
Print and JSON modes report that interactive review is unavailable.

The extension uses only Pi's extension and TUI APIs plus the bundled `typebox` schema library.
It does not invoke `gh-axi`, `lavish-axi`, `npx`, or an external review server.
