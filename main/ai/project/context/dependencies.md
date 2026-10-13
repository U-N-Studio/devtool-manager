# Dependencies

## Dependency Graph
```
customtkinter → ui/app.py → ui/*_tab.py
                          → ui/widgets.py
                          → ui/fonts.py

src/core/* ← src/viewmodel/* ← src/ui/*
src/utils/* ← src/core/* (logger)
src/utils/* ← src/viewmodel/* (logger, python_finder)
```

## Key Relationships
- `ui/app.py` is the root — owns all tabs and viewmodels
- Each `ui/*_tab.py` depends on its corresponding `viewmodel/*_viewmodel.py`
- `viewmodel/observable.py` is the base for all ViewModels
- `core/` has no UI dependencies (pure business logic)
- `utils/logger.py` is used across all layers

## Version Constraints
- customtkinter >=5.2 (for CTkScrollableFrame, theme support)
- Python >=3.9 (for `|` union type syntax)

## Adding Dependencies
1. Check if existing dependency can serve the purpose
2. Evaluate: maintenance activity, license compatibility
3. Add to `pyproject.toml` [project.dependencies]
4. Run `pip install -e .` and test
