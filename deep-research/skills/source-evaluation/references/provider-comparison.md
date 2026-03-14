# Search Provider Comparison — Detailed Reference

This reference provides detailed comparison of search providers for deep research agents. Consult when selecting providers for a research task.

## General Web Search

### Tavily Search API

**What it is:** Purpose-built search API for AI agents and research systems. Designed to return clean, relevant content optimized for LLM consumption rather than ad-driven web results.

**Key features:**
- Standard search endpoint returns relevant URLs with content summaries
- Extract endpoint pulls full content from specific URLs
- Returns structured JSON optimized for LLM context
- Supports search depth configuration (basic vs. advanced)

**Best for:** General-purpose research, technical topics, current events. De facto standard for LangGraph and CrewAI integrations.

**Architectural contribution:** Tavily's most important insight is the reflection/distillation pattern — distilling tool outputs into reflections and propagating only reflections reduces token consumption from quadratic to linear growth. This single technique reduced tokens by 66% versus Open Deep Research while achieving state-of-the-art quality on the DeepResearch Bench.

**Source:** [Tavily documentation](https://tavily.com); [DeepResearch Bench results](https://blog.tavily.com)

### Exa (Neural Search)

**What it is:** Neural search engine that uses embeddings for semantic matching rather than keyword-based retrieval.

**Key features:**
- Semantic search mode (meaning-based, not keyword-based)
- Keyword search mode (traditional BM25-style)
- Auto mode (combines both)
- Content extraction from matched URLs

**Best for:** Finding conceptually similar content, research where exact keywords are unknown, exploring adjacent topics.

### Standard Search (Google, Bing, DuckDuckGo)

**When to use:** Broad coverage, recent events, specific URL lookup. These optimize for human engagement metrics which may not correlate with research quality.

**Limitations for research:** SEO-optimized results, ad-mixed rankings, content farm prominence.

## Academic Search

### Semantic Scholar API

**What it is:** AI-powered academic search engine by the Allen Institute for AI. Indexes 225M+ papers across all academic disciplines.

**Key features:**
- Paper search by keyword, title, or author
- Citation graph traversal (references and citations)
- Paper details including abstract, year, citation count, venue
- Author profiles and publication lists
- Open access PDF links where available

**Best for:** Finding academic papers, understanding citation networks, literature reviews, verifying paper existence.

**API details:** Free tier with rate limits. Endpoints for paper search, paper details, author search, recommendations.

**Source:** [Semantic Scholar API docs](https://api.semanticscholar.org/)

### arXiv

**What it is:** Open-access preprint repository for physics, mathematics, computer science, and related fields. Most ML/AI papers appear here before (or instead of) journal publication.

**Key features:**
- Full-text search across titles, abstracts, and paper content
- Category-based browsing (cs.AI, cs.CL, cs.LG, etc.)
- Direct PDF access
- arXiv API for programmatic access

**Best for:** ML/AI research, preprints, cutting-edge results not yet in journals.

**Limitation:** Not peer-reviewed. Papers may be superseded by later versions. Quality varies.

### Google Scholar

**What it is:** Google's academic search engine. Broader coverage than Semantic Scholar but less structured API access.

**Best for:** Cross-disciplinary search, finding papers that cite a known paper, author impact metrics.

**Limitation:** No official API; scraping is against ToS. Better accessed via WebSearch with `site:scholar.google.com` queries.

## Domain-Specific Search

### PubMed / PubMed Central

**What it is:** Free search engine for biomedical and life sciences literature maintained by the National Library of Medicine (NLM).

**Key features:**
- E-utilities API for programmatic access
- MeSH (Medical Subject Headings) for controlled vocabulary search
- Links to full-text articles in PubMed Central
- Clinical trial data linkage

**Best for:** Medical research, drug interactions, clinical outcomes, public health, biology.

**Source:** [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)

### OpenAlex

**What it is:** Open-source academic knowledge graph with 250M+ works. Free and open alternative to proprietary academic databases.

**Key features:**
- REST API with no authentication required
- Concept-based search
- Institution and author linkage
- Full citation graph

**Best for:** Large-scale bibliometric analysis, when Semantic Scholar rate limits are a concern, open-access-first research.

**Source:** [OpenAlex documentation](https://docs.openalex.org/)

## Provider Selection by Domain

| Research Domain | Primary Provider | Secondary Provider | Avoid |
|----------------|-----------------|-------------------|-------|
| **ML/AI** | arXiv, Semantic Scholar | Tavily (for blog posts, docs) | Generic web search alone |
| **Medical/Clinical** | PubMed | Semantic Scholar | Wikipedia for medical claims |
| **Legal** | Government databases, court opinion DBs | Tavily for analysis articles | Content farms |
| **Technical/Engineering** | Official documentation, GitHub | Tavily, Stack Overflow (high-score) | Tutorial sites without attribution |
| **Business/Market** | Industry reports, SEC filings | Tavily for news coverage | Affiliate marketing sites |
| **General Knowledge** | Tavily | Wikipedia (for orientation only, not citation) | Anonymous forums |

## Provider Orchestration Pattern

For comprehensive research, use a multi-provider strategy:

1. **Orientation search** — Broad web search to understand the landscape and identify key terms
2. **Authority search** — Domain-specific providers (Semantic Scholar, PubMed) for primary sources
3. **Expert search** — Targeted web search for engineering blogs, conference talks, expert analysis
4. **Gap-filling search** — Additional web searches to fill specific information gaps

This four-phase approach front-loads high-quality sources (addressing the saturation bottleneck) while ensuring broad coverage.
