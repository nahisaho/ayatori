# Tasks: GraphRAG MCP Server

**Feature ID**: FEAT-001
**Task Document Version**: 1.1
**Status**: ✅ Completed
**Created**: 2025-12-05
**Completed**: 2025-12-05
**Author**: @orchestrator

---

## 1. Task Overview

### 1.1 Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 24 |
| Estimated Hours | 56-72 hours |
| Implementation Phases | 5 |
| Critical Path | Phase 1 → Phase 2 → Phase 3 |

### 1.2 Phase Structure

| Phase | Name | Tasks | Hours | Dependencies |
|-------|------|-------|-------|--------------|
| 1 | Foundation | 5 | 8-10 | None |
| 2 | Core Server | 6 | 16-20 | Phase 1 |
| 3 | Search Handlers | 5 | 12-16 | Phase 2 |
| 4 | Index & Config | 4 | 10-14 | Phase 2 |
| 5 | Polish & Release | 4 | 10-12 | Phase 3, 4 |

---

## 2. Phase 1: Foundation (Days 1-2)

### Task 1.1: Project Scaffolding
**Priority**: P0 (Critical)
**Estimated Hours**: 2-3
**Requirements**: REQ-GMS-001

**Description**:
プロジェクト基盤の構築。pyproject.toml、ディレクトリ構造、型ヒントマーカーの作成。

**Deliverables**:
```
lib/graphrag-mcp-server/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/graphrag_mcp_server/
│   ├── __init__.py
│   ├── __main__.py
│   └── py.typed
└── tests/
    ├── __init__.py
    └── conftest.py
```

**Acceptance Criteria**:
- [x] `pip install -e .` が成功すること
- [x] `python -m graphrag_mcp_server --version` が動作すること
- [x] pytest が実行可能なこと

**TDD Sequence**:
1. RED: `test_package_import()` - パッケージインポートテスト
2. GREEN: `__init__.py` 作成
3. BLUE: リファクタリング

---

### Task 1.2: CLI Foundation
**Priority**: P0 (Critical)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-002

**Description**:
Typer ベースの CLI 基盤構築。serve, index, query, stats サブコマンドのスケルトン作成。

**Deliverables**:
```
src/graphrag_mcp_server/cli/
├── __init__.py
├── main.py      # typer.Typer() app
├── serve.py     # serve コマンド (stub)
├── index.py     # index コマンド (stub)
├── query.py     # query コマンド (stub)
└── stats.py     # stats コマンド (stub)
```

**Acceptance Criteria**:
- [x] `graphrag-mcp --help` でサブコマンド一覧表示
- [x] 各サブコマンドの `--help` が動作
- [x] 終了コード規約準拠 (0=成功)

**TDD Sequence**:
1. RED: `test_cli_help()`, `test_cli_serve_help()`
2. GREEN: Typer app 実装
3. BLUE: コマンド構造最適化

---

### Task 1.3: Configuration Module
**Priority**: P0 (Critical)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-005

**Description**:
Pydantic Settings ベースの設定管理。環境変数からの設定読み込み。

**Deliverables**:
```
src/graphrag_mcp_server/config/
├── __init__.py
├── settings.py   # GraphRAGMCPSettings (Pydantic BaseSettings)
└── providers.py  # LLMProviderConfig
```

**Environment Variables**:
```bash
GRAPHRAG_INDEX_PATH       # インデックスパス (required)
GRAPHRAG_LLM_PROVIDER     # openai | azure_openai | anthropic
GRAPHRAG_LLM_MODEL        # モデル名
GRAPHRAG_LLM_API_KEY      # API キー
GRAPHRAG_VECTOR_STORE     # lancedb | azure_search
```

**TDD Sequence**:
1. RED: `test_settings_from_env()`, `test_missing_required_env()`
2. GREEN: Pydantic Settings 実装
3. BLUE: バリデーションロジック整理

---

### Task 1.4: Error Handling Module
**Priority**: P1 (High)
**Estimated Hours**: 1
**Requirements**: REQ-GMS-030, REQ-GMS-031, REQ-GMS-032, REQ-GMS-033

**Description**:
カスタム例外クラスと MCP エラーレスポンスマッピング。

**Deliverables**:
```
src/graphrag_mcp_server/errors/
├── __init__.py
└── handlers.py
```

**Exception Classes**:
```python
class GraphRAGMCPError(Exception): ...
class IndexNotFoundError(GraphRAGMCPError): ...
class LLMProviderError(GraphRAGMCPError): ...
class ValidationError(GraphRAGMCPError): ...
class TokenBudgetExceededError(GraphRAGMCPError): ...
```

**TDD Sequence**:
1. RED: `test_error_mapping_to_mcp()`
2. GREEN: 例外クラス実装
3. BLUE: エラーメッセージ改善

---

### Task 1.5: Test Infrastructure
**Priority**: P0 (Critical)
**Estimated Hours**: 1-2
**Requirements**: REQ-GMS-004

**Description**:
pytest fixtures、mock 設定、サンプルインデックスデータの準備。

**Deliverables**:
```
tests/
├── conftest.py           # 共通 fixtures
├── fixtures/
│   └── sample_index/     # テスト用 GraphRAG インデックス
└── unit/
    └── __init__.py
```

**Key Fixtures**:
```python
@pytest.fixture
def mock_graphrag_index(): ...

@pytest.fixture
def mock_llm_response(): ...

@pytest.fixture
def sample_query(): ...
```

**TDD Sequence**:
1. RED: fixtures を使用するテスト作成
2. GREEN: fixtures 実装
3. BLUE: fixture 再利用性向上

---

## 3. Phase 2: Core Server (Days 3-5)

### Task 2.1: MCP Server Application
**Priority**: P0 (Critical)
**Estimated Hours**: 3-4
**Requirements**: REQ-GMS-003

**Description**:
MCP サーバーのメインアプリケーション。FastMCP または mcp-python SDK を使用。

**Deliverables**:
```
src/graphrag_mcp_server/server/
├── __init__.py
└── app.py        # MCPサーバーインスタンス
```

**Implementation**:
```python
from mcp import Server

server = Server("graphrag-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]: ...

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Any: ...
```

**TDD Sequence**:
1. RED: `test_server_initialization()`, `test_list_tools()`
2. GREEN: サーバー実装
3. BLUE: エラーハンドリング追加

---

### Task 2.2: Stdio Transport
**Priority**: P0 (Critical)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-003

**Description**:
標準入出力 (stdio) トランスポートの実装。VS Code 統合用。

**Deliverables**:
- `serve` コマンドの `--transport stdio` モード
- stdin/stdout ストリーム処理

**TDD Sequence**:
1. RED: `test_stdio_transport_message_handling()`
2. GREEN: stdio ハンドラー実装
3. BLUE: エッジケース対応

---

### Task 2.3: SSE Transport
**Priority**: P1 (High)
**Estimated Hours**: 2-3
**Requirements**: REQ-GMS-003

**Description**:
Server-Sent Events (SSE) トランスポートの実装。

**Deliverables**:
- `serve` コマンドの `--transport sse --port PORT` モード
- HTTP/SSE エンドポイント

**TDD Sequence**:
1. RED: `test_sse_transport_connection()`
2. GREEN: SSE ハンドラー実装
3. BLUE: 接続管理改善

---

### Task 2.4: Tools Registry
**Priority**: P0 (Critical)
**Estimated Hours**: 3
**Requirements**: REQ-GMS-010-015

**Description**:
MCP Tools の定義とレジストリ。

**Deliverables**:
```
src/graphrag_mcp_server/server/tools.py
```

**Tools**:
| Tool Name | Description | Handler |
|-----------|-------------|---------|
| `global_search` | Map-reduce community search | `search.global_search()` |
| `local_search` | Entity-based search | `search.local_search()` |
| `drift_search` | DRIFT search | `search.drift_search()` |
| `basic_search` | Vector similarity | `search.basic_search()` |
| `build_index` | Index construction | `index.build_index()` |
| `get_statistics` | Index stats | `index.get_statistics()` |

**TDD Sequence**:
1. RED: `test_tool_schema_validation()`, `test_tool_registration()`
2. GREEN: Tools 定義
3. BLUE: スキーマ最適化

---

### Task 2.5: Resources Registry
**Priority**: P1 (High)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-020

**Description**:
MCP Resources の定義。インデックスデータへの読み取りアクセス。

**Deliverables**:
```
src/graphrag_mcp_server/server/resources.py
```

**Resources**:
| Resource URI | Description |
|--------------|-------------|
| `graphrag://entities` | エンティティ一覧 |
| `graphrag://communities` | コミュニティ一覧 |
| `graphrag://statistics` | インデックス統計 |

**TDD Sequence**:
1. RED: `test_resource_listing()`, `test_resource_read()`
2. GREEN: Resources 実装
3. BLUE: キャッシュ追加

---

### Task 2.6: Prompts Registry
**Priority**: P2 (Medium)
**Estimated Hours**: 2
**Requirements**: N/A (Enhancement)

**Description**:
MCP Prompts の定義。事前定義されたクエリテンプレート。

**Deliverables**:
```
src/graphrag_mcp_server/server/prompts.py
```

**Prompts**:
| Prompt Name | Description |
|-------------|-------------|
| `analyze_topic` | トピック分析プロンプト |
| `explore_entities` | エンティティ探索 |
| `summarize_community` | コミュニティ要約 |

**TDD Sequence**:
1. RED: `test_prompt_schema()`, `test_prompt_render()`
2. GREEN: Prompts 実装
3. BLUE: テンプレート改善

---

## 4. Phase 3: Search Handlers (Days 6-8)

### Task 3.1: Global Search Handler
**Priority**: P0 (Critical)
**Estimated Hours**: 3
**Requirements**: REQ-GMS-010

**Description**:
GraphRAG Global Search API の呼び出しと結果変換。

**Deliverables**:
```
src/graphrag_mcp_server/handlers/search.py
```

**Implementation** (Article VIII 準拠 - 直接呼び出し):
```python
from graphrag.api import global_search

async def handle_global_search(query: str, **kwargs) -> SearchResult:
    result = await global_search(
        query=query,
        root_dir=settings.index_path,
        community_level=kwargs.get("community_level", 2),
        ...
    )
    return SearchResult.from_graphrag(result)
```

**TDD Sequence**:
1. RED: `test_global_search_success()`, `test_global_search_timeout()`
2. GREEN: ハンドラー実装
3. BLUE: レスポンス形式最適化

---

### Task 3.2: Local Search Handler
**Priority**: P0 (Critical)
**Estimated Hours**: 2-3
**Requirements**: REQ-GMS-011

**Description**:
GraphRAG Local Search API の呼び出し。

**Implementation**:
```python
from graphrag.api import local_search

async def handle_local_search(query: str, **kwargs) -> SearchResult:
    result = await local_search(query=query, ...)
    return SearchResult.from_graphrag(result)
```

**TDD Sequence**:
1. RED: `test_local_search_with_entities()`, `test_local_search_conversation()`
2. GREEN: ハンドラー実装
3. BLUE: 会話履歴処理改善

---

### Task 3.3: DRIFT Search Handler
**Priority**: P1 (High)
**Estimated Hours**: 3
**Requirements**: REQ-GMS-012

**Description**:
DRIFT (Dynamic Reasoning and Inference with Flexible Traversal) 検索の実装。

**Implementation**:
```python
from graphrag.api import drift_search

async def handle_drift_search(query: str, **kwargs) -> DriftSearchResult:
    result = await drift_search(query=query, ...)
    return DriftSearchResult.from_graphrag(result)
```

**TDD Sequence**:
1. RED: `test_drift_search_followup()`, `test_drift_search_depth()`
2. GREEN: ハンドラー実装
3. BLUE: フォローアップロジック改善

---

### Task 3.4: Basic Search Handler
**Priority**: P1 (High)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-013

**Description**:
基本的なベクトル類似度検索。

**Implementation**:
```python
from graphrag.api import basic_search

async def handle_basic_search(query: str, top_k: int = 10) -> list[TextUnit]:
    result = await basic_search(query=query, top_k=top_k, ...)
    return [TextUnit.from_graphrag(r) for r in result]
```

**TDD Sequence**:
1. RED: `test_basic_search_topk()`, `test_basic_search_empty()`
2. GREEN: ハンドラー実装
3. BLUE: 結果フィルタリング追加

---

### Task 3.5: Streaming Response Handler
**Priority**: P1 (High)
**Estimated Hours**: 2-3
**Requirements**: REQ-GMS-022

**Description**:
ストリーミングレスポンスのサポート。

**Implementation**:
```python
from graphrag.api import global_search_streaming

async def handle_global_search_streaming(query: str, **kwargs):
    async for chunk in global_search_streaming(query=query, ...):
        yield StreamingChunk(content=chunk)
```

**TDD Sequence**:
1. RED: `test_streaming_chunks()`, `test_streaming_cancellation()`
2. GREEN: ストリーミング実装
3. BLUE: バッファリング最適化

---

## 5. Phase 4: Index & Config (Days 9-11)

### Task 4.1: Index Build Handler
**Priority**: P1 (High)
**Estimated Hours**: 3-4
**Requirements**: REQ-GMS-014

**Description**:
GraphRAG インデックス構築ハンドラー。

**Deliverables**:
```
src/graphrag_mcp_server/handlers/index.py
```

**Implementation**:
```python
from graphrag.api import build_index

async def handle_build_index(data_path: str, mode: str = "incremental"):
    result = await build_index(
        root_dir=data_path,
        method=mode,
        ...
    )
    return IndexBuildResult.from_graphrag(result)
```

**TDD Sequence**:
1. RED: `test_build_index_full()`, `test_build_index_incremental()`
2. GREEN: ハンドラー実装
3. BLUE: 進捗レポート追加

---

### Task 4.2: Index Statistics Handler
**Priority**: P2 (Medium)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-020

**Description**:
インデックス統計情報の取得。

**Statistics**:
```python
@dataclass
class IndexStatistics:
    entity_count: int
    relationship_count: int
    community_count: int
    text_unit_count: int
    document_count: int
    index_version: str
    last_updated: datetime
```

**TDD Sequence**:
1. RED: `test_get_statistics()`, `test_statistics_cache()`
2. GREEN: 統計ハンドラー実装
3. BLUE: キャッシュ追加

---

### Task 4.3: LLM Provider Integration
**Priority**: P0 (Critical)
**Estimated Hours**: 3
**Requirements**: REQ-GMS-042, REQ-GMS-043, REQ-GMS-044

**Description**:
複数 LLM プロバイダーのサポート。

**Providers**:
| Provider | Environment Variable |
|----------|---------------------|
| OpenAI | `GRAPHRAG_LLM_API_KEY` |
| Azure OpenAI | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |

**TDD Sequence**:
1. RED: `test_openai_provider()`, `test_azure_provider()`
2. GREEN: プロバイダー実装
3. BLUE: フォールバック追加

---

### Task 4.4: Vector Store Integration
**Priority**: P1 (High)
**Estimated Hours**: 2-3
**Requirements**: REQ-GMS-040, REQ-GMS-041

**Description**:
LanceDB (ローカル) / Azure AI Search (クラウド) サポート。

**TDD Sequence**:
1. RED: `test_lancedb_store()`, `test_azure_search_store()`
2. GREEN: ストア実装
3. BLUE: 設定切り替え改善

---

## 6. Phase 5: Polish & Release (Days 12-14)

### Task 5.1: Integration Tests
**Priority**: P0 (Critical)
**Estimated Hours**: 3
**Requirements**: Article IX

**Description**:
実サービスを使用した統合テスト。

**Deliverables**:
```
tests/integration/
├── test_server.py
├── test_search.py
└── test_index.py
```

**Test Scenarios**:
- [x] サーバー起動→クエリ→シャットダウン
- [x] インデックス作成→検索→結果検証
- [x] エラーリカバリー

**Article IX 準拠**:
- LanceDB: 実データベース使用
- LLM: コスト削減のためモック許可

---

### Task 5.2: Documentation
**Priority**: P1 (High)
**Estimated Hours**: 2-3
**Requirements**: REQ-GMS-002

**Description**:
README、使用例、API ドキュメント。

**Deliverables**:
- `README.md` - 概要、クイックスタート
- `docs/` - 詳細ドキュメント
- `examples/` - 使用例

---

### Task 5.3: VS Code Configuration
**Priority**: P1 (High)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-003

**Description**:
VS Code MCP 設定サンプルと統合ガイド。

**Deliverables**:
```json
// .vscode/mcp.json example
{
  "servers": {
    "graphrag": {
      "command": "graphrag-mcp",
      "args": ["serve", "--transport", "stdio"],
      "env": {
        "GRAPHRAG_INDEX_PATH": "./graphrag_index"
      }
    }
  }
}
```

---

### Task 5.4: Package Release Preparation
**Priority**: P1 (High)
**Estimated Hours**: 2
**Requirements**: REQ-GMS-001

**Description**:
PyPI リリース準備。

**Deliverables**:
- [x] `pyproject.toml` 最終化
- [x] `CHANGELOG.md`
- [x] GitHub Actions CI/CD
- [ ] PyPI テストリリース

---

## 7. Dependency Graph

```
Phase 1 (Foundation)
    ├── 1.1 Project Scaffolding
    │       ↓
    ├── 1.2 CLI Foundation
    │       ↓
    ├── 1.3 Configuration Module
    │       ↓
    ├── 1.4 Error Handling
    │       ↓
    └── 1.5 Test Infrastructure
            ↓
Phase 2 (Core Server)
    ├── 2.1 MCP Server Application ←──────────────────┐
    │       ↓                                         │
    ├── 2.2 Stdio Transport                           │
    │       ↓                                         │
    ├── 2.3 SSE Transport                             │
    │       ↓                                         │
    ├── 2.4 Tools Registry ──────────┐                │
    │       ↓                        │                │
    ├── 2.5 Resources Registry       │                │
    │       ↓                        │                │
    └── 2.6 Prompts Registry         │                │
            ↓                        ↓                │
Phase 3 (Search Handlers)          Phase 4 (Index)   │
    ├── 3.1 Global Search ◄──────── 4.1 Index Build  │
    ├── 3.2 Local Search            4.2 Statistics   │
    ├── 3.3 DRIFT Search            4.3 LLM Provider │
    ├── 3.4 Basic Search            4.4 Vector Store │
    └── 3.5 Streaming               │                │
            ↓                       ↓                │
Phase 5 (Polish & Release) ◄────────┴────────────────┘
    ├── 5.1 Integration Tests
    ├── 5.2 Documentation
    ├── 5.3 VS Code Config
    └── 5.4 Package Release
```

---

## 8. Traceability Matrix

| Task | Requirements | Design Component | Test File |
|------|--------------|------------------|-----------|
| 1.1 | REQ-GMS-001 | Package Structure | `test_package.py` |
| 1.2 | REQ-GMS-002 | CLI Module | `test_cli.py` |
| 1.3 | REQ-GMS-005 | Config Module | `test_config.py` |
| 1.4 | REQ-GMS-030-033 | Error Module | `test_errors.py` |
| 2.1 | REQ-GMS-003 | MCP Server | `test_server.py` |
| 2.4 | REQ-GMS-010-015 | Tools Registry | `test_tools.py` |
| 3.1 | REQ-GMS-010 | SearchHandler | `test_global_search.py` |
| 3.2 | REQ-GMS-011 | SearchHandler | `test_local_search.py` |
| 3.3 | REQ-GMS-012 | SearchHandler | `test_drift_search.py` |
| 3.4 | REQ-GMS-013 | SearchHandler | `test_basic_search.py` |
| 3.5 | REQ-GMS-022 | StreamingHandler | `test_streaming.py` |
| 4.1 | REQ-GMS-014 | IndexHandler | `test_index.py` |
| 4.3 | REQ-GMS-042-044 | ProviderConfig | `test_providers.py` |
| 4.4 | REQ-GMS-040-041 | VectorStore | `test_vector_stores.py` |

---

## 9. Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2025-12-05 | @orchestrator | All tasks completed, 291 tests passing |
| 1.0 | 2025-12-05 | @orchestrator | Initial task breakdown |
