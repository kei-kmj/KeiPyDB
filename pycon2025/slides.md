---
theme: seriph
background: '#f9fafb'
colorSchema: 'light'
class: text-center
css: unocss
highlighter: shiki
lineNumbers: false
info: |
  ## Python製RDBMSで理解する、データベースのピース
  PyCon JP 2025
drawings:
  persist: false
transition: slide-left
title: Python製RDBMSで理解する、データベースのピース
mdc: true
hideInToc: true
---

<style>
html {
  --slidev-theme-primary: #454554;
}
.slidev-layout {
  background-color: #f9fafb !important;
  color: #454554 !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, li, td, th {
  color: #454554 !important;
}
.slidev-page-number {
  position: absolute;
  bottom: 1rem;
  right: 2rem;
  color: #888;
  font-size: 0.85rem;
}
</style>

# Python製RDBMSで理解する、<br>データベースのピース

<div class="mt-12">

### コードのステップ実行とヘックスビューアーで<br>内部動作を追ってみよう

</div>

<div class="absolute bottom-12 left-0 right-0">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    PyCon JP 2025 →
  </span>
</div>

<div class="absolute bottom-6 left-0 right-0 text-gray-500">
  @Keiko Kamijo
</div>

<div class="slidev-page-number">
  1
</div>

<!-- スライド2: 自己紹介 -->
---
layout: two-cols
---

<style scoped>
.col-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
  padding-left: 2rem;
  white-space: nowrap;
}
.col-right {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-end;
  height: 100%;
  padding-right: 2rem;
  margin-top: -4rem;
}
.col-right img:first-child {
  width: 20rem;
  height: 20rem;
  margin-bottom: 0.5rem;
}
.col-right img:last-child {
  width: 14rem;
  height: auto;
}
h1 { font-size: 2.5rem !important; }
h2 { font-size: 1.75rem !important; }
h3, p { font-size: 1.5rem !important; }
</style>

<div class="col-left">

# 自己紹介
<br>

### 上條 恵子 Keiko Kamijo
<br>

### 💻 GitHub: @kei-kmj
### 𝕏 Twitter: @kamijima
<br>

### 株式会社デルタX エンジニア
<br>

### 夫と子供をほったらかして、
### サイゼリアで読書しながら一人飲みするのがたまの楽しみ

</div>

::right::

<div class="col-right">

![Keiko Kamijo](/avatar.png)

<br>

![DeltaX](/deltax-logo.png)

</div>

<div class="slidev-page-number">
  2
</div>

<!-- スライド3: bestjuku.png（暗い背景） -->
---
layout: center
---

<style scoped>
.slidev-layout {
  background-color: #111827 !important;
}
</style>

<div class="flex items-center justify-center h-full">
  <img src="/bestjuku.png" style="max-width: 70%; max-height: 90%; object-fit: contain;" />
</div>

<div class="slidev-page-number" style="color: #ccc;">
  3
</div>

<!---->

<!-- スライド4: img.png（全画面） -->
---
layout: cover
background: /img.png
---

<!---->

<div class="slidev-page-number">
  4
</div>

<!-- スライド5: 今日の内容 -->
---

# 今日の内容

## 話すこと
- 内容は後で追加
- 内容は後で追加  
- 内容は後で追加

## 話さないこと
- SQL文の書き方
- DBの使い方や最適化

<div class="slidev-page-number">
  5
</div>

<!-- ==================== -->
<!-- スライド6: データベースとは？ -->
<!-- ==================== -->
---

# データベースとは？

## データを永続的に保存し、効率的に管理するシステム

<br>

### 主な特徴
- **永続性**: プログラムが終了してもデータが残る
- **並行性**: 複数のユーザーが同時アクセス可能
- **整合性**: データの一貫性を保証
- **効率性**: 大量データから高速検索

<br>

### 様々な種類のデータベース
**RDBMS** (MySQL, PostgreSQL)｜**NoSQL** (MongoDB, Redis)｜**グラフDB** (Neo4j)｜**時系列DB** (InfluxDB)

→ 今日はRDBMSに注目！

<div class="slidev-page-number">
  6
</div>

<!-- ==================== -->
<!-- スライド7: RDBMSとは？ -->
<!-- ==================== -->
---

# RDBMSとは？

## Relational Database Management System

<br>

### 特徴

- データを**表（テーブル）**で管理
- **SQL**という共通言語で操作
- **リレーショナルモデル**に基づく設計

<br>

### 代表的なRDBMS

PostgreSQL, MySQL, Oracle, SQL Server, SQLite...

<div class="slidev-page-number">
  7
</div>

<!-- ==================== -->
<!-- スライド8: RDBMSのアーキテクチャ -->
<!-- ==================== -->
---
layout: two-cols
---

# RDBMSのアーキテクチャ

<style scoped>
.col-left {
  padding-right: 1rem;
}
.col-right {
  padding-left: 1rem;
}
table {
  font-size: 0.85rem;
  width: 100%;
}
td, th {
  padding: 0.5rem 1rem;
  line-height: 1.8;
}
</style>

<div class="col-left">

```
┌─────────────────────┐
│   SQLクエリ          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│    パーサー        　 │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   プランナー          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   実行エンジン        │   
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  トランザクション他    │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  ファイルマネージャー   │
└─────────────────────┘
```

</div>

::right::

<div class="col-right" style="display: flex; align-items: center; justify-content: center; height: 100%;">

<div style="width: 100%;">

| コンポーネント | 役割 |
|:--------------|:-----|
| **パーサー** | SQL文を解析し内部表現に変換 |
| **プランナー** | 最適な実行計画を選択 |
| **実行エンジン** | 実際にデータを読み書き |
| **トランザクション管理** | ACID特性の保証 |
| **メタデータ管理** | テーブル構造・統計情報管理 |
| **バッファ管理** | メモリキャッシュ管理 |
| **ファイル管理** | ディスクI/O制御 |

</div>

</div>

<div class="slidev-page-number">
  8
</div>

<!-- ==================== -->
<!-- スライド9: SQLクエリの処理フロー -->
<!-- ==================== -->
---

# SQLクエリの処理フロー

## 例: `SELECT name FROM users WHERE name = 'alice'`

<br>

### 1. パーサー
```
"SELECT name FROM users WHERE name = 'alice'"
    ↓ Lexer
[SELECT] [name] [FROM] [users] [WHERE] [name] [=] ['alice']
    ↓ Parser
QueryData { fields: ["name"], tables: ["users"], pred: "name = 'alice'" }
```

### 2. プランナー
```
TableScan("users")
    ↓
SelectScan(pred: "name = 'alice'")
    ↓
ProjectScan(fields: ["name"])
```

### 3. 実行
```python
scan.open()
while scan.next():
    print(scan.getString("name"))
scan.close()
```

<div class="slidev-page-number">
  9
</div>

<!-- ==================== -->
<!-- スライド10: パーサーデモ - 導入 -->
<!-- ==================== -->
---

# パーサーのステップ実行デモ

## SQLがどのように解析されるか見てみよう！

<br>

### デモで使うSQL
```sql
SELECT name FROM users WHERE name = 'alice'
```

<br>

### パーサーの2つのステップ
1. **字句解析（Lexer）** - 文字列をトークンに分割
2. **構文解析（Parser）** - トークンから構造を作る

<div class="slidev-page-number">
  10
</div>

<!-- ==================== -->
<!-- スライド11: 字句解析のステップ実行 -->
<!-- ==================== -->
---

# ステップ1: 字句解析（Lexer）

<style scoped>
.token-box {
  display: inline-block;
  background: #e5e7eb;
  padding: 0.25rem 0.75rem;
  margin: 0.25rem;
  border-radius: 0.25rem;
  font-family: monospace;
}
.arrow {
  font-size: 1.5rem;
  margin: 1rem 0;
}
</style>

## 入力SQL
```sql
SELECT name FROM users WHERE name = 'alice'
```

<p class="arrow">↓</p>

## トークン化の過程

<div style="margin-top: 1rem;">
  <span class="token-box">SELECT</span>
  <span class="token-box">name</span>
  <span class="token-box">FROM</span>
  <span class="token-box">users</span>
  <span class="token-box">WHERE</span>
  <span class="token-box">name</span>
  <span class="token-box">=</span>
  <span class="token-box">'alice'</span>
</div>

<br>

### Pythonコードで確認
```python
from db.parse.lexer import Lexer

lex = Lexer("SELECT name FROM users WHERE name = 'alice'")
while not lex.is_done():
    print(f"Token: {lex.current_token}")
    lex.next()
```

<div class="slidev-page-number">
  11
</div>

<!-- ==================== -->
<!-- スライド12: 字句解析の実行結果 -->
<!-- ==================== -->
---

# Lexerの実行結果

<style scoped>
.output-box {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  font-family: monospace;
  font-size: 0.9rem;
  line-height: 1.6;
}
.highlight {
  color: #fbbf24;
}
</style>

## デバッガーでステップ実行

<div class="output-box">
Token: SELECT (type: KEYWORD)<br>
Token: name (type: ID)<br>
Token: , (type: DELIMITER)<br>
Token: FROM (type: KEYWORD)<br>
Token: users (type: ID)<br>
Token: WHERE (type: KEYWORD)<br>
Token: name (type: ID)<br>
Token: = (type: DELIMITER)<br>
Token: 'alice' (type: STRING_CONSTANT)<br>
</div>

<br>

### トークンの種類
- **KEYWORD**: SQL予約語（SELECT, FROM, WHERE）
- **ID**: 識別子（テーブル名、カラム名）
- **DELIMITER**: 区切り文字（,、>）
- **INT_CONSTANT**: 整数定数

<div class="slidev-page-number">
  12
</div>

<!-- ==================== -->
<!-- スライド13: 構文解析のステップ -->
<!-- ==================== -->
---

# ステップ2: 構文解析（Parser）

### 入力（トークン列）
```text
[SELECT] [name] [FROM] [users] [WHERE] [name] [=] ['alice']
```

### 出力（QueryData オブジェクト）
```text
QueryData {
    fields: ["name"],
    tables: ["users"],
    predicate: Predicate {
        left: Term("name", type=FIELD),
        operator: "=",
        right: Term("alice", type=CONSTANT)
    }
}
```

### Pythonコードで確認
```python
parser = Parser("SELECT name FROM users WHERE name = 'alice'")
query_data = parser.query()
print(f"Fields: {query_data.fields}")
print(f"Tables: {query_data.tables}")
print(f"Predicate: {query_data.pred}")
```

<div class="slidev-page-number">
  13
</div>

---

