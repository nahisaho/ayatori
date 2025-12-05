# Deployment Guide

Guide for deploying GraphRAG MCP Server in various environments.

## Local Development

### Prerequisites

- Python 3.11+
- uv (recommended) or pip
- GraphRAG index (or sample data to build one)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/graphrag-mcp-server.git
cd graphrag-mcp-server

# Install with development dependencies
uv sync --all-extras

# Or with pip
pip install -e ".[dev]"
```

### Running Locally

```bash
# Serve with stdio transport
graphrag-mcp serve --transport stdio

# Serve with SSE transport
graphrag-mcp serve --transport sse --port 8080

# Build index from sample data
graphrag-mcp index /path/to/documents --full
```

## VS Code Integration

### Configure mcp.json

Create `.vscode/mcp.json` in your project:

```json
{
  "mcpServers": {
    "graphrag": {
      "command": "graphrag-mcp",
      "args": ["serve"],
      "env": {
        "GRAPHRAG_INDEX_PATH": "${workspaceFolder}/data/index",
        "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
      }
    }
  }
}
```

### Verify Installation

1. Open VS Code Command Palette (Ctrl+Shift+P)
2. Run "MCP: List Servers"
3. Verify "graphrag" appears in the list

## Claude Desktop Integration

### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "graphrag": {
      "command": "/path/to/graphrag-mcp",
      "args": ["serve"],
      "env": {
        "GRAPHRAG_INDEX_PATH": "/path/to/index"
      }
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "graphrag": {
      "command": "C:\\path\\to\\graphrag-mcp.exe",
      "args": ["serve"],
      "env": {
        "GRAPHRAG_INDEX_PATH": "C:\\path\\to\\index"
      }
    }
  }
}
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# Copy application
COPY src/ src/

# Set environment
ENV GRAPHRAG_INDEX_PATH=/data/index
ENV GRAPHRAG_TRANSPORT=sse
ENV GRAPHRAG_SSE_PORT=8080

EXPOSE 8080

CMD ["graphrag-mcp", "serve", "--transport", "sse", "--port", "8080"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  graphrag-mcp:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GRAPHRAG_INDEX_PATH=/data/index
    restart: unless-stopped
```

### Running with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f graphrag-mcp

# Connect client to http://localhost:8080/sse
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graphrag-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: graphrag-mcp
  template:
    metadata:
      labels:
        app: graphrag-mcp
    spec:
      containers:
      - name: graphrag-mcp
        image: your-registry/graphrag-mcp:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: graphrag-secrets
              key: openai-api-key
        - name: GRAPHRAG_INDEX_PATH
          value: /data/index
        volumeMounts:
        - name: index-data
          mountPath: /data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: index-data
        persistentVolumeClaim:
          claimName: graphrag-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: graphrag-mcp
spec:
  selector:
    app: graphrag-mcp
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
```

### Secrets

```bash
kubectl create secret generic graphrag-secrets \
  --from-literal=openai-api-key=sk-your-key
```

## Azure Container Apps

### Deploy with Azure CLI

```bash
# Create Container App Environment
az containerapp env create \
  --name graphrag-env \
  --resource-group myResourceGroup \
  --location eastus

# Deploy Container App
az containerapp create \
  --name graphrag-mcp \
  --resource-group myResourceGroup \
  --environment graphrag-env \
  --image your-registry/graphrag-mcp:latest \
  --target-port 8080 \
  --ingress external \
  --env-vars \
    OPENAI_API_KEY=secretref:openai-key \
    GRAPHRAG_INDEX_PATH=/data/index
```

## Health Checks

### Readiness Probe

```bash
# HTTP endpoint for health check
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "index_loaded": true,
  "llm_connected": true
}
```

### Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
```

## Monitoring

### Prometheus Metrics

```bash
# Enable metrics endpoint
export GRAPHRAG_METRICS_ENABLED=true
export GRAPHRAG_METRICS_PORT=9090
```

Metrics available at `http://localhost:9090/metrics`

### Key Metrics

| Metric | Description |
|--------|-------------|
| `graphrag_requests_total` | Total requests by tool |
| `graphrag_request_duration_seconds` | Request latency histogram |
| `graphrag_errors_total` | Total errors by type |
| `graphrag_index_size_bytes` | Current index size |

## Troubleshooting

### Common Issues

1. **Index not found**: Verify `GRAPHRAG_INDEX_PATH` points to valid index
2. **LLM connection failed**: Check API key and network connectivity
3. **Memory issues**: Increase container memory limits
4. **Slow queries**: Consider using Azure AI Search for large indexes

### Debug Mode

```bash
# Enable debug logging
export GRAPHRAG_LOG_LEVEL=DEBUG
graphrag-mcp serve --transport sse
```
