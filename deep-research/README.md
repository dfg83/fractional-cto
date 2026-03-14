# Deep Research

A structured deep research plugin for Claude Code that transforms ad-hoc web searches into a repeatable, hallucination-resistant research pipeline.

## The Problem

When using Claude Code for research, three problems emerge:

1. **No methodology** — Research is ad-hoc, with no structured approach to decomposition, source evaluation, or synthesis
2. **Hallucination risk** — Without verification guardrails, research agents produce confident reports with fabricated statistics, fake citations, and unsourced claims
3. **Poor source quality** — Agents default to SEO-optimized content farms over authoritative sources, with 57% of source errors occurring in the first retrieval round

## What This Plugin Provides

### Skills

| Skill | Purpose |
|-------|---------|
| `research-methodology` | Query analysis, decomposition strategies, effort scaling, dynamic replanning, stopping criteria |
| `source-evaluation` | Source credibility tiers (T1-T6), multi-provider search strategy, SEO spam detection, CRAAP framework |
| `hallucination-prevention` | 7-type hallucination taxonomy, citation verification rules, circuit breaker patterns, confidence scoring |
| `synthesis-and-reporting` | Deduplication, conflict resolution, thematic analysis, citation management, report quality checklist |

### Command

**`/research <topic>`** — Orchestrated research session:
1. Analyzes query complexity — asks clarifying questions if too vague
2. Decomposes into subtopics (count emerges from query, not preset)
3. Spawns parallel `research-worker` agents with web search
4. Each worker writes an intermediate document with sources
5. Synthesizes into a single output document with inline citations
6. Preserves worker docs for traceability

### Agent

**`research-worker`** — Parallel web research agent (runs on Sonnet):
- Searches the web extensively on an assigned subtopic
- Evaluates source credibility using the T1-T6 tier system
- Writes intermediate findings with inline citations
- Flags uncertainties and gaps explicitly

## Three Meta-Principles

1. **Every claim needs a source** — No unsourced assertions. If it cannot be cited, it cannot be stated as fact.
2. **Source quality determines output quality** — Front-load high-quality sources. 57% of errors start in early retrieval.
3. **Verify before synthesizing** — Treat each agent's output as untrusted input. Cross-reference claims.

## Installation

```bash
# Test locally
claude --plugin-dir /path/to/deep-research

# Or add to your project
# Copy to your project's plugin directory
```

## Usage

```
# Full orchestrated research session
/research "How do production LLM agents handle memory and state?"

# Skills auto-activate when relevant
# Ask about source quality → source-evaluation loads
# Writing a research report → synthesis-and-reporting loads
# Verifying claims → hallucination-prevention loads
```

## Research Foundations

This plugin's methodology is grounded in:

- **Anthropic's multi-agent research system** — orchestrator-worker pattern, CitationAgent, effort scaling rules
- **OWASP Top 10 for Agentic Applications** — ASI08 cascading failure prevention
- **Press et al. (EMNLP 2023)** — Self-Ask decomposition, compositionality gap
- **Liu et al. (TACL 2024)** — Lost in the Middle position bias
- **Tavily research** — reflection-based token efficiency (linear vs quadratic growth)
- **DR-Arena (2025)** — source quality as primary bottleneck in deep research agents
