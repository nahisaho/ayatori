# Design: GraphRAG MCP Server

**Feature ID**: FEAT-001
**Design Version**: 1.0
**Status**: Draft
**Created**: 2025-12-05
**Author**: @system-architect, @constitution-enforcer

---

## 1. Constitutional Compliance Validation

### 1.1 Validation Summary

| Article | Title | Status | Notes |
|---------|-------|--------|-------|
| I | Library-First Principle | ✅ PASS | REQ-GMS-001 で明示的に定義 |
| II | CLI Interface Mandate | ✅ PASS | REQ-GMS-002 で明示的に定義 |
| III | Test-First Imperative | ✅ PASS | REQ-GMS-004 で明示的に定義 |
| IV | EARS Requirements Format | ✅ PASS | 全24要件が EARS パターン準拠 |
| V | Traceability Mandate | ✅ PASS | 追跡マトリクス定義済み |
| VI | Project Memory | ✅ PASS | steering 参照済み |
| VII | Simplicity Gate | ✅ PASS | 単一プロジェクト (≤3) |
| VIII | Anti-Abstraction Gate | ⚠️ REVIEW | GraphRAG API 直接使用を確認要 |
| IX | Integration-First Testing | ✅ PASS | 実サービステスト計画 |

**Overall Status**: ✅ **APPROVED FOR DESIGN PHASE**

### 1.2 Article VIII Review: Anti-Abstraction

**Question**: GraphRAG ライブラリをラップすることは Article VIII 違反か？

**判定**: **非違反**

**理由**:
1. MCP サーバーは「カスタム抽象化レイヤー」ではなく「プロトコル変換レイヤー」
2. GraphRAG API を直接呼び出し、結果を MCP プロトコルにマッピングするのみ
3. ビジネスロジックの追加やカスタムラッパーは作成しない
4. 参照実装 `.mcp/CodeGraphMCPServer/` と同様のパターン

**設計指針**:
```python
# ✅ 正しいパターン: GraphRAG API 直接呼び出し
from graphrag.api import global_search

async def handle_global_search(query: str) -> MCPResponse:
    result = await global_search(query=query, ...)  # 直接呼び出し
    return MCPResponse(content=result)  # プロトコル変換のみ

# ❌ 禁止パターン: カスタム抽象化
class MyGraphRAGWrapper:
    def search(self, query):  # 独自API
        ...  # カスタムロジック
```

---

## 2. C4 Architecture

### 2.1 Context Diagram (Level 1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              System Context                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌─────────────┐         ┌─────────────────────────┐         ┌───────────┐  │
│   │   AI User   │         │                         │         │   LLM     │  │
│   │  (Developer)│         │  GraphRAG MCP Server    │         │ Provider  │  │
│   │             │◄───────►│                         │◄───────►│ (OpenAI/  │  │
│   │ Uses Copilot│   MCP   │  [Software System]      │   API   │  Azure/   │  │
│   │ Claude etc. │         │                         │         │ Anthropic)│  │
│   └─────────────┘         └───────────┬─────────────┘         └───────────┘  │
│                                       │                                       │
│                                       │ File I/O                              │
│                                       ▼                                       │
│                           ┌───────────────────────┐                          │
│                           │   Document Corpus     │                          │
│                           │   (Text/Code Files)   │                          │
│                           │   [External System]   │                          │
│                           └───────────────────────┘                          │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Container Diagram (Level 2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GraphRAG MCP Server                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   MCP Server    │    │   Query Engine  │    │  Index Engine   │          │
│  │   [Container]   │───►│   [Container]   │    │  [Container]    │          │
│  │                 │    │                 │    │                 │          │
│  │ - stdio handler │    │ - global_search │    │ - build_index   │          │
│  │ - SSE handler   │    │ - local_search  │    │ - prompt_tune   │          │
│  │ - tools/prompts │    │ - drift_search  │    │ - file_watcher  │          │
│  │ - resources     │    │ - basic_search  │    │                 │          │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘          │
│           │                      │                      │                    │
│           │                      ▼                      ▼                    │
│           │             ┌─────────────────────────────────────┐              │
│           │             │         GraphRAG Core Library       │              │
│           │             │         [External Library]          │              │
│           │             │                                     │              │
│           │             │  graphrag.api.* (直接呼び出し)       │              │
│           │             └──────────────────┬──────────────────┘              │
│           │                                │                                 │
│           ▼                                ▼                                 │
│  ┌─────────────────┐              ┌─────────────────┐                       │
│  │    CLI Module   │              │  Vector Store   │                       │
│  │   [Container]   │              │   [Container]   │                       │
│  │                 │              │                 │                       │
│  │ - serve         │              │ - LanceDB       │                       │
│  │ - index         │              │ - Azure Search  │                       │
│  │ - query         │              │                 │                       │
│  │ - stats         │              │                 │                       │
│  └─────────────────┘              └─────────────────┘                       │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Component Diagram (Level 3)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MCP Server Container                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Transport Layer                                │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │   │
│  │  │  StdioHandler   │    │   SSEHandler    │    │ StreamHandler   │   │   │
│  │  │  [Component]    │    │  [Component]    │    │  [Component]    │   │   │
│  │  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘   │   │
│  └───────────┼──────────────────────┼──────────────────────┼────────────┘   │
│              │                      │                      │                 │
│              ▼                      ▼                      ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Protocol Layer                                 │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │   │
│  │  │  ToolRegistry   │    │ResourceRegistry │    │ PromptRegistry  │   │   │
│  │  │  [Component]    │    │  [Component]    │    │  [Component]    │   │   │
│  │  │                 │    │                 │    │                 │   │   │
│  │  │ - global_search │    │ - entities      │    │ - analyze       │   │   │
│  │  │ - local_search  │    │ - communities   │    │ - explore       │   │   │
│  │  │ - drift_search  │    │ - text_units    │    │ - compare       │   │   │
│  │  │ - basic_search  │    │ - statistics    │    │ - summarize     │   │   │
│  │  │ - build_index   │    │                 │    │                 │   │   │
│  │  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘   │   │
│  └───────────┼──────────────────────┼──────────────────────┼────────────┘   │
│              │                      │                      │                 │
│              ▼                      ▼                      ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Handler Layer                                  │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │   │
│  │  │ SearchHandler   │    │  IndexHandler   │    │  ConfigHandler  │   │   │
│  │  │  [Component]    │    │  [Component]    │    │  [Component]    │   │   │
│  │  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘   │   │
│  └───────────┼──────────────────────┼──────────────────────┼────────────┘   │
│              │                      │                      │                 │
│              ▼                      ▼                      ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    GraphRAG API (Direct Calls)                        │   │
│  │                                                                        │   │
│  │   graphrag.api.global_search()    graphrag.api.build_index()          │   │
│  │   graphrag.api.local_search()     graphrag.api.generate_prompts()     │   │
│  │   graphrag.api.drift_search()                                          │   │
│  │   graphrag.api.basic_search()                                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Package Structure

```
lib/graphrag-mcp-server/
├── pyproject.toml              # REQ-GMS-001: 独立パッケージ
├── README.md
├── LICENSE
├── src/
│   └── graphrag_mcp_server/
│       ├── __init__.py         # パブリック API エクスポート
│       ├── __main__.py         # python -m graphrag_mcp_server
│       ├── py.typed            # 型ヒントマーカー
│       │
│       ├── cli/                # REQ-GMS-002: CLI モジュール
│       │   ├── __init__.py
│       │   ├── main.py         # typer app
│       │   ├── serve.py        # serve コマンド
│       │   ├── index.py        # index コマンド
│       │   ├── query.py        # query コマンド
│       │   └── stats.py        # stats コマンド
│       │
│       ├── server/             # REQ-GMS-003: MCP サーバー
│       │   ├── __init__.py
│       │   ├── app.py          # MCP アプリケーション
│       │   ├── tools.py        # MCP Tools 定義
│       │   ├── resources.py    # MCP Resources 定義
│       │   └── prompts.py      # MCP Prompts 定義
│       │
│       ├── handlers/           # ビジネスロジック
│       │   ├── __init__.py
│       │   ├── search.py       # 検索ハンドラー (REQ-GMS-010~013)
│       │   ├── index.py        # インデックスハンドラー (REQ-GMS-014)
│       │   ├── prompts.py      # プロンプトハンドラー (REQ-GMS-015)
│       │   └── streaming.py    # ストリーミング (REQ-GMS-022)
│       │
│       ├── config/             # 設定管理
│       │   ├── __init__.py
│       │   ├── settings.py     # Pydantic Settings
│       │   └── providers.py    # LLM プロバイダー設定
│       │
│       └── errors/             # エラーハンドリング (REQ-GMS-030~033)
│           ├── __init__.py
│           └── handlers.py
│
└── tests/                      # REQ-GMS-004: テストスイート
    ├── __init__.py
    ├── conftest.py             # pytest fixtures
    ├── unit/
    │   ├── test_cli.py
    │   ├── test_tools.py
    │   ├── test_handlers.py
    │   └── test_config.py
    ├── integration/
    │   ├── test_server.py
    │   ├── test_search.py
    │   └── test_index.py
    └── fixtures/
        └── sample_index/
```

---

## 4. ADR (Architecture Decision Records)

### ADR-001: GraphRAG API Direct Usage

**Status**: Accepted

**Context**: 
GraphRAG ライブラリの機能を MCP サーバーとして公開する必要がある。

**Decision**: 
`graphrag.api.*` モジュールを直接呼び出し、カスタムラッパーを作成しない。

**Consequences**:
- ✅ Article VIII (Anti-Abstraction) 準拠
- ✅ GraphRAG アップデートへの追従が容易
- ✅ コードの複雑性低減
- ⚠️ GraphRAG API 変更時の影響を受ける

**Constitutional Reference**: Article VIII

---

### ADR-002: Single Package Architecture

**Status**: Accepted

**Context**: 
プロジェクト構造をどのように設計するか。

**Decision**: 
単一の Python パッケージ (`graphrag-mcp-server`) として実装する。

**Consequences**:
- ✅ Article VII (Simplicity Gate) 準拠 - 1プロジェクト ≤ 3
- ✅ デプロイと配布が簡素
- ✅ 依存関係管理が容易

**Constitutional Reference**: Article VII

---

### ADR-003: LanceDB as Default Vector Store

**Status**: Accepted

**Context**: 
ローカル開発/テスト用のベクトルストアを選択する必要がある。

**Decision**: 
LanceDB をデフォルトのベクトルストアとして採用する。Azure AI Search はオプション。

**Consequences**:
- ✅ ゼロ設定でのローカル開発が可能
- ✅ 外部サービス依存なし (開発時)
- ✅ Article IX (Integration-First Testing) 準拠 - 実際のDBでテスト

**Constitutional Reference**: Article IX

---

### ADR-004: Environment Variable Configuration

**Status**: Accepted

**Context**: 
認証情報と設定の管理方法を決定する必要がある。

**Decision**: 
すべての認証情報は環境変数から取得する。設定ファイルには秘密情報を含めない。

**Consequences**:
- ✅ REQ-GMS-005 (Security) 準拠
- ✅ 12-factor app 原則に従う
- ✅ CI/CD パイプラインとの統合が容易

**Constitutional Reference**: Security Requirement

---

### ADR-005: Document ETL/Chunking Exclusion

**Status**: Accepted

**Context**: 
PubSec-Info-Assistant のような ETL パイプライン (Azure Document Intelligence + unstructured.io によるドキュメント解析、チャンキング、言語翻訳) を MCP Server に組み込むべきか検討した。

**Compared Systems**:
| Feature | PubSec-Info-Assistant | GraphRAG Native |
|---------|----------------------|-----------------|
| Document Parsing | Azure Doc Intelligence + unstructured.io | なし (TXT/CSV/JSON のみ) |
| Supported Formats | PDF, DOCX, PPTX, XLSX, HTML, etc. | TXT, CSV, JSON |
| Chunking Strategy | Token-based + sentence boundary | Token-based with overlap |
| Structure Preservation | Title, Section, Table metadata | Metadata prepend (v2.6+) |
| Language Translation | Azure Translator | なし |

**Decision**: 
ETL/Chunking 機能を GraphRAG MCP Server に組み込まない。ドキュメント前処理は外部サービスに委譲する。

**Rationale**:
1. **Article VIII 準拠**: GraphRAG のネイティブ入力処理を尊重し、カスタム抽象化を回避
2. **責務分離**: MCP Server はクエリ/インデックス API 変換に専念
3. **依存関係軽減**: unstructured.io (500MB+)、pandoc、tesseract 等の肥大化を回避
4. **GraphRAG 設計思想**: シンプルな入力形式 (TXT/CSV/JSON) は意図的な設計判断

**Recommended Architecture**:
```
[Document Sources (PDF/Office/etc.)]
          ↓
[External ETL Service] ← PubSec-Info-Assistant / Azure Doc Intelligence / unstructured
          ↓
[TXT/CSV/JSON files]
          ↓
[GraphRAG MCP Server] ← クエリ & インデックス API のみ
```

**User Guidance**:
- MCP Server ドキュメントに前処理ガイドラインを記載
- 推奨ツール: unstructured-io, Azure Document Intelligence, Apache Tika

**Consequences**:
- ✅ Article VII (Simplicity Gate) 準拠
- ✅ Article VIII (Anti-Abstraction) 準拠
- ✅ 軽量で高速な起動
- ⚠️ ユーザーは事前にドキュメント変換が必要

**Constitutional Reference**: Article VII, Article VIII

---

## 5. Interface Specifications

### 5.1 CLI Interface (REQ-GMS-002)

```bash
# サーバー起動
graphrag-mcp serve [OPTIONS]
  --transport [stdio|sse]   # 通信モード (default: stdio)
  --port PORT               # SSE モード時のポート (default: 8080)
  --index-path PATH         # インデックスパス (default: ./graphrag_index)

# インデックス作成
graphrag-mcp index [OPTIONS] DATA_PATH
  --full                    # フルインデックス
  --incremental             # インクリメンタル (default)
  --watch                   # ファイル監視モード

# クエリ実行 (デバッグ用)
graphrag-mcp query [OPTIONS] QUERY
  --type [global|local|drift|basic]
  --community-level INT
  --top-k INT

# 統計表示
graphrag-mcp stats [OPTIONS]
  --index-path PATH
  --format [text|json]

# バージョン・ヘルプ
graphrag-mcp --version
graphrag-mcp --help
```

### 5.2 MCP Tools Schema

```json
{
  "tools": [
    {
      "name": "global_search",
      "description": "Execute a global search across the entire dataset using community summaries",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The search query"
          },
          "community_level": {
            "type": "integer",
            "description": "Community hierarchy level (0=most detailed)",
            "default": 2
          },
          "response_type": {
            "type": "string",
            "description": "Desired response format",
            "default": "Multiple Paragraphs"
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "local_search",
      "description": "Execute an entity-based local search",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The search query"
          },
          "entity_types": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Filter by entity types"
          },
          "response_type": {
            "type": "string",
            "default": "Multiple Paragraphs"
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "drift_search",
      "description": "Execute DRIFT search combining global and local methods",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The search query"
          },
          "follow_up_depth": {
            "type": "integer",
            "description": "Depth of follow-up questions",
            "default": 2
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "basic_search",
      "description": "Execute basic vector similarity search",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string"
          },
          "top_k": {
            "type": "integer",
            "default": 10
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "build_index",
      "description": "Build or update the GraphRAG index",
      "inputSchema": {
        "type": "object",
        "properties": {
          "data_path": {
            "type": "string",
            "description": "Path to data directory"
          },
          "mode": {
            "type": "string",
            "enum": ["full", "incremental"],
            "default": "incremental"
          }
        },
        "required": ["data_path"]
      }
    },
    {
      "name": "get_statistics",
      "description": "Get index statistics",
      "inputSchema": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
```

---

## 6. Test Strategy

### 6.1 Test Categories

| Category | Purpose | Real Services | Coverage Target |
|----------|---------|---------------|-----------------|
| Unit | 個別コンポーネント | No | 90% |
| Integration | API統合 | LanceDB (real) | 80% |
| E2E | フルフロー | All real | 70% |

### 6.2 Test Database Setup (Article IX)

```yaml
# docker-compose.test.yml
services:
  test-graphrag:
    build: .
    environment:
      - GRAPHRAG_INDEX_PATH=/data/test_index
      - LLM_PROVIDER=mock  # テスト用モック (Article IX 例外)
    volumes:
      - ./tests/fixtures:/data
```

**Article IX 例外事項**:
- LLM API 呼び出しは高コストのためモック使用を許可
- ベクトルストア (LanceDB) は実サービス使用必須

---

## 7. Traceability Update

| Requirement | Design Component | Source File |
|-------------|------------------|-------------|
| REQ-GMS-001 | Package Structure | `pyproject.toml` |
| REQ-GMS-002 | CLI Module | `src/graphrag_mcp_server/cli/` |
| REQ-GMS-003 | MCP Server | `src/graphrag_mcp_server/server/` |
| REQ-GMS-010 | SearchHandler.global_search | `handlers/search.py` |
| REQ-GMS-011 | SearchHandler.local_search | `handlers/search.py` |
| REQ-GMS-012 | SearchHandler.drift_search | `handlers/search.py` |
| REQ-GMS-013 | SearchHandler.basic_search | `handlers/search.py` |
| REQ-GMS-014 | IndexHandler | `handlers/index.py` |
| REQ-GMS-030-033 | ErrorHandlers | `errors/handlers.py` |

---

## 8. Next Steps

1. **@api-designer**: MCP Tools/Resources/Prompts の詳細仕様
2. **@test-engineer**: テストケース設計
3. **@software-developer**: タスク分解と実装開始

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | @system-architect | Initial design |
| 1.0 | 2025-12-05 | @constitution-enforcer | Compliance validation |

