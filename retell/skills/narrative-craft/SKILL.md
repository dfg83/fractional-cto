---
name: narrative-craft
description: >
  This skill should be used when writing a blog post from conversation data, identifying
  story arcs in human-AI collaboration, structuring narrative beats, choosing story angles,
  handling user quotes, or applying editorial principles to conversation-derived content.
  Covers first-person voice constraints, five-act structure mapping, beat-to-treatment
  classification, and blog-worthiness heuristics specific to the retell pipeline.
version: 0.1.0
---

# Narrative Craft

## Overview

Guide the retell pipeline's LLM stages through editorial decisions: which moments matter, what angle to take, how to structure beats, and how to write in authentic first-person voice. This skill provides the narrative principles and practical heuristics for the Triage, Outline, Draft, and Polish stages.

## Hard Constraints

### First-Person Voice

All blog posts use first-person voice from the author's perspective. This is not configurable.

- "I asked Claude to..." not "The user asked Claude to..."
- "I rejected the monochrome direction because..." not "Oliver rejected..."
- "I'd built this brainstorming skill the week before..." not "A brainstorming skill had been built..."

### No Dashes as Punctuation

Never use em dashes, en dashes, or hyphens as punctuation in the final blog post. They are a dead giveaway of AI-generated text. Restructure sentences instead: use commas, semicolons, colons, parentheses, or split into separate sentences. Hyphens in compound words (e.g., "real-time", "well-known") are fine.

## Story Arc Detection

### Beat Types

Every conversation contains beats — moments where something shifts. Classify each event:

| Beat type | Detection signal |
|-----------|-----------------|
| **Opening / Inciting event** | First substantive user message (skip interrupted ones) |
| **Plan / Strategy** | `planContent` field, or assistant messages with structured plans |
| **Action / Exploration** | Clusters of `tool_use` calls (research, code writing, browsing) |
| **Pivot / Rejection** | User pushback, direction changes ("feels wrong", "let's try...") |
| **Discovery / Breakthrough** | Excitement markers, resolution of prior tension |
| **Convergence** | Options narrowing, decisions locking in |
| **Resolution** | Final deliverable, user satisfaction, or deliberate stopping point |

### The Five-Act Structure

Long conversations naturally fall into acts:

```
ACT 1  Setup:        What's the goal? What's the plan?
ACT 2  Exploration:  Research, first attempts, parallel work
ACT 3  Deepening:    Iteration, refinement, pointed questions
ACT 4  Convergence:  Options narrow, decisions lock in
ACT 5  Resolution:   Final output (may be open-ended)
```

Session boundaries and `/compact` markers are natural act breaks. For technical details on detecting these boundaries, see the `conversation-format` skill.

## Story Angles

The same conversation can yield multiple blog posts. Each angle pulls a different thread:

| Angle type | Focus | Best when |
|-----------|-------|-----------|
| **Process** | The journey from start to finish | Clear arc with setup → conflict → resolution |
| **Decision** | A specific pivotal choice | Strong rejection/pivot moment with emotional texture |
| **Methodology** | A technique or approach used | Reusable method that others could adopt |
| **Capability** | What the AI could do | Surprising or non-obvious AI behavior |
| **Tool-building** | Making tools to solve problems | Meta-narrative: built the tool, then used it |

A recommendation should argue for an angle with reasoning: why the arc works narratively, who would read it, and what makes it non-obvious.

## Narrative Signal Classification

The `conversation-format` skill owns the technical extraction rules (which JSONL entry types to parse, which content blocks to extract, which user messages to filter). This section covers the *editorial* layer: how to prioritize extracted signal for narrative purposes.

### High narrative value

| Source | Why it matters for the story |
|--------|------------------------------|
| User `text` | Drives the story — intent, pivots, emotions |
| Assistant `text` | The action, decisions, deliverables |
| Thinking blocks | "Behind the scenes" depth — reveals reasoning, internal deliberation |
| Continuation summaries | Ready-made chapter bridges between sessions |

### Medium narrative value (use selectively)

| Source | When to include |
|--------|----------------|
| Tool names | When the *action* matters ("launched 4 parallel agents") |
| Turn duration | To convey pacing ("after 3 minutes of research...") |
| Subagent final outputs | When showing depth of investigation |

### Skip in all narrative stages

Tool result contents, progress entries, empty messages (permission grants), system-reminder tags, and CLI command output. These are already filtered by the parser — see the `conversation-format` skill for the complete filter chain.

## Quote Handling

Real CLI user messages are informal — typos, fragments, shorthand. Direct quotes should feel authentic but not sloppy.

**Rules:**
- **Fix obvious typos** when quoting ("If feels" becomes "It feels")
- **Merge consecutive user messages** that form one thought into a single quote
- **Mark cleaned quotes with `[cleaned]`** in the outline so the author can verify
- **Never fabricate quotes** — clean and merge only, never invent

**Example:**
- Raw: `"Why did we come up with mono. If feels completely wrong to me."` + `"Even lifeless"`
- Cleaned: `"It feels completely wrong to me. Even lifeless."`

## Author Context

The JSONL contains what happened but not why it matters. Author context fills that gap and can be injected at any interactive gate:

| Type | Effect on the story |
|------|-------------------|
| **Backstory** | Adds depth (a tool was *crafted*, not just used) |
| **Intent / motivation** | Gives emotional stakes the conversation never stated |
| **Audience framing** | Shapes tone, jargon level, assumptions |
| **Corrections** | Prevents narrative built on a misread |
| **Scope directives** | Editorial cuts before tokens are spent |

Author context is tiny (~100-500 tokens) and travels forward through all subsequent stages.

## Blog-Worthiness Heuristics

Not every conversation makes a good story. Quick assessment before spending tokens:

**Likely blog-worthy:**
- 15+ substantive user messages
- Subagent research (parallel exploration)
- Multi-session (longer arc)
- Diverse tools (research + creation + browsing)
- Emotional moments (rejection, excitement, surprise)

**Probably not a story:**
- Fewer than 5 substantive user messages
- Single tool type (just Edit + Bash = coding session)
- No pivots or decisions (linear task completion)
- Very small file (<0.1 MB)

These are heuristics, not rules. A 10-message conversation with a dramatic pivot can be a great short-form post.

## Treatment Types

When building an outline, classify each beat's treatment:

| Treatment | Description | When to use |
|-----------|-------------|-------------|
| `quote` | Use exact words (cleaned) | Emotional moments, pivotal statements |
| `summarize` | Paraphrase in narrative voice | Technical details, long exchanges |
| `montage` | Compress a sequence into flowing prose | Clusters of similar actions |
| `skip` | Omit entirely | Tangents, repetition, dead ends |

## Scope Rules

- Read from a **single conversation** plus its subagents only
- Never parse or reference other conversation files
- If the author wants backstory from other sessions, they inject it as author context
- A single conversation can yield multiple blog posts — different angle, different story
