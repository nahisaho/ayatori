# Feature: GraphRAG MCP Server

**Feature ID**: FEAT-001
**Feature Name**: GraphRAG MCP Server
**Status**: Design Complete
**Created**: 2025-12-05
**Author**: @orchestrator
**Constitutional Compliance**: ✅ Validated (2025-12-05)

---

## 1. Executive Summary

### 1.1 概要

Microsoft GraphRAG (Graph Retrieval-Augmented Generation) の機能を MCP (Model Context Protocol) サーバーとして公開し、AI アシスタント (GitHub Copilot, Claude Desktop, Cursor 等) から GraphRAG の強力なクエリ機能を利用可能にする。

### 1.2 ビジネス価値

- **開発者体験の向上**: AI アシスタントから直接 GraphRAG の知識グラフを検索可能
- **統合の簡素化**: MCP プロトコルによる標準化されたインターフェース
- **コンテキスト強化**: ドキュメントやコードベースの深い理解を AI に提供

### 1.3 参照資料

- `References/graphrag/` - Microsoft GraphRAG 実装 (v2.7.0)
- `References/graphrag/docs/query/` - クエリエンジンドキュメント
- `.mcp/CodeGraphMCPServer/` - 参照 MCP サーバー実装

---

## 2. EARS Requirements

### 2.1 Ubiquitous Requirements (ユビキタス要件)

#### REQ-GMS-001: Library-First Architecture
**The** GraphRAG MCP Server **SHALL** be implemented as an independent library with its own package structure before any application integration.

**Acceptance Criteria**:
- [ ] 独立したパッケージディレクトリ (`lib/graphrag-mcp-server/` または `/packages/`)
- [ ] 独立した `pyproject.toml` または `package.json`
- [ ] アプリケーションコードへの依存がないこと
- [ ] パブリック API が明確にエクスポートされていること

**Constitutional Reference**: Article I (Library-First Principle)

---

#### REQ-GMS-002: CLI Interface
**The** GraphRAG MCP Server library **SHALL** expose all primary functionality through a CLI interface.

**Acceptance Criteria**:
- [ ] CLI エントリーポイントの提供 (`graphrag-mcp` コマンド)
- [ ] `--help` フラグによるドキュメント
- [ ] 主要操作のサポート: `serve`, `index`, `stats`, `query`
- [ ] 終了コードの規約準拠 (0=成功, 非0=エラー)

**Constitutional Reference**: Article II (CLI Interface Mandate)

---

#### REQ-GMS-003: MCP Protocol Compliance
**The** GraphRAG MCP Server **SHALL** implement the Model Context Protocol specification version 1.0 or higher.

**Acceptance Criteria**:
- [ ] MCP SDK (`mcp>=1.0.0`) の使用
- [ ] stdio 通信モードのサポート
- [ ] SSE (Server-Sent Events) 通信モードのサポート
- [ ] MCP Tools, Resources, Prompts の実装

**Constitutional Reference**: N/A (Technical Requirement)

---

#### REQ-GMS-004: Test Coverage
**The** GraphRAG MCP Server **SHALL** maintain test coverage of at least 80% with tests written before implementation (Red-Green-Blue cycle).

**Acceptance Criteria**:
- [ ] 全 EARS 要件に対応するテストの存在
- [ ] テストカバレッジ ≥ 80%
- [ ] Red-Green-Blue サイクルの証跡 (git履歴)
- [ ] テストなしの本番コードがないこと

**Constitutional Reference**: Article III (Test-First Imperative)

---

#### REQ-GMS-005: Security - No Credential Storage
**The** GraphRAG MCP Server **SHALL NOT** store any credentials, API keys, or secrets in code or configuration files.

**Acceptance Criteria**:
- [ ] 環境変数による認証情報の取得
- [ ] コード/設定ファイルへの秘密情報の非保存
- [ ] LLM API キーの安全な取り扱い

**Constitutional Reference**: Article III (Security Requirements)

---

### 2.2 Event-Driven Requirements (イベント駆動要件)

#### REQ-GMS-010: Global Search Query
**WHEN** a client sends a global search query, **the** GraphRAG MCP Server **SHALL** execute a map-reduce style search across community reports and return aggregated results within 60 seconds.

**Acceptance Criteria**:
- [ ] コミュニティレポートからのmap-reduce検索実行
- [ ] 結果の集約と優先順位付け
- [ ] 60秒以内のレスポンス (設定可能なタイムアウト)
- [ ] ストリーミングレスポンスのサポート

**Related GraphRAG Component**: `graphrag.api.global_search`, `graphrag.api.global_search_streaming`

---

#### REQ-GMS-011: Local Search Query
**WHEN** a client sends a local search query with entity references, **the** GraphRAG MCP Server **SHALL** retrieve relevant entities, relationships, and text units from the knowledge graph.

**Acceptance Criteria**:
- [ ] エンティティベースの検索実行
- [ ] 関連エンティティ、リレーション、テキストユニットの取得
- [ ] コンテキストウィンドウ内でのデータ優先順位付け
- [ ] 会話履歴のサポート

**Related GraphRAG Component**: `graphrag.api.local_search`, `graphrag.api.local_search_streaming`

---

#### REQ-GMS-012: DRIFT Search Query
**WHEN** a client sends a DRIFT search query, **the** GraphRAG MCP Server **SHALL** combine global and local search methods using community information and dynamic follow-up questions.

**Acceptance Criteria**:
- [ ] Primer フェーズ: クエリとコミュニティレポートの比較
- [ ] Follow-Up フェーズ: ローカル検索によるクエリ精緻化
- [ ] 階層的な質問・回答構造の出力
- [ ] 信頼度スコアの提供

**Related GraphRAG Component**: `graphrag.api.drift_search`, `graphrag.api.drift_search_streaming`

---

#### REQ-GMS-013: Basic Vector Search
**WHEN** a client sends a basic search query, **the** GraphRAG MCP Server **SHALL** perform standard top-k vector similarity search on text units.

**Acceptance Criteria**:
- [ ] ベクトル類似度検索の実行
- [ ] top-k パラメータの設定可能性
- [ ] テキストユニットチャンクの返却

**Related GraphRAG Component**: `graphrag.api.basic_search`, `graphrag.api.basic_search_streaming`

---

#### REQ-GMS-014: Index Build Request
**WHEN** a client requests index building, **the** GraphRAG MCP Server **SHALL** trigger the GraphRAG indexing pipeline on the specified data source.

**Acceptance Criteria**:
- [ ] フルインデックスモードのサポート
- [ ] インクリメンタルインデックスモードのサポート
- [ ] 進捗レポートの提供
- [ ] エンティティ・リレーション抽出の実行

**Related GraphRAG Component**: `graphrag.api.build_index`

---

#### REQ-GMS-015: Prompt Tuning Request
**WHEN** a client requests prompt tuning, **the** GraphRAG MCP Server **SHALL** generate optimized indexing prompts based on the data corpus.

**Acceptance Criteria**:
- [ ] ドキュメント選択タイプの指定
- [ ] LLM プロバイダー設定のサポート
- [ ] カスタマイズされたプロンプトの生成

**Related GraphRAG Component**: `graphrag.api.generate_indexing_prompts`

---

### 2.3 State-Driven Requirements (状態駆動要件)

#### REQ-GMS-020: Index Available State
**WHILE** a valid GraphRAG index is available, **the** GraphRAG MCP Server **SHALL** respond to all search queries using the indexed data.

**Acceptance Criteria**:
- [ ] インデックスの存在確認
- [ ] インデックスバージョンの検証
- [ ] インデックス統計情報の提供

---

#### REQ-GMS-021: Multi-Index Mode
**WHILE** multiple GraphRAG indexes are configured, **the** GraphRAG MCP Server **SHALL** support cross-index search queries.

**Acceptance Criteria**:
- [ ] 複数インデックスの設定読み込み
- [ ] マルチインデックス検索 API の提供
- [ ] インデックス選択パラメータのサポート

**Related GraphRAG Component**: `graphrag.api.multi_index_*`

---

#### REQ-GMS-022: Streaming Response Mode
**WHILE** streaming is enabled, **the** GraphRAG MCP Server **SHALL** provide incremental response chunks as they are generated.

**Acceptance Criteria**:
- [ ] SSE 形式でのストリーミング
- [ ] チャンク単位での応答送信
- [ ] コールバックハンドラのサポート

---

### 2.4 Unwanted Behavior Requirements (異常系要件)

#### REQ-GMS-030: No Index Available
**IF** no GraphRAG index is available, **THEN the** GraphRAG MCP Server **SHALL** return an appropriate error message with instructions for index creation.

**Acceptance Criteria**:
- [ ] 明確なエラーメッセージの返却
- [ ] インデックス作成手順の案内
- [ ] HTTP 404 または MCP エラーコードの使用

---

#### REQ-GMS-031: LLM Provider Error
**IF** the LLM provider returns an error or is unavailable, **THEN the** GraphRAG MCP Server **SHALL** return a graceful error response with retry guidance.

**Acceptance Criteria**:
- [ ] LLM エラーのキャッチと変換
- [ ] リトライ可能かどうかの判定
- [ ] タイムアウト設定のサポート

---

#### REQ-GMS-032: Invalid Query Format
**IF** a client sends an invalid query format, **THEN the** GraphRAG MCP Server **SHALL** return a validation error with schema information.

**Acceptance Criteria**:
- [ ] 入力バリデーションの実行
- [ ] スキーマ情報を含むエラーメッセージ
- [ ] Pydantic による型検証

---

#### REQ-GMS-033: Token Budget Exceeded
**IF** the query context exceeds the configured token budget, **THEN the** GraphRAG MCP Server **SHALL** truncate and prioritize content based on relevance scores.

**Acceptance Criteria**:
- [ ] トークン予算の監視
- [ ] 関連性スコアによる優先順位付け
- [ ] 切り捨て警告の提供

---

### 2.5 Optional Feature Requirements (オプション機能要件)

#### REQ-GMS-040: Azure AI Search Integration
**WHERE** Azure AI Search is configured, **the** GraphRAG MCP Server **SHALL** use Azure AI Search as the vector store backend.

**Acceptance Criteria**:
- [ ] Azure AI Search クライアントの統合
- [ ] 接続文字列/認証の設定
- [ ] インデックス作成・検索操作のサポート

---

#### REQ-GMS-041: LanceDB Local Storage
**WHERE** local storage mode is configured, **the** GraphRAG MCP Server **SHALL** use LanceDB for vector storage.

**Acceptance Criteria**:
- [ ] LanceDB ローカルストレージの設定
- [ ] ファイルベースのインデックス管理
- [ ] 開発/テスト環境でのサポート

---

#### REQ-GMS-042: OpenAI Provider
**WHERE** OpenAI is configured as the LLM provider, **the** GraphRAG MCP Server **SHALL** use OpenAI API for language model operations.

**Acceptance Criteria**:
- [ ] OpenAI API キーの設定
- [ ] モデル選択 (gpt-4, gpt-4o 等)
- [ ] エンベディングモデルの設定

---

#### REQ-GMS-043: Azure OpenAI Provider
**WHERE** Azure OpenAI is configured, **the** GraphRAG MCP Server **SHALL** use Azure OpenAI Service for language model operations.

**Acceptance Criteria**:
- [ ] Azure OpenAI エンドポイント設定
- [ ] デプロイメント名の設定
- [ ] Azure AD 認証のサポート

---

#### REQ-GMS-044: Anthropic Provider
**WHERE** Anthropic is configured, **the** GraphRAG MCP Server **SHALL** use Anthropic Claude API for language model operations.

**Acceptance Criteria**:
- [ ] Anthropic API キーの設定
- [ ] Claude モデル選択
- [ ] ストリーミングレスポンスのサポート

---

#### REQ-GMS-045: File Watch Auto-Reindex
**WHERE** file watching is enabled, **the** GraphRAG MCP Server **SHALL** automatically trigger incremental reindexing when source files change.

**Acceptance Criteria**:
- [ ] ファイル変更の監視
- [ ] デバウンス設定 (秒)
- [ ] 自動インクリメンタルインデックス

---

---

## 3. MCP Interface Specification

### 3.1 MCP Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `global_search` | データセット全体の俯瞰的検索 | `query`, `community_level`, `response_type` |
| `local_search` | エンティティベースの詳細検索 | `query`, `entity_types`, `response_type` |
| `drift_search` | 動的推論による複合検索 | `query`, `config` |
| `basic_search` | ベクトル類似度検索 | `query`, `top_k` |
| `build_index` | インデックス構築 | `data_path`, `mode`, `config` |
| `get_statistics` | インデックス統計 | `index_path` |
| `list_entities` | エンティティ一覧 | `entity_type`, `limit` |
| `list_communities` | コミュニティ一覧 | `level`, `limit` |
| `generate_prompts` | プロンプトチューニング | `doc_selection_type` |
| `question_generation` | フォローアップ質問生成 | `queries`, `context` |

### 3.2 MCP Resources

| Resource Name | URI Pattern | Description |
|---------------|-------------|-------------|
| `entities` | `graphrag://entities` | エンティティデータへのアクセス |
| `communities` | `graphrag://communities/{level}` | コミュニティレポートへのアクセス |
| `text_units` | `graphrag://text_units` | テキストユニットへのアクセス |
| `statistics` | `graphrag://stats` | インデックス統計情報 |

### 3.3 MCP Prompts

| Prompt Name | Description | Arguments |
|-------------|-------------|-----------|
| `analyze_dataset` | データセット分析 | `focus_area` |
| `explore_entity` | エンティティ探索 | `entity_name` |
| `compare_concepts` | 概念比較 | `concept_a`, `concept_b` |
| `summarize_themes` | テーマ要約 | `detail_level` |
| `debug_index` | インデックス問題診断 | `issue_description` |
| `optimize_query` | クエリ最適化 | `original_query` |

---

## 4. Technology Stack

### 4.1 Core Dependencies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | ランタイム |
| graphrag | 2.7.0 | GraphRAG コアライブラリ |
| mcp | 1.0.0+ | MCP プロトコル SDK |
| pydantic | 2.0+ | データバリデーション |
| typer | 0.9.0+ | CLI フレームワーク |
| aiosqlite | 0.19+ | 非同期 SQLite |
| networkx | 3.0+ | グラフ操作 |
| tiktoken | 0.5+ | トークンカウント |

### 4.2 Optional Dependencies

| Technology | Version | Purpose | Configuration |
|------------|---------|---------|---------------|
| azure-search-documents | 11.5+ | Azure AI Search | `AZURE_SEARCH_*` |
| lancedb | 0.17+ | ローカルベクトルストア | `VECTOR_STORE=lancedb` |
| openai | 1.68+ | OpenAI API | `OPENAI_API_KEY` |
| anthropic | (latest) | Anthropic API | `ANTHROPIC_API_KEY` |
| watchfiles | 0.21+ | ファイル監視 | `--watch` フラグ |

---

## 5. Traceability Matrix

| Requirement ID | Design Component | Test Case | Status |
|----------------|------------------|-----------|--------|
| REQ-GMS-001 | Package Structure | TEST-PKG-001 | Pending |
| REQ-GMS-002 | CLI Module | TEST-CLI-001 | Pending |
| REQ-GMS-003 | MCP Server Core | TEST-MCP-001 | Pending |
| REQ-GMS-004 | Test Suite | TEST-COV-001 | Pending |
| REQ-GMS-005 | Config Module | TEST-SEC-001 | Pending |
| REQ-GMS-010 | Global Search Handler | TEST-GSH-001 | Pending |
| REQ-GMS-011 | Local Search Handler | TEST-LSH-001 | Pending |
| REQ-GMS-012 | DRIFT Search Handler | TEST-DSH-001 | Pending |
| REQ-GMS-013 | Basic Search Handler | TEST-BSH-001 | Pending |
| REQ-GMS-014 | Index Builder | TEST-IDX-001 | Pending |
| REQ-GMS-015 | Prompt Tuner | TEST-PTN-001 | Pending |
| REQ-GMS-020 | Index Manager | TEST-IDM-001 | Pending |
| REQ-GMS-021 | Multi-Index Manager | TEST-MIM-001 | Pending |
| REQ-GMS-022 | Streaming Handler | TEST-STR-001 | Pending |
| REQ-GMS-030 | Error Handler | TEST-ERR-001 | Pending |
| REQ-GMS-031 | LLM Error Handler | TEST-ERR-002 | Pending |
| REQ-GMS-032 | Validation Handler | TEST-VAL-001 | Pending |
| REQ-GMS-033 | Token Manager | TEST-TOK-001 | Pending |
| REQ-GMS-040 | Azure Search Adapter | TEST-AZS-001 | Pending |
| REQ-GMS-041 | LanceDB Adapter | TEST-LDB-001 | Pending |
| REQ-GMS-042 | OpenAI Adapter | TEST-OAI-001 | Pending |
| REQ-GMS-043 | Azure OpenAI Adapter | TEST-AOA-001 | Pending |
| REQ-GMS-044 | Anthropic Adapter | TEST-ANT-001 | Pending |
| REQ-GMS-045 | File Watcher | TEST-WCH-001 | Pending |

---

## 6. Constitutional Compliance Checklist

### Article I: Library-First Principle
- [ ] Feature implemented as library in `/lib` or separate package
- [ ] Library has independent package.json/pyproject.toml
- [ ] Library has dedicated test suite
- [ ] Library exports public API
- [ ] No imports from application code

### Article II: CLI Interface Mandate
- [ ] Library provides CLI entry point
- [ ] CLI documented with --help flag
- [ ] CLI supports common operations
- [ ] CLI uses consistent argument patterns
- [ ] CLI exit codes follow conventions

### Article III: Test-First Imperative
- [ ] Tests exist before implementation
- [ ] All EARS requirements have corresponding tests
- [ ] Test coverage ≥ 80%
- [ ] Tests follow Red-Green-Blue evidence
- [ ] No production code without tests

### Article IV: EARS Requirements Format
- [x] All requirements use EARS patterns
- [x] Requirements are unambiguous
- [x] Acceptance criteria defined
- [ ] Requirements mapped to tests
- [ ] Requirements reviewed by stakeholders

### Article V: Traceability Mandate
- [x] Requirements have unique IDs (REQ-GMS-NNN)
- [ ] Design documents include requirements matrix
- [ ] Code comments reference requirement IDs
- [ ] Tests reference requirement IDs in descriptions
- [ ] `traceability-auditor` validation passes

---

## 7. Next Steps

1. **@constitution-enforcer**: 憲法準拠の検証
2. **@system-architect**: C4 アーキテクチャ設計
3. **@api-designer**: MCP インターフェース詳細設計
4. **@test-engineer**: テスト計画の策定
5. **@software-developer**: 実装タスクの分解

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | @orchestrator | Initial requirements definition |

