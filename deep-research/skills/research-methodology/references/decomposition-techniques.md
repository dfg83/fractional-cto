# Decomposition Techniques — Detailed Reference

This reference provides detailed descriptions of decomposition techniques for research query planning. Consult when selecting or implementing a decomposition strategy.

## Self-Ask Prompting (Press et al., EMNLP 2023)

**Paper:** "Measuring and Narrowing the Compositionality Gap in Language Models" ([arXiv 2210.03350](https://arxiv.org/abs/2210.03350))

**Mechanism:** The model explicitly asks itself intermediate follow-up questions, answers them, then composes the final answer. The structured "Follow up: / Intermediate answer:" format forces explicit decomposition and creates natural insertion points for external tools (web search).

**Format:**
```
Question: [Complex multi-hop question]
Are follow up questions needed here: Yes.
Follow up: [Sub-question 1]
Intermediate answer: [Answer to sub-question 1]
Follow up: [Sub-question 2]
Intermediate answer: [Answer to sub-question 2]
So the final answer is: [Composed answer]
```

**Results:** On Bamboogle (multi-hop questions Google cannot answer directly): Self-Ask 57.6%, Self-Ask + Search 60.0%, vs chain-of-thought 46.4%. On 2WikiMultiHopQA: Self-Ask + Search 40.1% vs Self-Ask alone 30.0%.

**When to use:** Multi-hop factual queries where each sub-question is independently answerable. Most effective when combined with search tools.

**Limitations:** Sequential dependency assumption — all sub-questions chain linearly. Single-pass decomposition — no revisiting earlier sub-questions. Shallow decomposition for deeply nested queries.

## Least-to-Most Prompting (Zhou et al., ICLR 2023)

**Paper:** "Least-to-Most Prompting Enables Complex Reasoning in Large Language Models" ([arXiv 2205.10625](https://arxiv.org/abs/2205.10625))

**Mechanism:** Two-stage process: (1) Decompose the problem into ordered subproblems from simplest to most complex. (2) Solve each subproblem sequentially, feeding the answer of each into the context for the next.

**Key result:** On the SCAN benchmark (compositional generalization), Least-to-Most with just 14 examples achieved 99.7% accuracy versus 6% for standard prompting — and this was comparable to neural-symbolic models trained on the full 15,000-example training set.

**When to use:** Problems with natural ordering from simple to complex. Tasks requiring compositional generalization. Educational/tutorial-style explanations.

**Limitations:** Forces sequential execution — no parallelism. Context window grows with each step (accumulated answers). Ordering sensitivity — wrong decomposition order degrades results.

## Plan-and-Solve Prompting (Wang et al., ACL 2023)

**Paper:** "Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models" ([arXiv 2305.04091](https://arxiv.org/abs/2305.04091))

**Mechanism:** Zero-shot prompt: "Let's first understand the problem and devise a plan to solve the problem. Then, let's carry out the plan and solve the problem step by step." The improved PS+ variant adds instructions to "extract relevant variables" and "calculate intermediate results."

**Results:** PS+ consistently outperformed Zero-shot-CoT across all tested datasets and achieved comparable performance to 8-shot CoT — without any examples.

**When to use:** When few-shot examples are not available. General-purpose planning for novel query types. Quick decomposition without elaborate prompting.

## DAG-Based Decomposition (MindSearch, ICLR 2025)

**Paper:** "MindSearch: Mimicking Human Minds Elicits Deep AI Searcher" ([arXiv 2407.20183](https://arxiv.org/abs/2407.20183))

**Mechanism:** Models query decomposition as iterative directed acyclic graph construction. A WebPlanner decomposes the query into a DAG of sub-questions where edges represent dependencies. WebSearcher agents execute each node. New sub-questions emerge from discovered information — the graph grows dynamically.

**Key result:** Processes 300+ web pages in 3 minutes. Achieves significantly deeper research than flat decomposition.

**Three dependency types:**
- **Data dependency** — Sub-question B requires the answer to sub-question A
- **Logical dependency** — Sub-question B's formulation depends on A's answer
- **Discovery dependency** — Sub-question B only becomes apparent after answering A

**When to use:** Complex queries with inter-dependent threads. Research topics where subtopics are not known in advance. Situations requiring iterative deepening.

## LLMCompiler (Kim et al., ICML 2024)

**Paper:** "An LLM Compiler for Parallel Function Calling" ([arXiv 2312.04511](https://arxiv.org/abs/2312.04511))

**Mechanism:** Treats query decomposition like compiler optimization — identifies tasks that can run in parallel based on data dependencies, schedules them as soon as dependencies are met.

**Key result:** 3.74x speedup over sequential approaches, 6.73x cost reduction by avoiding redundant tool calls.

**When to use:** When execution speed matters. Queries with a mix of independent and dependent subtopics. Production systems where parallelism directly reduces latency and cost.

## ParallelSearch (Zhao et al., 2025)

**Paper:** "ParallelSearch: Training LLMs to Decompose Queries into Parallel Sub-Queries"

**Mechanism:** Uses reinforcement learning to train LLMs to decompose queries into parallel sub-queries. The model learns which parts of a query can be investigated simultaneously vs. which require sequential processing.

**Key result:** 12.7% improvement on parallelizable questions while using only 69.6% of LLM calls versus sequential approaches.

**When to use:** Queries with clearly independent facets. Comparison-type queries. Survey-type queries covering multiple aspects of a topic.

## Choosing a Decomposition Strategy — Decision Framework

```
Is the query a single fact lookup?
  → YES: No decomposition needed. Direct search.
  → NO: Continue.

Does the query have independent facets that can be researched simultaneously?
  → YES: Parallel decomposition (ParallelSearch pattern).
  → PARTIALLY: DAG-based decomposition (some parallel, some dependent).
  → NO: Continue.

Is there a natural simple-to-complex ordering?
  → YES: Least-to-Most prompting.
  → NO: Continue.

Is the query multi-hop factual?
  → YES: Self-Ask + Search.
  → NO: Plan-and-Solve for general decomposition.
```

The key insight from production experience (Harrison Chase, LangChain): domain-specific decomposition strategies consistently outperform general-purpose planning. When building research for a specific domain, embed decomposition decisions in deterministic control flow rather than delegating entirely to the LLM.
