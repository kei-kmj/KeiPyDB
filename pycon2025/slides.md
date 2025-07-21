<!-- スライド1: タイトル -->
---
theme: seriph
background: '#f9fafb'
colorSchema: 'light'
class: text-center
css: unocss
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

<!---->

<!-- スライド4: img.png（全画面） -->
---
layout: cover
background: /img.png
---

<!---->

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

<!-- ==================== -->
<!-- スライド8: RDBMSのアーキテクチャ -->
<!-- ==================== -->
---

# RDBMSのアーキテクチャ

```
┌─────────────────────────────────────────────┐
│            SQLクエリ/更新コマンド              │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│               パーサー (Parser)               │
│  • 字句解析 (Lexer) → トークン分割              │
│  • 構文解析 → QueryData/UpdateDataオブジェクト  │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│          プランナー / クエリ最適化              │
│  • 実行計画の生成・最適化                       │
│  • コスト見積もり・統計情報活用                  │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│             実行エンジン (Scan)               │
│  • TableScan, SelectScan, ProductScan等      │
│  • パイプライン処理でレコード取得                │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│           各種マネージャー層                   │
├─────────────────────┴───────────────────────┤
│ メタデータ │ レコード │ トランザクション │ メモリ │
│ マネージャー│マネージャー│  マネージャー  │マネージャー│
└─────────────────────┴───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│          ファイルマネージャー                  │
│         ディスクI/O・永続化                   │
└─────────────────────────────────────────────┘
```

<!-- ==================== -->
<!-- スライド9: 主要コンポーネントの役割 -->
<!-- ==================== -->
---

# 主要コンポーネントの役割

<style scoped>
table {
  font-size: 0.9rem;
}
</style>

| コンポーネント | 役割 | SimpleDBクラス |
|:--------------|:-----|:---------------|
| **パーサー** | SQL文を解析し内部表現に変換 | Lexer, Parser |
| **プランナー** | 最適な実行計画を選択 | BasicQueryPlanner |
| **実行エンジン** | 実際にデータを読み書き | TableScan, SelectScan |
| **メタデータ管理** | テーブル構造・統計情報管理 | MetadataMgr |
| **トランザクション管理** | ACID特性の保証 | Transaction, LockTable |
| **バッファ管理** | メモリキャッシュ管理 | BufferMgr |
| **ファイル管理** | ディスクI/O制御 | FileMgr, BlockId |

<!-- ==================== -->
<!-- スライド10: SQLクエリの処理フロー -->
<!-- ==================== -->
---

# SQLクエリの処理フロー

## 例: `SELECT name FROM users WHERE age > 20`

<br>

### 1. パーサー
```
"SELECT name FROM users WHERE age > 20"
    ↓ Lexer
[SELECT] [name] [FROM] [users] [WHERE] [age] [>] [20]
    ↓ Parser
QueryData { fields: ["name"], tables: ["users"], pred: "age > 20" }
```

### 2. プランナー
```
TableScan("users")
    ↓
SelectScan(pred: "age > 20")
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

---

