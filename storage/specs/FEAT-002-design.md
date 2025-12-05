# Design: Document Import for GraphRAG

**Feature ID**: FEAT-002
**Design Version**: 1.0
**Status**: Draft
**Created**: 2025-12-05
**Author**: @system-architect, @constitution-enforcer
**Parent Feature**: FEAT-001 (GraphRAG MCP Server)

---

## 1. Constitutional Compliance Validation

### 1.1 Validation Summary

| Article | Title | Status | Notes |
|---------|-------|--------|-------|
| I | Library-First Principle | ✅ PASS | REQ-DIM-001 で独立モジュール定義 |
| II | CLI Interface Mandate | ✅ PASS | REQ-DIM-002 で CLI コマンド定義 |
| III | Test-First Imperative | ✅ PASS | REQ-DIM-003 で 80% カバレッジ要件 |
| IV | EARS Requirements Format | ✅ PASS | 全19要件が EARS パターン準拠 |
| V | Traceability Mandate | ✅ PASS | 追跡マトリクス定義済み |
| VI | Project Memory | ✅ PASS | steering 参照済み |
| VII | Simplicity Gate | ✅ PASS | FEAT-001 の拡張モジュール |
| VIII | Anti-Abstraction Gate | ✅ PASS | Unstructured/GraphRAG 直接使用 |
| IX | Integration-First Testing | ✅ PASS | 実ファイルテスト計画 |

**Overall Status**: ✅ **APPROVED FOR DESIGN PHASE**

### 1.2 Article VIII Review: Anti-Abstraction

**Question**: Unstructured ライブラリをラップすることは Article VIII 違反か？

**判定**: **非違反**

**理由**:
1. Document Import モジュールは「カスタム抽象化レイヤー」ではなく「入力変換レイヤー」
2. Unstructured API を直接呼び出し、結果を GraphRAG 形式に変換するのみ
3. 独自の解析エンジンは作成しない
4. FEAT-001 の ADR-005 で除外された ETL 機能を補完する設計

**設計指針**:
```python
# ✅ 正しいパターン: Unstructured API 直接呼び出し
from unstructured.partition.auto import partition

async def parse_document(file_path: Path) -> list[Element]:
    elements = partition(filename=str(file_path))  # 直接呼び出し
    return elements  # 結果をそのまま返却

# ❌ 禁止パターン: カスタム解析エンジン
class MyDocumentParser:
    def parse(self, file_path):  # 独自API
        ...  # カスタム解析ロジック
```

---

## 2. C4 Architecture

### 2.1 Context Diagram (Level 1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              System Context                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌─────────────┐         ┌─────────────────────────┐                        │
│   │   AI User   │         │                         │                        │
│   │  (Developer)│         │  GraphRAG MCP Server    │                        │
│   │             │◄───────►│  + Document Import      │                        │
│   │ Uses Copilot│   MCP   │                         │                        │
│   │ Claude etc. │         │  [Software System]      │                        │
│   └─────────────┘         └───────────┬─────────────┘                        │
│                                       │                                       │
│        ┌──────────────────────────────┼──────────────────────────────┐       │
│        │                              │                              │       │
│        ▼                              ▼                              ▼       │
│   ┌───────────┐              ┌───────────────┐              ┌───────────┐   │
│   │ Documents │              │ GraphRAG      │              │   LLM     │   │
│   │ (PDF/DOCX │              │ Index         │              │ Provider  │   │
│   │  HTML etc)│              │ [Data Store]  │              │ (Embeddings)│ │
│   │ [External]│              │               │              │           │   │
│   └───────────┘              └───────────────┘              └───────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Container Diagram (Level 2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GraphRAG MCP Server + Document Import                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   MCP Server    │    │   Query Engine  │    │  Index Engine   │          │
│  │   [Container]   │───►│   [Container]   │    │  [Container]    │          │
│  │   (FEAT-001)    │    │   (FEAT-001)    │    │  (FEAT-001)     │          │
│  └────────┬────────┘    └─────────────────┘    └─────────────────┘          │
│           │                                                                   │
│           │ extends                                                           │
│           ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Document Import Module (FEAT-002)                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │  │ Document Parser │  │ Semantic Chunker│  │ Correlation     │       │   │
│  │  │  [Component]    │  │  [Component]    │  │ Builder         │       │   │
│  │  │                 │  │                 │  │  [Component]    │       │   │
│  │  │ - PDF/DOCX/HTML │  │ - Japanese NLP  │  │ - Structure     │       │   │
│  │  │ - Unstructured  │  │ - fugashi       │  │ - Reference     │       │   │
│  │  │ - Normalizer    │  │ - Token-based   │  │ - Semantic      │       │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘       │   │
│  │           │                    │                    │                 │   │
│  │           ▼                    ▼                    ▼                 │   │
│  │  ┌──────────────────────────────────────────────────────────────┐    │   │
│  │  │               GraphRAG Adapter [Component]                     │    │   │
│  │  │  - TextUnit 変換  - Relationship 生成  - Index Import          │    │   │
│  │  └──────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────┐              ┌─────────────────┐                       │
│  │    CLI Module   │              │  Vector Store   │                       │
│  │   [Container]   │              │   [Container]   │                       │
│  │                 │              │                 │                       │
│  │ - import        │              │ - LanceDB       │                       │
│  │ - import-dir    │              │ - Chunk Cache   │                       │
│  └─────────────────┘              └─────────────────┘                       │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Component Diagram (Level 3) - Document Import Module

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Document Import Module                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                          Parser Layer                                  │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │   │
│  │  │ DocumentParser  │    │  Normalizer     │    │ LanguageDetector│   │   │
│  │  │  [Component]    │    │  [Component]    │    │  [Component]    │   │   │
│  │  │                 │    │                 │    │                 │   │   │
│  │  │ partition()     │───►│ normalize()     │───►│ detect_lang()   │   │   │
│  │  │ (Unstructured)  │    │ Element→Normal  │    │ (langdetect)    │   │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                        │                                     │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                          Chunker Layer                                 │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │   │
│  │  │ ChunkerFactory  │    │ JapaneseChunker │    │  TokenChunker   │   │   │
│  │  │  [Component]    │    │  [Component]    │    │  [Component]    │   │   │
│  │  │                 │    │                 │    │                 │   │   │
│  │  │ create(lang)    │───►│ chunk_ja()      │    │ chunk_token()   │   │   │
│  │  │                 │    │ (fugashi)       │    │ (tiktoken)      │   │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                        │                                     │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Correlation Layer                               │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │   │
│  │  │ StructuralCorr  │    │ ReferenceCorr   │    │  SemanticCorr   │   │   │
│  │  │  [Component]    │    │  [Component]    │    │  [Component]    │   │   │
│  │  │                 │    │                 │    │   (Optional)    │   │   │
│  │  │ same_section    │    │ links/citations │    │ embedding_sim   │   │   │
│  │  │ sequential      │    │                 │    │                 │   │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                        │                                     │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Adapter Layer                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │   │
│  │  │                  GraphRAGAdapter [Component]                     │  │   │
│  │  │                                                                   │  │   │
│  │  │  chunks_to_textunits()   correlations_to_relationships()         │  │   │
│  │  │  import_to_index()       generate_correlation_graph()            │  │   │
│  │  └─────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Package Structure

```
lib/graphrag-mcp-server/
├── pyproject.toml              # 依存関係追加
├── src/
│   └── graphrag_mcp_server/
│       ├── __init__.py         # パブリック API エクスポート更新
│       │
│       ├── import/             # REQ-DIM-001: Document Import モジュール
│       │   ├── __init__.py     # パブリック API
│       │   │   └── exports: DocumentImporter, ChunkProcessor, CorrelationBuilder
│       │   │
│       │   ├── models.py       # データモデル定義
│       │   │   ├── NormalizedElement
│       │   │   ├── TextChunk
│       │   │   ├── ChunkCorrelation
│       │   │   ├── CorrelationType (Enum)
│       │   │   ├── ImportState (Enum)
│       │   │   └── ImportResult
│       │   │
│       │   ├── parser.py       # REQ-DIM-010, REQ-DIM-011
│       │   │   ├── DocumentParser
│       │   │   │   └── parse(file_path) → list[Element]
│       │   │   └── ElementNormalizer
│       │   │       └── normalize(elements) → list[NormalizedElement]
│       │   │
│       │   ├── chunker/        # REQ-DIM-012, REQ-DIM-013
│       │   │   ├── __init__.py
│       │   │   ├── base.py     # BaseChunker ABC
│       │   │   ├── japanese.py # JapaneseSemanticChunker
│       │   │   │   └── chunk(text, max_tokens, overlap) → list[TextChunk]
│       │   │   ├── token.py    # TokenChunker (for English)
│       │   │   └── factory.py  # ChunkerFactory
│       │   │       └── create(language) → BaseChunker
│       │   │
│       │   ├── language.py     # REQ-DIM-013: 言語検出
│       │   │   └── LanguageDetector
│       │   │       └── detect(text) → str ("ja", "en", "mixed")
│       │   │
│       │   ├── correlation.py  # REQ-DIM-014: 相関抽出
│       │   │   ├── CorrelationBuilder
│       │   │   │   └── build(chunks) → list[ChunkCorrelation]
│       │   │   ├── StructuralCorrelator
│       │   │   ├── ReferenceCorrelator
│       │   │   └── SemanticCorrelator (optional)
│       │   │
│       │   ├── adapter.py      # REQ-DIM-015: GraphRAG 変換
│       │   │   └── GraphRAGAdapter
│       │   │       ├── chunks_to_textunits(chunks) → DataFrame
│       │   │       ├── correlations_to_relationships(corrs) → DataFrame
│       │   │       └── import_to_index(chunks, correlations, index_path)
│       │   │
│       │   ├── importer.py     # メイン API
│       │   │   └── DocumentImporter
│       │   │       └── import_document(file_path, options) → ImportResult
│       │   │
│       │   └── cache.py        # REQ-DIM-021: チャンクキャッシュ
│       │       └── ChunkCache
│       │           ├── get(file_hash) → list[TextChunk] | None
│       │           └── set(file_hash, chunks)
│       │
│       ├── cli/
│       │   ├── main.py         # 既存 CLI
│       │   └── import_cmd.py   # REQ-DIM-002: import コマンド
│       │       ├── import_file(path, options)
│       │       └── import_directory(path, options)
│       │
│       ├── server/
│       │   └── tools.py        # REQ-DIM-016: MCP Tools 追加
│       │       ├── graphrag_import_document
│       │       ├── graphrag_import_directory
│       │       ├── graphrag_list_supported_formats
│       │       └── graphrag_get_chunk_correlations
│       │
│       └── handlers/
│           └── import_handler.py  # インポートハンドラー
│               └── ImportHandler
│                   └── handle_import(request) → ImportResult
│
└── tests/
    ├── unit/
    │   ├── test_parser.py
    │   ├── test_chunker_japanese.py
    │   ├── test_chunker_token.py
    │   ├── test_correlation.py
    │   └── test_adapter.py
    ├── integration/
    │   ├── test_import_pdf.py
    │   ├── test_import_docx.py
    │   ├── test_import_html.py
    │   └── test_import_directory.py
    └── fixtures/
        └── documents/
            ├── sample_ja.pdf
            ├── sample_ja.docx
            ├── sample_en.pdf
            └── sample_mixed.html
```

---

## 4. ADR (Architecture Decision Records)

### ADR-006: Unstructured for Document Parsing

**Status**: Accepted

**Context**: 
多様なドキュメント形式（PDF、DOCX、HTML等）を解析する必要がある。

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Unstructured | 多形式対応、構造抽出優秀、活発な開発 | 依存関係が多い |
| Apache Tika | Java ベース、安定 | Python バインディングが別途必要 |
| PyMuPDF | PDF 特化、高速 | 他形式非対応 |
| python-docx | DOCX 特化 | 他形式非対応 |

**Decision**: 
Unstructured を採用する。

**Consequences**:
- ✅ 単一ライブラリで多形式対応
- ✅ 構造情報（見出し、段落、表）の抽出が容易
- ✅ 活発なメンテナンス
- ⚠️ インストールサイズが大きい（オプション依存）

**Constitutional Reference**: Article VIII (直接利用)

---

### ADR-007: fugashi for Japanese Tokenization

**Status**: Accepted

**Context**: 
日本語テキストのセマンティックチャンキングには形態素解析が必要。

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| fugashi | MeCab 互換、高速、pip install 可能 | 辞書が別途必要 |
| sudachi | 高精度、分割モード選択可 | やや重い |
| janome | 純 Python、インストール容易 | 速度が遅い |
| spaCy (ja) | NLP パイプライン統合 | オーバースペック |

**Decision**: 
fugashi + unidic-lite を採用する。

**Consequences**:
- ✅ 高速な形態素解析
- ✅ pip だけでインストール完了
- ✅ 軽量な辞書 (unidic-lite)
- ⚠️ 専門用語の分割精度は辞書依存

**Constitutional Reference**: Article VII (Simplicity)

---

### ADR-008: Structural Correlation First

**Status**: Accepted

**Context**: 
チャンク間の相関をどのように抽出するか。

**Options Considered**:
1. 構造的相関のみ（同一セクション、隣接関係）
2. 参照相関追加（リンク、引用）
3. 意味的相関追加（埋め込み類似度）

**Decision**: 
Phase 1 では構造的相関と参照相関を実装。意味的相関はオプション機能として Phase 2 で追加。

**Rationale**:
- 構造的相関は低コストで高精度
- 意味的相関は LLM API 呼び出しが必要でコスト高
- 段階的実装で早期価値提供

**Consequences**:
- ✅ 初期実装がシンプル
- ✅ LLM 依存なしで基本機能動作
- ⚠️ 意味的相関は後日追加

**Constitutional Reference**: Article VII (Simplicity Gate)

---

### ADR-009: Cache by File Hash

**Status**: Accepted

**Context**: 
同じドキュメントの再処理を避けるためのキャッシュ戦略。

**Decision**: 
ファイルの SHA-256 ハッシュをキーとしてチャンク結果をキャッシュする。

**Implementation**:
```python
import hashlib

def compute_file_hash(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
```

**Consequences**:
- ✅ ファイル内容が同一なら再利用
- ✅ ファイル名変更でも動作
- ⚠️ 大ファイルのハッシュ計算コスト

**Constitutional Reference**: Performance Optimization

---

### ADR-010: Integration with FEAT-001 Package

**Status**: Accepted

**Context**: 
Document Import を別パッケージにするか、FEAT-001 の拡張にするか。

**Decision**: 
FEAT-001 (`graphrag-mcp-server`) パッケージ内のサブモジュールとして実装する。

**Rationale**:
1. Article VII 準拠（3プロジェクト以下）
2. 依存関係の一元管理
3. MCP Server との統合が容易
4. オプション依存で分離可能

**Consequences**:
- ✅ 単一パッケージでインストール
- ✅ MCP Tools の自動登録
- ⚠️ パッケージサイズ増加（オプション依存で軽減）

**Constitutional Reference**: Article VII

---

## 5. Interface Specifications

### 5.1 CLI Interface (REQ-DIM-002)

```bash
# 単一ファイルインポート
graphrag-mcp import <file_path> [OPTIONS]
  --language [auto|ja|en]     # 言語指定 (default: auto)
  --chunk-strategy [semantic|token|sentence]  # チャンク戦略 (default: semantic)
  --max-chunk-tokens INT      # 最大トークン数 (default: 300)
  --overlap-tokens INT        # オーバーラップ (default: 50)
  --index-path PATH           # インデックスパス (default: ./graphrag_index)
  --no-cache                  # キャッシュ無効化
  --output-correlations PATH  # 相関グラフ出力 (JSON/GraphML)

# ディレクトリインポート
graphrag-mcp import-dir <directory_path> [OPTIONS]
  --format [pdf,docx,html,md,txt]  # 対象形式 (default: all)
  --recursive                       # サブディレクトリ含む
  --parallel INT                    # 並列処理数 (default: 4)
  [上記オプション全て]

# サポート形式一覧
graphrag-mcp import --list-formats

# 使用例
graphrag-mcp import ./docs/report.pdf --language ja
graphrag-mcp import-dir ./docs/ --format pdf,docx --recursive
```

### 5.2 MCP Tools Schema (REQ-DIM-016)

```json
{
  "tools": [
    {
      "name": "graphrag_import_document",
      "description": "Import a document into GraphRAG index with semantic chunking. Supports PDF, DOCX, PPTX, HTML, and Markdown files. Automatically detects language and applies appropriate chunking strategy.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Absolute path to the document file"
          },
          "language": {
            "type": "string",
            "enum": ["auto", "ja", "en"],
            "default": "auto",
            "description": "Document language (auto-detected if not specified)"
          },
          "chunk_strategy": {
            "type": "string",
            "enum": ["semantic", "token", "sentence"],
            "default": "semantic",
            "description": "Chunking strategy (semantic recommended for Japanese)"
          },
          "max_chunk_tokens": {
            "type": "integer",
            "default": 300,
            "description": "Maximum tokens per chunk"
          },
          "overlap_tokens": {
            "type": "integer",
            "default": 50,
            "description": "Overlap tokens between chunks"
          },
          "extract_correlations": {
            "type": "boolean",
            "default": true,
            "description": "Extract chunk correlations"
          }
        },
        "required": ["file_path"]
      }
    },
    {
      "name": "graphrag_import_directory",
      "description": "Import all documents in a directory into GraphRAG index",
      "inputSchema": {
        "type": "object",
        "properties": {
          "directory_path": {
            "type": "string",
            "description": "Path to the directory containing documents"
          },
          "formats": {
            "type": "array",
            "items": {"type": "string"},
            "default": ["pdf", "docx", "html", "md", "txt"],
            "description": "File formats to import"
          },
          "recursive": {
            "type": "boolean",
            "default": false,
            "description": "Include subdirectories"
          },
          "language": {
            "type": "string",
            "enum": ["auto", "ja", "en"],
            "default": "auto"
          },
          "chunk_strategy": {
            "type": "string",
            "enum": ["semantic", "token", "sentence"],
            "default": "semantic"
          }
        },
        "required": ["directory_path"]
      }
    },
    {
      "name": "graphrag_list_supported_formats",
      "description": "List all supported document formats for import",
      "inputSchema": {
        "type": "object",
        "properties": {}
      }
    },
    {
      "name": "graphrag_get_chunk_correlations",
      "description": "Get correlation graph between chunks for a document",
      "inputSchema": {
        "type": "object",
        "properties": {
          "document_id": {
            "type": "string",
            "description": "Document ID or file path"
          },
          "correlation_types": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["structural", "reference", "semantic", "sequential"]
            },
            "default": ["structural", "reference", "sequential"],
            "description": "Types of correlations to include"
          },
          "format": {
            "type": "string",
            "enum": ["json", "graphml"],
            "default": "json",
            "description": "Output format"
          }
        },
        "required": ["document_id"]
      }
    }
  ]
}
```

### 5.3 Python API

```python
from graphrag_mcp_server.import import (
    DocumentImporter,
    ChunkProcessor,
    CorrelationBuilder,
    ImportOptions,
    ImportResult,
)

# シンプルなインポート
importer = DocumentImporter(index_path="./graphrag_index")
result: ImportResult = await importer.import_document(
    file_path="./docs/report.pdf",
    language="ja",
    chunk_strategy="semantic",
)

print(f"Imported {result.chunk_count} chunks")
print(f"Found {result.correlation_count} correlations")

# カスタムオプション
options = ImportOptions(
    max_chunk_tokens=400,
    overlap_tokens=100,
    extract_correlations=True,
    cache_enabled=True,
)
result = await importer.import_document("./docs/report.pdf", options=options)

# 個別コンポーネント使用
from graphrag_mcp_server.import.parser import DocumentParser
from graphrag_mcp_server.import.chunker import JapaneseSemanticChunker

parser = DocumentParser()
elements = parser.parse("./docs/report.pdf")

chunker = JapaneseSemanticChunker(max_tokens=300, overlap=50)
chunks = chunker.chunk(elements)

correlation_builder = CorrelationBuilder()
correlations = correlation_builder.build(chunks)
```

---

## 6. Data Models

### 6.1 Core Models

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from datetime import datetime

class CorrelationType(Enum):
    """チャンク間相関の種類"""
    STRUCTURAL_SAME_SECTION = "structural_same_section"
    STRUCTURAL_SAME_DOCUMENT = "structural_same_document"
    REFERENCE_LINK = "reference_link"
    REFERENCE_CITATION = "reference_citation"
    SEMANTIC_SIMILAR = "semantic_similar"
    SEQUENTIAL_NEXT = "sequential_next"
    SEQUENTIAL_PREV = "sequential_prev"
    PARENT_CHILD = "parent_child"

class ImportState(Enum):
    """インポート処理状態"""
    PENDING = "pending"
    PARSING = "parsing"
    CHUNKING = "chunking"
    CORRELATING = "correlating"
    IMPORTING = "importing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class NormalizedElement:
    """正規化されたドキュメント要素"""
    id: str
    text: str
    element_type: str  # Title, NarrativeText, Table, ListItem, etc.
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)
    
    # メタデータ例:
    # - page_number: int
    # - section: str
    # - source_file: str
    # - coordinates: dict (optional)

@dataclass
class TextChunk:
    """チャンク化されたテキスト単位"""
    id: str
    text: str
    token_count: int
    language: str  # "ja", "en", "mixed"
    source_elements: list[str]  # 元の NormalizedElement ID リスト
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # メタデータ例:
    # - chunk_index: int
    # - start_page: int
    # - end_page: int
    # - section_path: list[str]

@dataclass
class ChunkCorrelation:
    """チャンク間の相関関係"""
    source_chunk_id: str
    target_chunk_id: str
    correlation_type: CorrelationType
    weight: float = 1.0  # 相関の強さ (0.0 - 1.0)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ImportResult:
    """インポート結果"""
    success: bool
    document_id: str
    file_path: str
    chunk_count: int
    correlation_count: int
    processing_time_ms: int
    state: ImportState
    error_message: str | None = None
    chunks: list[TextChunk] = field(default_factory=list)
    correlations: list[ChunkCorrelation] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)

@dataclass
class ImportProgress:
    """インポート進捗"""
    state: ImportState
    current_file: str
    processed_files: int
    total_files: int
    processed_chunks: int
    estimated_remaining_seconds: int | None = None
```

---

## 7. Test Strategy

### 7.1 Test Categories

| Category | Purpose | Real Services | Coverage Target |
|----------|---------|---------------|-----------------|
| Unit | 個別コンポーネント | No | 90% |
| Integration | ファイル処理統合 | Real files | 80% |
| E2E | フルインポートフロー | All real | 70% |

### 7.2 Test Fixtures

```
tests/fixtures/documents/
├── pdf/
│   ├── sample_ja_simple.pdf      # 日本語単純テキスト
│   ├── sample_ja_complex.pdf     # 日本語複雑構造 (表、画像)
│   ├── sample_en_simple.pdf      # 英語単純テキスト
│   └── sample_mixed.pdf          # 日英混在
├── docx/
│   ├── sample_ja.docx
│   └── sample_en.docx
├── html/
│   ├── sample_ja.html
│   └── sample_structured.html    # 複雑な HTML 構造
├── markdown/
│   ├── sample_ja.md
│   └── sample_with_code.md       # コードブロック含む
└── corrupted/
    ├── invalid.pdf               # 破損ファイル
    └── password_protected.pdf    # パスワード保護
```

### 7.3 Key Test Cases

```python
# tests/unit/test_chunker_japanese.py
class TestJapaneseSemanticChunker:
    def test_respects_sentence_boundary(self):
        """文の途中で切れないことを確認"""
        
    def test_respects_paragraph_boundary(self):
        """段落境界を尊重することを確認"""
        
    def test_max_token_limit(self):
        """最大トークン数制限を確認"""
        
    def test_overlap_tokens(self):
        """オーバーラップが正しく設定されることを確認"""

# tests/integration/test_import_pdf.py
class TestPDFImport:
    def test_import_japanese_pdf(self, sample_ja_pdf):
        """日本語 PDF のインポートを確認"""
        
    def test_import_preserves_structure(self, structured_pdf):
        """構造情報が保持されることを確認"""
        
    def test_correlation_extraction(self, multi_section_pdf):
        """相関が正しく抽出されることを確認"""
```

---

## 8. Traceability Matrix

| Requirement | Design Component | Source File | Test File |
|-------------|------------------|-------------|-----------|
| REQ-DIM-001 | Package Structure | `import/__init__.py` | - |
| REQ-DIM-002 | CLI Import Commands | `cli/import_cmd.py` | `test_cli_import.py` |
| REQ-DIM-003 | Test Coverage | `tests/` | All tests |
| REQ-DIM-004 | Security | `import/importer.py` | `test_security.py` |
| REQ-DIM-010 | DocumentParser | `import/parser.py` | `test_parser.py` |
| REQ-DIM-011 | ElementNormalizer | `import/parser.py` | `test_normalizer.py` |
| REQ-DIM-012 | JapaneseSemanticChunker | `import/chunker/japanese.py` | `test_chunker_japanese.py` |
| REQ-DIM-013 | LanguageDetector, ChunkerFactory | `import/language.py`, `chunker/factory.py` | `test_language.py` |
| REQ-DIM-014 | CorrelationBuilder | `import/correlation.py` | `test_correlation.py` |
| REQ-DIM-015 | GraphRAGAdapter | `import/adapter.py` | `test_adapter.py` |
| REQ-DIM-016 | MCP Tools | `server/tools.py` | `test_mcp_import.py` |
| REQ-DIM-020 | ImportProgress | `import/importer.py` | `test_progress.py` |
| REQ-DIM-021 | ChunkCache | `import/cache.py` | `test_cache.py` |
| REQ-DIM-030 | Error Handling | `import/importer.py` | `test_error_handling.py` |
| REQ-DIM-031 | Memory Management | `import/parser.py` | `test_memory.py` |
| REQ-DIM-032 | Path Validation | `import/importer.py` | `test_security.py` |

---

## 9. Dependencies Update

### 9.1 pyproject.toml Changes

```toml
[project]
dependencies = [
    # 既存の依存関係
    "fastmcp>=0.1.0",
    "typer>=0.9.0",
    # ... 他の既存依存
    
    # FEAT-002 追加依存
    "langdetect>=1.0.9",
    "networkx>=3.0",
]

[project.optional-dependencies]
# ドキュメントインポート機能
import = [
    "unstructured>=0.10.0",
    "fugashi>=1.3.0",
    "unidic-lite>=1.0.8",
]

# PDF サポート
pdf = [
    "unstructured[pdf]>=0.10.0",
]

# DOCX サポート  
docx = [
    "unstructured[docx]>=0.10.0",
]

# 全形式サポート
all-formats = [
    "unstructured[all-docs]>=0.10.0",
    "fugashi>=1.3.0",
    "unidic-lite>=1.0.8",
]

# 開発用
dev = [
    # 既存の dev 依存
    "graphrag-mcp-server[import,pdf,docx]",  # インポート機能のテスト用
]
```

### 9.2 Installation Commands

```bash
# 基本インストール (インポート機能なし)
pip install graphrag-mcp-server

# インポート機能付き
pip install graphrag-mcp-server[import]

# PDF サポート付き
pip install graphrag-mcp-server[import,pdf]

# 全形式サポート
pip install graphrag-mcp-server[all-formats]
```

---

## 10. Next Steps

1. **@task-planner**: FEAT-002-tasks.md でタスク分解
2. **@software-developer**: Phase 1 (Core Parser) から実装開始
3. **@test-engineer**: テストフィクスチャの準備

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | @system-architect | Initial design |
| 1.0 | 2025-12-05 | @constitution-enforcer | Compliance validation |
