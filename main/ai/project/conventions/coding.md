# Coding Conventions

## Style
- Line length: 120
- Indentation: 4 spaces
- String quotes: single (Python)
- Trailing commas: yes

## Naming
- Classes: PascalCase
- Functions/Methods: snake_case
- Constants: UPPER_SNAKE_CASE
- Private members: _prefix
- Files: snake_case.py

## Type Hints
- All public functions must have type annotations
- Use `|` union syntax over `Union[]` (Python 3.10+)
- Prefer `str | None` over `Optional[str]`

## Imports
- Standard library → third-party → local (src.*)
- No wildcard imports (`from x import *`)
- Use `__all__` for public API

## Error Handling
- Never use bare `except:`
- Never swallow exceptions silently
- Log errors before re-raising (use src.utils.logger)
- Use custom exception classes for domain errors

## Functions
- Max 50 lines per function
- Single responsibility per function
- Early return to reduce nesting
- No boolean flag parameters
