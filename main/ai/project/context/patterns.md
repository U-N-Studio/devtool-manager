# Patterns & Idioms

## Recurring Patterns

### Observable Pattern
All ViewModels extend `Observable` and notify subscribers on state change:
```python
class SomeViewModel(Observable):
    def refresh(self):
        # ... update state ...
        self.notify()
```

### Tab-ViewModel Pairing
Each UI tab has a 1:1 ViewModel:
- `env_tab.py` ↔ `env_viewmodel.py`
- `packages_tab.py` ↔ `packages_viewmodel.py`
- `commands_tab.py` ↔ `commands_viewmodel.py`

### Command Pattern
CLI commands use `core/commands.py` + `core/command_probes.py` for detection and execution.

### Config-Driven
UI labels and tool metadata come from `config/default.json` and `core/config_glossary.py`.

## Anti-Patterns to Avoid
- Putting business logic in UI event handlers — delegate to ViewModel
- Directly calling core from UI — always go through ViewModel
- Creating new ViewModel instances per event — reuse the singleton
- Hardcoding paths — use `python_finder.py` for Python discovery
