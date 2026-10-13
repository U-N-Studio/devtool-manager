# Testing Conventions

## Requirements
- All new code must have tests
- Bug fixes must include regression test
- Public API must have integration test

## Coverage
- Minimum: 80%
- Critical paths: 100%

## Test Structure
```
tests/
├── unit/           # Fast, isolated, no I/O
├── integration/    # With real dependencies
└── conftest.py     # Shared fixtures
```

## Naming
- Test files: `test_<module>.py`
- Test names: `test_<scenario>_<expected_result>`
- Use descriptive asserts

## Rules
- No shared mutable state between tests
- Each test is independent and repeatable
- Mock at boundaries only, not internals
- Test behavior, not implementation
- Use pytest fixtures for common setup
