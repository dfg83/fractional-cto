# Synthesis Patterns — Detailed Reference

This reference provides detailed synthesis approaches from commercial research systems and academic research. Consult when implementing or improving synthesis quality.

## Commercial System Approaches

### OpenAI Deep Research

Follows a Plan-Act-Observe loop where an o3-based model iteratively searches, reads, and reasons. The synthesizer constructs a narrative outline for the final document and decides the structure that best fits the material — whether chronological, thematic, or problem-and-solution. Redundant information from multiple sub-agents is merged into a single clean statement before report writing begins.

**Source:** [OpenAI blog](https://openai.com/index/introducing-deep-research/); [PromptLayer analysis](https://blog.promptlayer.com/how-deep-research-works/)

### Google Gemini Deep Research

Performs multiple passes of self-critique to enhance clarity and detail. In building the report, Gemini critically evaluates information, identifies key themes and inconsistencies, and structures the report logically. Users can review and edit the research plan before execution.

**Source:** [Google blog](https://blog.google/products/gemini/google-gemini-deep-research/)

### Anthropic Multi-Agent Research System

Uses a LeadResearcher (Opus 4) that synthesizes results from parallel subagents (Sonnet 4) and decides whether more research is needed. A dedicated CitationAgent processes documents to identify specific citation locations. The system outperformed single-agent setups by more than 90%, with improvement strongly linked to spreading reasoning across multiple independent context windows.

**Source:** [Anthropic engineering blog](https://www.anthropic.com/engineering/multi-agent-research-system)

## Synthesis Approaches

### Map-Reduce Synthesis

**Pattern:** Each worker produces a summary of its findings (map). The synthesizer combines all summaries into a final report (reduce). Used by O-Researcher and LangChain's map-reduce chain.

**Advantages:** Scalable to many workers. Each worker's summary is independent. Clear separation of concerns.

**Disadvantages:** Information loss during mapping. Cross-topic connections may be missed. Two-stage process limits interleaving.

**Source:** [O-Researcher, arXiv 2601.03743](https://arxiv.org/abs/2601.03743)

### Iterative Refinement

**Pattern:** Start with a draft report. Iteratively refine by comparing against source material, filling gaps, resolving inconsistencies, and improving coherence.

**Advantages:** Multiple passes improve quality. Can catch errors missed in first pass. Natural self-critique loop.

**Disadvantages:** Token-expensive (each iteration re-processes the full report). Risk of over-editing (introducing errors in later passes). Diminishing returns after 2-3 iterations.

### Outline-First Synthesis

**Pattern:** Generate a report outline (section headings + bullet points) first. Then fill each section independently. Finally, smooth transitions between sections.

**Advantages:** Structure is explicit and reviewable before committing to prose. Each section can be filled in parallel. Consistent with how human writers work.

**Disadvantages:** Rigid structure may not fit the material. Section boundaries can create artificial divisions. Requires good outline quality.

## Position-Bias Mitigation

The "Lost in the Middle" phenomenon is described in detail in `hallucination-prevention/references/hallucination-research.md`. In the synthesis context, the key implication is that LLMs attend disproportionately to information at the beginning and end of context, with >20% performance degradation for middle-positioned information (Liu et al., TACL 2024).

**Mitigations for synthesis:**
1. **Reorder context strategically** — Place the most important worker findings at the beginning and end of the synthesis prompt
2. **Process workers independently** — Synthesize each worker's findings into notes first, then combine notes (avoids one massive context)
3. **Use structured extraction** — Extract key claims and citations from each worker into a structured format before prose synthesis
4. **Multiple synthesis passes** — First pass for structure, second pass with reordered context for completeness

## Deduplication Patterns

### Three-Level Pipeline

Extending the framework defined in the `synthesis-and-reporting` SKILL.md:

1. **Exact dedup** — Same URL or identical text appearing in multiple workers → keep one reference, prefer the earliest retrieval
2. **Near-duplicate dedup** — Same content with minor wording variations from different URLs (syndicated content) → identify the primary source using authority signals
3. **Semantic dedup** — Different words expressing the same finding → merge into strongest statement, cite the most authoritative source

### SemHash for Semantic Deduplication

SemHash combines Model2Vec embeddings with Approximate Nearest Neighbor search via Vicinity. Can deduplicate SQuAD 2.0 (130,000 samples) in 7 seconds. Identifies semantic duplicates — content pairs conveying similar meaning despite different wording.

**Source:** [GitHub: MinishLab/semhash](https://github.com/MinishLab/semhash)

## Conflict Resolution Framework

### DRAGged into Conflicts (2025)

The DRAGged into Conflicts benchmark specifically evaluates how LLMs handle contradicting information from retrieved passages. Key finding: models often default to one source without acknowledging the conflict, producing authoritative-sounding but one-sided reports.

**Source:** [arXiv 2506.08500](https://arxiv.org/abs/2506.08500)

### Resolution Strategies by Conflict Type

| Conflict Type | Strategy | Example |
|--------------|----------|---------|
| **Numerical discrepancy** | Report both values; cite sources; note discrepancy | "Source A reports 47% while Source B reports 52%" |
| **Contradictory findings** | Present both; explain methodology differences | "Study A (lab setting) found X; Study B (field setting) found Y" |
| **Temporal evolution** | Present as a timeline; prefer most recent | "Earlier work reported X; more recent analysis shows Y" |
| **Scope difference** | Clarify each finding's scope | "For enterprise contexts, X holds; for startups, Y is more common" |

## Report Quality Metrics

### RAGAS Faithfulness

Measures whether the generated report is faithful to the source documents. Decomposes the report into individual claims and checks each against the source context. Scores from 0 to 1.

**Source:** [RAGAS, arXiv 2309.15217](https://arxiv.org/abs/2309.15217)

### G-Eval

Uses LLM-as-judge with chain-of-thought evaluation across dimensions: coherence, consistency, fluency, relevance. Achieves higher correlation with human judgments than traditional metrics.

**Source:** [arXiv 2303.16634](https://arxiv.org/abs/2303.16634)

### Practical Quality Checks

For research documents, these concrete checks matter more than abstract metrics:

1. **Citation coverage** — What percentage of factual claims have inline citations?
2. **Source diversity** — How many independent sources are cited? (>5 for moderate research, >15 for comprehensive)
3. **Conflict acknowledgment** — Are contradictions between sources noted?
4. **Gap transparency** — Are limitations and uninvestigated areas stated?
5. **Numerical accuracy** — Do reported numbers match source text exactly?
