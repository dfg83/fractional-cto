---
description: Review the current Python package for best-practice violations — project structure, pyproject.toml, typing, testing, CI/CD, documentation, versioning, API design, packaging, security, and developer experience
disable-model-invocation: true
---

Review the Python package currently being worked on against the python-package principles.

Follow this process:

1. Identify which python-package areas are relevant to the current context (project structure, pyproject.toml, code quality, testing, CI/CD, documentation, versioning, API design, packaging, security, developer experience)
2. For each relevant area, invoke the corresponding python-package skill
3. Evaluate the current code and configuration against each skill's review checklist
4. Report findings organized by principle, using this format for each:

**[Principle Name]**
- Violations found (with specific file/line references)
- What to fix and how (show the correct configuration or code)
- Items that already comply

5. Provide a summary with:
   - Total violations count by severity (critical / important / suggestion)
   - Top 3 most impactful fixes to make first
   - Overall package health score (exemplary / solid / adequate / needs-work / non-compliant)

Severity guide:
- **Critical**: Deviations from PEPs, missing pyproject.toml fields, no type checking, no CI, security vulnerabilities
- **Important**: Suboptimal configuration, missing coverage thresholds, incomplete documentation structure, poor API surface design
- **Suggestion**: Minor improvements, better naming, additional checklist items, optimization opportunities

Focus on concrete, specific violations. Every finding must reference the exact principle and PEP/standard being violated. No vague "consider improving" — state what is wrong and what the fix is.
