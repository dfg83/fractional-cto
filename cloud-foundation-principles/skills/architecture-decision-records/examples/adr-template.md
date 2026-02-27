# ADR Template

A ready-to-use template for Architecture Decision Records. Copy this file when creating a new ADR.

## Template

```markdown
# ADR-XXXX: [Title -- Short, Descriptive Phrase]

**Status:** Proposed | Accepted | Superseded by ADR-XXXX | Deprecated
**Date:** YYYY-MM-DD
**Deciders:** [Team or individuals who made the decision]

## Context

[Describe the situation that prompted this decision. Include:]
- What problem or question arose?
- What constraints exist (technical, organizational, budget, timeline)?
- What alternatives were considered?
- What trade-offs were evaluated?

[Be specific. Future readers need enough context to understand WHY this
decision was necessary, not just WHAT was decided.]

## Decision

[State the decision clearly and unambiguously. This should be 1-3 sentences.]

[Include specifics: which tool/service/pattern was chosen, what was explicitly
rejected, and any conditions or scope limitations.]

## Consequences

### Positive
- [What becomes easier, safer, cheaper, or more maintainable?]

### Negative
- [What becomes harder, more expensive, or constrained?]
- [What new risks or limitations does this introduce?]

### Follow-Up Actions
- [ ] [Specific task required to implement this decision]
- [ ] [Documentation or communication needed]
- [ ] [Future review date or trigger condition]
```

## Rules for Using This Template

1. **Number sequentially** -- Never skip numbers. Never reuse numbers.
2. **One decision per ADR** -- If you find yourself documenting two decisions, write two ADRs.
3. **Keep it short** -- If an ADR exceeds one page, you are including implementation details that belong in code comments or a design doc.
4. **Never edit an accepted ADR** -- Write a new ADR that supersedes it. The original stays as historical record.
5. **Link related ADRs** -- Reference relevant ADRs in the Context section (e.g., "Building on the naming convention established in ADR-0002").

## Superseding an ADR

When a decision changes, create a new ADR:

```markdown
# ADR-0015: Switch from Redis to Managed Caching Service

**Status:** Accepted
**Date:** 2026-06-01
**Supersedes:** ADR-0008
**Deciders:** Platform Team

## Context

ADR-0008 selected self-hosted Redis for caching. After 4 months of operation,
we experienced three outages caused by Redis failover misconfigurations.
The managed caching service now supports our access patterns and costs $50/month
more than self-hosted.

## Decision

Migrate all caching workloads from self-hosted Redis to the cloud provider's
managed caching service. Complete migration within 2 weeks. ADR-0008 is
superseded.

## Consequences

### Positive
- Eliminates operational burden of Redis cluster management
- Automated failover reduces risk of cache-related outages

### Negative
- Monthly cost increases ~$50
- Slight latency increase due to managed service network path

### Follow-Up Actions
- [ ] Update ADR-0008 status to "Superseded by ADR-0015"
- [ ] Migrate dev environment first, validate for 3 days
- [ ] Migrate prod environment
- [ ] Remove self-hosted Redis Terraform module
```

Then update the original ADR's status line (this is the ONLY edit allowed):

```markdown
# ADR-0008: Use Self-Hosted Redis for Caching

**Status:** Superseded by ADR-0015    ← Only change: update the status line
**Date:** 2026-02-01
...
[Rest of the original ADR remains unchanged]
```

## File Naming Convention

```
ADR-0001-adopt-adrs.md
ADR-0002-naming-convention.md
ADR-0003-multi-account-strategy.md
ADR-0004-container-orchestration.md
...
```

The filename includes the number and a kebab-case slug of the title. This keeps them sorted in file browsers and makes them searchable.
