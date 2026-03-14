# Artifact Evaluation Signals — Detailed Reference

This reference provides detailed guidance on evaluating non-content artifacts encountered during research. Consult when assessing software packages, tools, technologies, standards, or any recommendation that involves choosing between alternatives.

## The Three-Dimension Framework

Every artifact evaluation applies three signal dimensions:

1. **Health** — Is this artifact alive, maintained, and evolving?
2. **Adoption** — Do real users/organizations actually use this?
3. **Authority** — Who created/maintains this, and are they credible?

An artifact must score acceptably on all three dimensions. A widely-adopted but unmaintained package (high adoption, low health) is a ticking time bomb. A well-maintained but unused tool (high health, low adoption) may lack battle-testing.

---

## Software Packages (npm, PyPI, crates, gems)

### Health Signals

| Signal | How to Check | Healthy | Warning | Critical |
|--------|-------------|---------|---------|----------|
| **Last release** | Package registry page | <3 months | 3-12 months | >12 months with open issues |
| **Release frequency** | Changelog / release history | Regular (monthly-quarterly) | Sporadic | Single release, then silence |
| **Open issue response** | GitHub issues tab | Maintainer responds within days | Weeks | Months or never |
| **Dependency freshness** | Package manifest | Dependencies up to date | Some outdated | Major outdated/vulnerable deps |
| **CI status** | GitHub Actions / badges | Passing on main | Flaky | No CI at all |

### Adoption Signals

| Signal | How to Check | Strong | Moderate | Weak |
|--------|-------------|--------|----------|------|
| **Downloads** | npm weekly / PyPI monthly stats | >100K/week (npm), >50K/month (PyPI) | 1K-100K | <1K |
| **Dependents** | "Used by" on GitHub / npm dependents | >100 dependents | 10-100 | <10 |
| **Stars** | GitHub repo | >5,000 | 500-5,000 | <500 |
| **Stack Overflow** | Tagged questions | Active tag with answers | Some questions | No presence |

### Authority Signals

| Signal | How to Check | Strong | Moderate | Weak |
|--------|-------------|--------|----------|------|
| **Maintainer** | GitHub profile / org page | Known org (Meta, Google, Vercel) or established OSS maintainer | Active individual with history | Anonymous, no other projects |
| **Contributors** | GitHub contributors tab | 10+ contributors | 3-10 | 1 (bus factor = 1) |
| **License** | Package manifest / LICENSE file | Standard OSS (MIT, Apache 2.0, BSD) | Copyleft (GPL) — depends on use case | No license, custom license, or SSPL |
| **Security** | npm audit / safety / Snyk | No known vulnerabilities | Low-severity only | Unpatched high-severity CVEs |

### How to Check Package Health Quickly

For npm packages:
```
Search: "[package-name] npm" → check weekly downloads, last publish date
Search: "site:github.com [package-name]" → check stars, last commit, open issues
```

For PyPI packages:
```
Search: "[package-name] pypi" → check monthly downloads, last release
Search: "site:github.com [package-name]" → check repo health
```

For Rust crates:
```
Search: "[crate-name] crates.io" → check downloads, last update
```

---

## GitHub Repositories

### Health Signals

| Signal | How to Check | Healthy | Warning | Critical |
|--------|-------------|---------|---------|----------|
| **Last commit** | GitHub main page | <1 month | 1-6 months | >6 months |
| **PR merge time** | Recent closed PRs | Days | Weeks | Months or unmerged |
| **Issue triage** | Issues tab, filter by open | Labeled, responded to | Some response | Hundreds of untriaged issues |
| **Branch protection** | Repo settings (if visible) | Required reviews, CI checks | Some protection | Direct push to main |
| **Test coverage** | CI config, badges | Visible coverage (>60%) | Tests exist but no coverage metric | No tests |

### The 17-Star Test

The user's example: a repo with 17 stars and 9 months since last push. Evaluation:

- **Health:** Critical — 9 months inactive with no indication of planned maintenance
- **Adoption:** Weak — 17 stars suggests minimal real-world usage
- **Authority:** Check maintainer profile — if an established developer's side project, may be higher quality than stars suggest; if anonymous, avoid

**Verdict:** Flag as high-risk. Search for actively maintained alternatives. If no alternative exists, note the risk explicitly: "The only available package for X is [name] (17 stars, last updated [date]). Consider vendoring or maintaining a fork."

---

## APIs and Services

### Health Signals

| Signal | How to Check | Healthy | Warning | Critical |
|--------|-------------|---------|---------|----------|
| **Uptime** | Status page, third-party monitors | >99.9% | 99-99.9% | <99% or no status page |
| **API versioning** | Docs, changelog | Versioned with deprecation policy | Versioned but breaking changes | Unversioned or frequent breaking changes |
| **Documentation** | API docs site | Comprehensive, up to date, examples | Exists but gaps | Minimal or outdated |
| **Changelog** | Blog, docs, GitHub releases | Regular updates | Sporadic | No changelog |

### Adoption Signals

| Signal | How to Check | Strong | Moderate | Weak |
|--------|-------------|--------|----------|------|
| **Customer logos** | Website, case studies | Named enterprise customers | Startups, smaller companies | No public customers |
| **Integrations** | Marketplace, partner page | 50+ integrations | 10-50 | <10 |
| **Community** | Discord, forum, Stack Overflow | Active community, responsive | Some activity | Ghost town |
| **Pricing stability** | Pricing page history (Wayback Machine) | Stable for 12+ months | Recent changes | Frequent changes or opaque pricing |

### Authority Signals

| Signal | How to Check | Strong | Moderate | Weak |
|--------|-------------|--------|----------|------|
| **Company** | Crunchbase, LinkedIn | Established company, known team | Funded startup | Unknown entity |
| **Funding** | Crunchbase | Series B+ or profitable | Seed/Series A | No funding info |
| **SOC 2 / compliance** | Security page | SOC 2 Type II, GDPR | In progress | No compliance info |

---

## Technologies and Languages

### Health Signals

| Signal | How to Check | Healthy | Warning | Critical |
|--------|-------------|---------|---------|----------|
| **Release cadence** | Official site, GitHub | Regular releases (quarterly+) | Annual | >18 months since last release |
| **Roadmap** | Official blog, RFC process | Public roadmap, active RFCs | Some visibility | No roadmap |
| **CVE response** | Security advisories | Rapid patches (<72h critical) | Reasonable (weeks) | Slow or unpatched |

### Adoption Signals

| Signal | How to Check | Strong | Moderate | Weak |
|--------|-------------|--------|----------|------|
| **Stack Overflow Survey** | Annual developer survey | Top 20 in usage | Top 50 | Not listed |
| **Job postings** | LinkedIn, Indeed | >10K open positions | 1K-10K | <1K |
| **TIOBE / RedMonk** | Index websites | Top 20 | Top 50 | Declining or unlisted |
| **GitHub trending** | GitHub Explore | Trending in past year | Some activity | No traction |

### Authority Signals

| Signal | How to Check | Strong | Moderate | Weak |
|--------|-------------|--------|----------|------|
| **Backing** | Official site | Major org (Google, Mozilla, Apple, Microsoft) | Funded foundation | Single individual or small team |
| **Governance** | Governance docs | Open governance, multiple stakeholders | Foundation-led | BDFL with no succession plan |
| **Ecosystem** | Package registries | Rich ecosystem (thousands of packages) | Growing | Sparse |

---

## Standards and Specifications

### Health Signals

| Signal | How to Check | Healthy | Warning | Critical |
|--------|-------------|---------|---------|----------|
| **Status** | Standards body website | Published standard / recommendation | Proposed / draft | Expired / withdrawn |
| **Last revision** | Spec document | <2 years for active domain | 2-5 years | >5 years with known gaps |
| **Errata/updates** | Standards body | Active errata process | Some updates | Frozen |

### Adoption Signals

| Signal | How to Check | Strong | Moderate | Weak |
|--------|-------------|--------|----------|------|
| **Implementations** | Conformance tests, ecosystem | 3+ independent implementations | 1-2 implementations | Reference implementation only |
| **Industry support** | Member lists, announcements | Multiple major vendors committed | Some vendor support | Single vendor pushing it |

---

## Claims and Statistics

When research surfaces specific claims ("X% of companies use Y", "Y improves Z by N%"), evaluate the claim itself as an artifact:

| Signal | What to Check | Trustworthy | Suspicious |
|--------|--------------|-------------|------------|
| **Original source** | Can you find the primary study? | Yes, with methodology | Circular citations, no primary found |
| **Methodology** | How was the data collected? | Described, reasonable sample | Undescribed, self-selected, or <100 sample |
| **Funding** | Who paid for the study? | Independent / academic | Vendor-funded studying their own product |
| **Date** | When was data collected? | <2 years for tech topics | >3 years for fast-moving domains |
| **Replication** | Has anyone reproduced it? | Yes, consistent results | No replication, or contradicted |

**Rule:** When a claim's original source cannot be found, do not propagate it. State: "This claim is widely cited but the original source could not be verified."

---

## Artifact Evaluation in Research Output

When recommending or reporting on artifacts, include the evaluation signals in the output:

**Good:**
> `fastapi` (75K+ stars, 700+ contributors, monthly releases, backed by Sebastián Ramírez with corporate sponsors) is the leading choice for async Python APIs.

**Bad:**
> `fastapi` is a popular framework for building APIs.

**For risky artifacts:**
> `obscure-lib` (42 stars, last commit 8 months ago, single maintainer) is the only package addressing this specific need. Consider vendoring or evaluating maintenance risk before adopting as a dependency.

---

## Quick Evaluation Checklist

Before recommending any artifact in research output:

- [ ] **Health:** Last meaningful activity within 6 months?
- [ ] **Adoption:** Evidence of real-world usage beyond the maintainer?
- [ ] **Authority:** Credible maintainer/organization behind it?
- [ ] **Alternatives:** Compared against at least 2 alternatives?
- [ ] **Red flags:** Checked for bus factor, licensing, security issues?
- [ ] **Disclosed:** Any risks or caveats noted in the recommendation?
