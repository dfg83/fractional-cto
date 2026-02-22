# fractional-cto

Your AI CTO co-pilot -- opinionated, research-backed Claude Code plugins for building SaaS products that ship.

## About

Built by [Dr. Oliver Borchers](https://linkedin.com/in/oliverborchers) -- AI engineering lead by day, former startup CTO, open-source tinkerer ([fse](https://github.com/oborchers/Fast_Sentence_Embeddings)). I got tired of giving the same design reviews and architecture feedback across projects, so I turned them into Claude Code skills that kick in automatically.

## Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| **[saas-design-principles](./saas-design-principles)** | 12 | Speed, navigation, forms, tables, auth, accessibility, theming, responsive design, and more -- drawn from Linear, Stripe, Shopify Polaris, and Nielsen Norman Group research |
| **[api-design-principles](./api-design-principles)** | 12 | Routes, errors, auth, pagination, caching, webhooks, versioning, and more -- drawn from Stripe, GitHub, Twilio, Google, OWASP, and industry RFCs |
| **[pedantic-coder](./pedantic-coder)** | 16 | Zero-tolerance code pedantry -- naming precision, casing law, structural symmetry, import discipline, CLAUDE.md guidelines compliance, plus language packs for Python, TypeScript, and Go |
| **[python-package](./python-package)** | 12 | Research-backed Python packaging -- project structure, pyproject.toml, Ruff/mypy, pytest, CI/CD, MkDocs, versioning, API design, wheels, supply chain security, developer experience |

Each plugin includes principle skills with review checklists, working code examples, review commands, a reviewer agent, and a session hook that loads the skill index on startup.

## Installation

### Claude Code

Register the marketplace once:

```bash
/plugin marketplace add oborchers/fractional-cto
```

Then install any plugin:

```bash
/plugin install saas-design-principles@fractional-cto
/plugin install api-design-principles@fractional-cto
/plugin install pedantic-coder@fractional-cto
/plugin install python-package@fractional-cto
```

### Local Development

Test a specific plugin directly:

```bash
claude --plugin-dir /path/to/fractional-cto/saas-design-principles
claude --plugin-dir /path/to/fractional-cto/api-design-principles
claude --plugin-dir /path/to/fractional-cto/pedantic-coder
claude --plugin-dir /path/to/fractional-cto/python-package
```

## Adding Future Plugins

New plugins go in their own subdirectory with a `.claude-plugin/plugin.json` manifest. Register them in `.claude-plugin/marketplace.json` by adding an entry to the `plugins` array.

## License

MIT
