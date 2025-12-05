# Development Guide

Guide for contributing to GraphRAG MCP Server development.

## Development Setup

### Prerequisites

- Python 3.11+
- uv (recommended package manager)
- Git

### Clone and Install

```bash
# Clone repository
git clone https://github.com/your-org/graphrag-mcp-server.git
cd graphrag-mcp-server

# Install with all development dependencies
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate
```

### IDE Setup

#### VS Code

Recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

## Project Structure

```
graphrag-mcp-server/
├── src/
│   └── graphrag_mcp_server/
│       ├── __init__.py          # Package exports
│       ├── server/              # MCP server core
│       │   ├── __init__.py
│       │   └── app.py           # FastMCP application
│       ├── handlers/            # Tool handlers
│       │   ├── __init__.py
│       │   ├── search.py        # Search operations
│       │   └── index.py         # Index operations
│       ├── cli/                 # CLI commands
│       │   ├── __init__.py
│       │   ├── main.py          # Main entry point
│       │   ├── serve.py         # Serve command
│       │   └── query.py         # Query commands
│       ├── config/              # Configuration
│       │   ├── __init__.py
│       │   └── settings.py      # Settings management
│       ├── errors.py            # Error definitions
│       └── prompts.py           # Prompt templates
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test fixtures
├── docs/                        # Documentation
├── examples/                    # Example configurations
├── pyproject.toml               # Project configuration
└── README.md
```

## Code Style

### Formatting

We use Ruff for formatting and linting:

```bash
# Format code
uv run ruff format

# Check linting
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix
```

### Type Checking

We use mypy for type checking:

```bash
uv run mypy src/
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
uv run pre-commit install
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=graphrag_mcp_server --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_search.py

# Run with verbose output
uv run pytest -v --tb=short
```

### Writing Tests

```python
# tests/unit/test_example.py
import pytest
from unittest.mock import MagicMock, patch

from graphrag_mcp_server.handlers.search import handle_global_search


class TestGlobalSearch:
    """Tests for global search handler."""

    @pytest.mark.asyncio
    async def test_global_search_success(self):
        """Test successful global search."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            mock_settings.return_value.index_path.exists.return_value = True
            
            result = await handle_global_search(query="test query")
            
            assert result.metadata["search_type"] == "global"

    @pytest.mark.asyncio
    async def test_global_search_missing_index(self):
        """Test global search with missing index."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_settings:
            mock_settings.return_value.index_path.exists.return_value = False
            
            with pytest.raises(IndexNotFoundError):
                await handle_global_search(query="test query")
```

### Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Unit | `tests/unit/` | Test individual functions/classes |
| Integration | `tests/integration/` | Test component interactions |
| Fixtures | `tests/fixtures/` | Shared test data |

## Adding Features

### Adding a New Tool

1. Define handler in `src/graphrag_mcp_server/handlers/`:

```python
# handlers/new_feature.py
from dataclasses import dataclass
from graphrag_mcp_server.config import get_settings

@dataclass
class NewFeatureResult:
    data: str
    metadata: dict

async def handle_new_feature(param: str) -> NewFeatureResult:
    """Handle new feature request."""
    settings = get_settings()
    # Implementation
    return NewFeatureResult(data="result", metadata={})
```

2. Register in `src/graphrag_mcp_server/tools.py`:

```python
NEW_FEATURE_TOOL = {
    "name": "graphrag_new_feature",
    "description": "Description of new feature",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    }
}

ALL_TOOLS = [..., NEW_FEATURE_TOOL]
```

3. Add handler routing in `src/graphrag_mcp_server/server/app.py`:

```python
@mcp.tool()
async def graphrag_new_feature(param: str) -> list[TextContent]:
    result = await handle_new_feature(param)
    return [TextContent(type="text", text=str(result))]
```

4. Add tests:

```python
# tests/unit/test_new_feature.py
@pytest.mark.asyncio
async def test_new_feature():
    result = await handle_new_feature("test")
    assert result.data == "expected"
```

### Adding a New Prompt

1. Add to `src/graphrag_mcp_server/prompts.py`:

```python
NEW_PROMPT = {
    "name": "graphrag_new_prompt",
    "description": "Description",
    "arguments": [
        {"name": "arg1", "description": "Argument description", "required": True}
    ]
}

def get_new_prompt_messages(arg1: str) -> list[dict]:
    return [
        {"role": "user", "content": f"Prompt with {arg1}"}
    ]
```

2. Register in server app.

## Documentation

### Building Docs

```bash
# Install documentation dependencies
uv sync --extra docs

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

### Documentation Style

- Use Markdown for all documentation
- Include code examples with syntax highlighting
- Add API reference for new features
- Update CHANGELOG.md for changes

## Release Process

### Version Bump

```bash
# Bump version (uses semantic versioning)
uv run bump2version patch  # 0.1.0 -> 0.1.1
uv run bump2version minor  # 0.1.0 -> 0.2.0
uv run bump2version major  # 0.1.0 -> 1.0.0
```

### Create Release

```bash
# Create git tag
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1

# Build package
uv build

# Publish to PyPI (if configured)
uv publish
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Test failures**: Check that mock fixtures are up to date
3. **Type errors**: Run `mypy src/` to check types

### Getting Help

- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation
