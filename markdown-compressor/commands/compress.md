---
description: "Compress a markdown file to reduce token usage — lossless (structural) or lossy (semantic) modes with section-by-section review"
argument-hint: "<file-path> [--lossless] [--auto]"
disable-model-invocation: true
---

Compress the specified markdown file using the `markdown-compression` skill. The goal is to reduce token usage while preserving the information an LLM needs.

Follow this process exactly:

## Step 1: File Validation

Read the file specified in `$ARGUMENTS`. If no file was provided, use `AskUserQuestion` to ask the user which file to compress.

Verify:
- File exists and is readable
- File is markdown (`.md` extension)
- File is not empty

If the file has YAML frontmatter, note it — frontmatter must be preserved exactly.

## Step 2: Mode Selection

If `--lossless` was passed in arguments, use lossless mode. Otherwise, use `AskUserQuestion` to ask:

- **Lossy (recommended)** — semantic compression with compressor-reviewer loop. Maximum token reduction.
- **Lossless** — structural optimization only. Zero semantic change.

If `--auto` was passed in arguments, enable auto-approve mode and skip the question below. Otherwise, **immediately after** the mode selection answer is received, use `AskUserQuestion` to ask about review style — **do NOT proceed to Step 3 until this question is answered**:

- **Section-by-section (recommended)** — review and approve/skip/edit each section individually.
- **Auto-approve** — compress all sections without per-section review. The `compression-reviewer` agent still runs in lossy mode and auto-incorporates fixes, but the user is not gated.

**Both mode and review style must be resolved before moving to Step 3.**

## Step 3: Pre-Analysis

Read the full file and analyze its structure:

1. Parse the heading hierarchy (identify all `#`, `##`, `###`, etc.)
2. Split the file into sections at the highest sensible heading level (typically `##`)
3. For each section, count approximate tokens (words * 1.3)
4. Flag any structural issues:
   - Skipped heading levels (e.g., `#` → `###`)
   - Sections over ~500 tokens (candidates for attention)
   - Empty sections
   - Duplicate content across sections

Present the structural analysis as a table:

```
| # | Section | Tokens | Notes |
|---|---------|--------|-------|
| 1 | Overview | ~130 | |
| 2 | Configuration | ~340 | |
| 3 | Deployment | ~520 | Large section |
| 4 | Testing | ~0 | Empty |
```

Show the total token count. Then proceed to compression.

## Step 4: Batched Section Compression

Process non-empty sections in **batches of 5** to parallelize agent work. Each batch runs compressor agents simultaneously, then reviewer agents simultaneously, then handles results.

### Batch Loop

Repeat for each batch of up to 5 non-empty sections:

#### 4a: Compress Batch

Dispatch **all compressor agents in the batch in a single message** (multiple parallel Agent tool calls). Each `section-compressor` agent receives:
- The section's original text
- The compression mode (lossless or lossy)
- The section heading
- Adjacent section headings for context

Agents are read-only (Read/Grep/Glob only) and receive section text in their prompt — they do not read or modify the target file. It is safe to dispatch all agents in a batch simultaneously.

Wait for all compressor agents in the batch to return before proceeding to 4b.

#### 4b: Review Batch (lossy mode only)

If in lossy mode, dispatch **all reviewer agents in the batch in a single message** (multiple parallel Agent tool calls). Each `compression-reviewer` agent receives:
- The original section text
- The compressed section text from 4a
- The mode

Wait for all reviewer agents in the batch to return. For any section where the reviewer flags critical issues, incorporate the suggested restorations into the compressed version.

#### 4c: Present and Decide

**If auto-approve is active**, show a batch summary with one line per section:

```
Section [N]/[total]: [heading] — ~X → ~Y tokens (-Z%)
```

Then proceed directly to 4d for all sections in the batch.

**If auto-approve is NOT active**, present each section in the batch one at a time:

```
**Section: [heading]**
Original (~X tokens) → Compressed (~Y tokens) | -Z%

[Show the compressed version]

Changes: [brief list of what changed]
```

If the reviewer flagged and the output was adjusted, note: "Reviewer caught: [what was restored]"

Use `AskUserQuestion` for each section's decision:
- **Approve** — accept the compressed version
- **Skip** — keep the original section unchanged
- **Edit** — user provides custom text for this section

If the user chooses Edit, accept their replacement text for the section and continue to the next section in the batch.

#### 4d: Write Back

Write results to file for each section in the batch, in document order (top to bottom):

- **Approve / Auto-approve:** Use the `Edit` tool to replace the original section text with the compressed version.
- **Skip:** No edit needed — the original text stays.
- **Edit:** Use the `Edit` tool to replace the original section text with the user's custom text.

**Important:** After writing a batch, re-read the file before processing the next batch. Section boundaries shift as earlier sections change length. Use heading text (which is always preserved) to locate sections reliably.

### Why Batched

- Compressor and reviewer agents are independent per section — no cross-section dependencies
- Batch of 5 balances parallelism against API rate limits
- For 17 sections: ~4 batches instead of 17 sequential rounds (~4x wall-time speedup)
- In section-by-section mode, pre-computed batches eliminate wait time between reviews within a batch

## Step 5: Results

After all sections are processed, show the compression summary:

```
## Compression Complete

| Metric | Value |
|--------|-------|
| Original | ~X tokens |
| Compressed | ~Y tokens |
| Reduction | Z% |
| Sections modified | A of B |
| Mode | lossless/lossy |
```

The file has already been updated in-place throughout Step 4. Inform the user: "All changes written. Use `git diff` to review or `git checkout -- <file>` to revert."

## Mandatory Use of AskUserQuestion

**Every user decision point MUST use the `AskUserQuestion` tool.** Never ask for decisions via inline text. The interactive selector provides a consistent UX.

### Main Conversation Owns All User Interaction

`AskUserQuestion` must be called from **this command** (the main conversation), never from subagents. The `section-compressor` and `compression-reviewer` agents handle compression and review — they return results. This command presents those results and calls `AskUserQuestion` for every decision gate.

**Pattern:** for each batch of 5 sections → dispatch all compressor agents in parallel → collect results → dispatch all reviewer agents in parallel → collect results → incorporate fixes → present/auto-approve → write to file → next batch.

### Decision Points

Use `AskUserQuestion` at:
- File selection (if no argument)
- Mode selection (if no `--lossless` flag)
- Review style selection (if no `--auto` flag) — MUST be asked immediately after mode selection, before Step 3
- Per-section approval (approve/skip/edit) — unless auto-approve is active
