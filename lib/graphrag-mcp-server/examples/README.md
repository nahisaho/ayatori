# VS Code MCP Configuration Examples

This directory contains example MCP configuration files for different LLM providers.

## Usage

Copy the appropriate configuration file to your VS Code workspace `.vscode/mcp.json`:

```bash
# For OpenAI
cp examples/vscode-mcp.json .vscode/mcp.json

# For Azure OpenAI
cp examples/vscode-mcp-azure.json .vscode/mcp.json

# For Ollama (local)
cp examples/vscode-mcp-ollama.json .vscode/mcp.json
```

## Configuration Files

| File | Provider | Description |
|------|----------|-------------|
| `vscode-mcp.json` | OpenAI | Standard OpenAI API configuration |
| `vscode-mcp-azure.json` | Azure OpenAI | Azure OpenAI Service configuration |
| `vscode-mcp-ollama.json` | Ollama | Local LLM using Ollama |

## Environment Variables

Make sure to set the required environment variables:

### OpenAI
```bash
export OPENAI_API_KEY="your-api-key"
```

### Azure OpenAI
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
```

### Ollama
No API key required. Make sure Ollama is running:
```bash
ollama serve
```

## Index Path

Update `GRAPHRAG_INDEX_PATH` to point to your GraphRAG index directory.
The default is `${workspaceFolder}/graphrag_index`.
