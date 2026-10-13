# Architecture Conventions

## MVVM Layers
```
core (Model)  →  viewmodel (ViewModel)  →  ui (View)
  business       data binding + commands     CustomTkinter
  logic          observable pattern          widgets
```

## Rules
- **Dependency direction**: ui → viewmodel → core only
- **No cross-layer imports**: ui never imports core directly
- **ViewModel mediates**: View only talks to ViewModel, never to Model
- **Observable pattern**: ViewModel extends Observable, View subscribes to changes
- **Core is pure**: no GUI imports in core/ or viewmodel/

## Module Boundaries
- Each module has a clear public API (`__all__`)
- Internal symbols are prefixed with `_`
- Cross-module access through public API only

## Forbidden Patterns
- UI code in core/ (no ctk imports in business logic)
- Core imports in ui/ (must go through viewmodel)
- God classes with >10 methods
- Circular dependencies between modules
- Hardcoded config values (use config/default.json)
