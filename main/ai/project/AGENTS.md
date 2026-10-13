# AGENTS.md

## Project Identity

- **Name**: devtool-manager
- **Stack**: Python Desktop GUI
- **Language**: Python 3.9+
- **Runtime**: CPython

## Architecture

MVVM architecture with CustomTkinter GUI.

```
main/
├── src/
│   ├── core/          # Business logic: env.py, packages.py, commands.py, tools.py, executor.py
│   ├── ui/            # CustomTkinter GUI: app.py, env_tab.py, packages_tab.py, commands_tab.py
│   ├── viewmodel/     # MVVM ViewModels: observable.py, env/packages/commands/tool_info VMs
│   └── utils/         # Utilities: logger.py, python_finder.py
├── config/            # App config (default.json)
├── tests/             # Pytest
├── ai/                # Agent engineering docs
├── main.py            # Entry point
└── pyproject.toml
```

## Conventions

See `conventions/` for detailed rules:
- `coding.md` — Code style, naming, type hints
- `architecture.md` — MVVM layer boundaries, dependency rules
- `testing.md` — Test requirements, coverage thresholds
- `git.md` — Branch strategy, commit format, PR rules

## Context

See `context/` for project-specific knowledge:
- `tech-stack.md` — Frameworks, libraries, versions
- `dependencies.md` — Key dependency relationships
- `patterns.md` — Recurring patterns and idioms used

## Agent Rules

1. **Read conventions before writing code** — never assume style
2. **Respect MVVM boundaries** — core ↔ viewmodel ↔ ui, never skip a layer
3. **Run verification after changes** — ruff lint, pytest
4. **Commit only when asked** — never auto-commit
5. **Explain before acting** — on destructive operations, state intent first
