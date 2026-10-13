# Git Conventions

## Branch Strategy
| Branch | Purpose | Protection |
|--------|---------|------------|
| main | Stable release | Require PR + review |
| dev | Development | Require PR |
| feat/* | Feature work | None |
| fix/* | Bug fixes | None |

## Commit Format
```
type(scope): description
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `docs`: Documentation only
- `chore`: Build, config, tooling

### Rules
- Imperative mood: "add feature" not "added feature"
- No period at end
- Scope is module name (core/ui/viewmodel/utils)

## PR Rules
- Title follows commit format
- Description includes: what, why, how to test
- Squash merge to main/dev
- Delete branch after merge
