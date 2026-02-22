---
description: Audit an entire Python package repository for best-practice compliance — systematically scans the codebase for structure, configuration, typing, testing, CI/CD, documentation, and security issues
disable-model-invocation: true
argument-hint: "[path-or-scope]"
---

Perform a comprehensive audit of the entire Python package repository (or the scope provided as argument).

Follow this process:

1. **Discover the package**: Use Glob and Read to understand the repository structure:
   - Identify whether it uses src/ or flat layout
   - Map the directory structure and module boundaries
   - Locate pyproject.toml, setup.py/setup.cfg (if any legacy files remain)
   - Identify CI configuration, documentation, and test directories
   - Check for py.typed marker, __init__.py files, _internal/ convention

2. **Sample strategically**: Read key files:
   - pyproject.toml (always — this is the most important file)
   - __init__.py files (check __all__, public API surface)
   - Configuration files (ruff, mypy, pytest sections in pyproject.toml)
   - CI workflows (.github/workflows/)
   - Documentation config (mkdocs.yml or conf.py)
   - SECURITY.md, CONTRIBUTING.md, CHANGELOG.md
   - 3-5 representative source files from the main package
   - 2-3 test files

3. **Establish the package's current state**: Before flagging violations, document what the package already does well:
   - Which modern standards it follows
   - What tooling is already configured
   - What patterns are established

4. **For each python-package principle**, invoke the corresponding skill and audit:
   - Project Structure — src/ layout, __init__.py, py.typed, _internal/
   - pyproject.toml — PEP 621 metadata, build backend, dependency groups, SPDX license
   - Code Quality — Ruff config, mypy strict, modern type hints
   - Testing Strategy — pytest config, coverage, fixtures, strict mode
   - CI/CD — GitHub Actions, test matrix, trusted publishing, caching
   - Documentation — MkDocs Material, Diataxis, docstrings
   - Versioning & Releases — SemVer, changelog, deprecation policy
   - API Design — __all__, progressive disclosure, exception hierarchy
   - Packaging & Distribution — wheels, platform tags, package size
   - Security & Supply Chain — OIDC, Sigstore, SECURITY.md, dependency scanning
   - Developer Experience — one-command setup, CONTRIBUTING.md, Makefile

5. **Report findings** in this structure:

   ### Package Overview
   - Package name, layout, Python version support, build backend, total source files

   ### Current Strengths
   - What the package already does well (acknowledge compliance)

   ### Findings by Principle
   For each principle with violations:
   - **[Principle Name]** — X violations
   - Specific findings with file:line references
   - Whether this is a systemic issue or isolated
   - The fix (show before/after for configurations)

   ### Migration Path
   - If legacy patterns exist (setup.py, setup.cfg), outline migration steps
   - Prioritized list of changes by impact

   ### Summary
   - Severity counts: Critical / Important / Suggestion
   - Top 5 highest-impact improvements
   - Overall package health: exemplary / solid / adequate / needs-work / non-compliant
   - One-paragraph verdict

Focus on actionable improvements with the highest impact. A missing trusted publishing setup matters more than a slightly suboptimal Ruff rule.
