# Python Standards

## Script Metadata (PEP 723)

All Python scripts must use inline metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["dependency-name"]
# ///
```

## Type Hints

- All functions must have type hints
- Use `dict[str, Any]` not `Dict[str, Any]`
- Use `list[str]` not `List[str]`

## Hook Protocol

Hooks communicate via JSON stdin/stdout:

```python
import json
import sys

def main() -> None:
    data = json.load(sys.stdin)
    result = process(data)
    json.dump(result, sys.stdout)
```

Return `{"continue": true}` to allow actions.

## Forbidden

- No `pip install` - use PEP 723 dependencies
- No `requirements.txt` - use inline metadata
- No `venv` - use `uv run --script`
- No global mutable state

## Style

- Use `pathlib.Path` not `os.path`
- Use `dataclasses` for structured data
- Format with `ruff format`
- Lint with `ruff check`

## Commands

```bash
uv run script.py
uv run ruff format .
uv run ruff check .
python -m py_compile script.py
```
