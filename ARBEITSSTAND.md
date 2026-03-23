# fractional-cto Integration

**Repository:** https://github.com/dfg83/fractional-cto  
**Hinzugefügt:** 22.03.2026

## Überblick

fractional-cto ist ein umfangreiches Claude Code Plugin-System mit **93 Skills**, **15 Commands** und **16 Agents** für SaaS Engineering. Es bietet research-backed Best Practices für:

- SaaS Design Principles
- Visual Design Principles  
- API Design Principles
- Cloud Foundation Principles
- Code Quality (Pedantic Coder)
- Python Packaging
- Deep Research
- Structured Brainstorming
- Und mehr...

## Struktur

```
fractional-cto/
├── saas-design-principles/      # 13 skills, 1 command, 1 agent
├── visual-design-principles/    # 12 skills, 1 command, 1 agent
├── api-design-principles/       # 13 skills, 1 command, 1 agent
├── cloud-foundation-principles/ # 16 skills, 1 command, 1 agent
├── pedantic-coder/              # 16 skills, 3 commands, 1 agent
├── python-package/              # 13 skills, 2 commands, 1 agent
├── deep-research/               # 5 skills, 1 command, 3 agents
├── structured-brainstorming/    # 1 skill, 1 command, 1 agent
├── retell/                      # 2 skills, 1 command, 2 agents
├── markdown-compressor/         # 1 skill, 2 commands, 2 agents
└── stress-test/                 # 1 skill, 1 command, 2 agents
```

## Verwendung

### Für Claude Code/Cowork
```bash
# Marketplace hinzufügen
/plugin marketplace add oborchers/fractional-cto

# Einzelne Plugins installieren
/plugin install saas-design-principles@fractional-cto
/plugin install api-design-principles@fractional-cto
```

### Für OpenClaw (Skill-Import)
Die SKILL.md Dateien in jedem Plugin-Ordner folgen dem universellen Skill-Format und können direkt verwendet werden.

## Wichtige Commands

| Command | Plugin | Beschreibung |
|---------|--------|--------------|
| `/saas-review` | saas-design-principles | Review gegen SaaS Design Principles |
| `/design-review` | visual-design-principles | 8-Dimension Scoring für Visual Design |
| `/api-review` | api-design-principles | API Design Review |
| `/cloud-foundation-review` | cloud-foundation-principles | Infrastructure Review |
| `/pedantic-review` | pedantic-coder | Code Pedantry Review |
| `/research <topic>` | deep-research | Paralleles Web Research |
| `/brainstorm` | structured-brainstorming | Strukturiertes Brainstorming |
| `/stress-test <plan>` | stress-test | Adversarial Plan Review |

## Auto-Sync

**Noch nicht eingerichtet.**

Mögliche Cronjob-Konfiguration:
```bash
# Täglich um 03:00 CET
openclaw cron create \
  --name "fractional-cto-sync" \
  --schedule "0 3 * * *" \
  --timezone Europe/Berlin \
  --command "cd ~/.openclaw/workspace/projects/fractional-cto && git pull" \
  --session isolated
```

## Dokumentation

- Haupt-README: `projects/fractional-cto/README.md`
- Plugin-Manifeste: `*/.claude-plugin/plugin.json`
- Skill-Dateien: `*/skills/*/SKILL.md`
