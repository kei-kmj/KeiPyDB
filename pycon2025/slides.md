<style>
/* グローバルフォントサイズの統一設定 */
.slidev-layout {
  font-size: 1.1rem !important;
}
.slidev-layout h1 {
  font-size: 2.0em !important;
  line-height: 1.2 !important;
  margin: 2.5rem 0 1rem 0 !important;
}
.slidev-layout h2 {
  font-size: 1.4em !important;
  line-height: 1.2 !important;
  margin: 1.2rem 0 0.8rem 0 !important;
}
.slidev-layout h3 {
  font-size: 1.3em !important;
  line-height: 1.1 !important;
  margin: 1rem 0 0.6rem 0 !important;
}
.slidev-layout p {
  font-size: 1.3em !important;
  line-height: 1.5 !important;
}
.slidev-layout ul li, .slidev-layout ol li {
  font-size: 1.3em !important;
  line-height: 1.5 !important;
}
.slidev-layout pre code {
  font-size: 0.95em !important;
  line-height: 1.4 !important;
}
.slidev-layout table {
  font-size: 1em !important;
}
.slidev-layout td, .slidev-layout th {
  font-size: 0.95em !important;
  line-height: 1.4 !important;
}
/* コード内のインラインコード */
.slidev-layout code:not(pre code) {
  font-size: 0.9em !important;
}

/* 赤文字スタイル */
.red-uppercase {
  color: #DC143C !important;
  font-weight: bold !important;
}

/* オレンジ文字スタイル */
.orange-uppercase {
  color: #FF6600 !important;
  font-weight: bold !important;
}
</style>

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.3);" />
</div>
<!-- タイトル -->

# Python製RDBMSで理解する、データベースのピース

## 〜 コードのステップ実行とヘックスビュアーで内部動作を追ってみよう 〜


<br>

## PyCon JP 2025

## k-kamijo

<!-- スピーカーノート：
〜の発表をしたいと思います。よろしくお願いします
-->
---

<!-- Page 1 自己紹介-->

<CustomTwoCols :leftRatio="60">
<template v-slot:left>


# 自己紹介

<br>

<div style="width: 100%;">
<TransparentTable :items="[
  { label: '名　前：', value: 'k-kamijo' },
  { label: 'Github：', value: '@kei-kmj' },
  { label: '所　属：', value: '株式会社DeltaX' },
  { label: '趣　味：', value: '輪行<br>(電車旅 & サイクリング)' }
]" />
</div>
</template>
<template v-slot:right>
<div class="flex justify-center items-center h-full">
  <img src="/tokageusagi.png" class="w-64 h-64 rounded-full object-cover" />
</div>
</template>
</CustomTwoCols>

---
background: none
---

<style scoped>
.slidev-layout::before {
  display: none !important;
}
</style>

<div style="background-color: #f5f5f5; position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: -1;"></div>

<!-- Page 2 塾選紹介-->

<img src="/bestjuku.png" style="position: absolute; top: 20px; left: 0; right: 0; bottom: 30px; width: 100%; height: calc(100% - 30px); object-fit: contain;" />

<!--
スピーカーノート：
デルタxという会社名は、あまり聞きなれないと思いますが、
塾選という学習塾検索サイトを運営している会社です。
-->
---
background: none
---

<style scoped>
.slidev-layout::before {
  display: none !important;
}
</style>

<div style="background-color: #f5f5f5; position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: -1;"></div>

<!-- Page 3 CMスクショ-->

<img src="/cm.png" style="position: absolute; top: 0; left: 0; right: 0; bottom: 30px; width: 100%; height: calc(100% - 30px); object-fit: contain;" />
<!--
スピーカーノート：
関東圏にお住まいの方であれば、お笑い芸人のかが屋さんのCMを見たことがある方がいらっしゃるかもしれません。
このCMのサービスの会社です。
手前味噌ですが、このCMはYou Tubeで公開されていて、塾に関心がなくても面白いCMになっているので、ぜひ見てみてほしいです。
-->


---

<!-- Page 4 本題への区切り -->

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.1);" />
</div>

<div style="margin-left: 24rem; margin-top: 15rem">

# 本 題
</div>



<!--
スピーカーノート：
本題
-->


---
background: /background.png
---

<!-- Page 5 データベースとは -->

# データベースとは
## データを効率的に保存・検索・更新するためのシステム

##   **データベースの種類**
### 🍋 RDBMS → PostgreSQL, MySQL
### 🍋 NoSQL → MongoDB, Redis
### 🍋 グラフDB → Neo4j

## **RDBMS(Relational Database Management System)**
### 🍋 データをリレーショナルなテーブルで管理
### 🍋 SQLで操作


<!-- スピーカーノート：
今日のテーマはRDBMSで、聴衆レベルをビギナーに設定しているので、
データベースとは、の説明からさせてください。
データベースとは〜
データベースにもいろいろ種類があって、〜などがあります。

その中で今日取り上げるRDBMSは、〜という特徴があります。
-->

---
background: /background.png
---
<!-- Page 6 作ってみた -->

<CustomTwoCols :leftRatio="66" imageSrc="/simpledb.jpg" imageAlt="Database Design and Implementation book cover" imageClass="w-92% h-92% object-contain relative translate-x-2 translate-y-8">
  <template #left>


# 自作RDBMS:KeiPyDBの紹介
## [https://github.com/kei-kmj/KeiPyDB](https://github.com/kei-kmj/KeiPyDB)

<style>
.slidev-layout a {
  color: #3b82f6 !important;
}
</style>

## **「Database Design and Implementation: Second Edition 」** Edward Sciore (著)
## JavaでRDBMSを実装していく教科書っぽい洋書

<div style="margin-left: 15rem; font-size: 1.2rem;">⬇︎</div>

<div style="margin-left: 10rem; font-size: 1.5rem; font-weight: bold;">
Pythonで実装
</div>
  </template>
</CustomTwoCols>

<!-- スピーカーノート：
今日使う、Python製RDBMSですが、これは自作しました。
Database Design and Implementation という一般にSimpleDB本と呼ばれる書籍を参考にしてます。
JavaでRDBMSを実装していく内容ですが、書籍を参考にPythonで実装しました。
-->

---
background: /background.png
---

<!-- Page 7 KeiPyDBの機能 -->

# KeiPyDBの機能

<style scoped>
.feature-list li {
  font-size: 1.5rem !important;
  line-height: 1.6 !important;
}
.feature-list h2 {
  font-size: 1.8rem !important;
}
</style>

<div class="grid grid-cols-2 gap-8 feature-list">
<div class="ml-20">

## SQL
### 🍋 CREATE TABLE 
### 🍋 INSERT
### 🍋 SELECT
### 🍋 UPDATE 
### 🍋 DELETE
### 🍋 WHERE
### 🍋 CROSS JOIN

</div>
<div>

## 機能
### 🍋 トランザクション
### 🍋 ハッシュインデックス
### 🍋 B-treeインデックス

</div>
</div>



<!-- スピーカーノート
このRDBMSを使って話すことは、

-->


---
background: /background.png
---

<!-- Page 8.5 話すこと -->

# 話すこと
 
<br>

## 🍋 RDBMSがSQLをどのように処理するか
<br>

<style>
.slidev-code {
  font-size: 1.2rem !important;
  margin-top: -24px !important;
}
</style>

## 使用するSQL文
<br>

```sql
SELECT id, name FROM users WHERE name = 'Alice'   # id = 258, name = 'Alice'
``` 


<br>
<br>
<br>

### ※ なぜidが258なのかは、あとで説明します


<!-- スピーカーノート：
idは今は気にしなくてOK
-->
---
background: /background.png
---


<!-- Page 8 話さないこと -->


# 話さないこと
<br>

## ❌ 特定のデータベース製品の性質や使い方
## ❌ 難しいSQL文の書き方
## ❌ インデックス戦略
## ❌ パフォーマンスチューニング
## ❌ テーブル設計や正規化


<!-- スピーカーノート：
RDBMSのしくみを見ていくことで、DB君は裏側でこんな感じで頑張っているんだな、
とイメージが湧いて、トラブルシューティングの時などに、仕組みがこうだから、ここを疑ってみよう、
みたいな感じで役に立つといいかなと思います。
-->

---
background: /background.png
---

<!-- Page 9 SQLの性質 -->


# SQLは宣言型言語
<br>

<style>
.slidev-code {
  font-size: 1.5em !important;
}
</style>

```sql

SELECT id, name FROM users WHERE name = 'Alice'
```
<br>
        
## 何を取得したいかを伝えるだけで、
## どうやって取得するかはRDBMSが決める
<br>


<!-- スピーカーノート：
さて、RDBMSの特徴の一つはSQLを使うことです。
RDBMSは、宣言型のSQLを、命令型の処理に変換して実行するわけですが、
どうやっているのか。アーキテクチャを見ていきます。
-->

---
background: /background.png
---

<!-- Page 10 アーキテクチャ -->

# RDBMSのアーキテクチャ
<img src="/architecture.png" style="width: 73%; height: 86%; margin-left: 160px; margin-top: -22px">


<!-- スピーカーノート：
クライアントからSQLがくると、まずParserがSQLを解析します。
Parserはさらに、LexerとParserに分かれています。
Lexerが文字列を単語に分解して、Parserが単語から意味を理解します。
Plannerが実行計画を立てて
Executorが実行します。
もう少し低レイヤーなところで、
Buffer Managerがメモリを管理して、
File Manager:がディスクの読み書きをする
-->
---
background: /background.png
---
<!-- Page 11 字句解析 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 100%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Lexer (字句解析)
## 文字列をトークン（意味のある最小単位）に分解する
<br>

<style>
.slidev-code {
  font-size: 1.2em !important;
}
</style>
```sql
SELECT id, name FROM users WHERE name = 'Alice'
```
<br>

<div style="text-align: center; font-size: 1.2em;">⬇︎</div>

<br>

<div style="text-align: center; font-size: 1.0em; margin-left: -8rem; margin-right: -8rem;">

### `SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`   
</div>


</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
一つ一つ見ていくと、まずLexerで、〜

-->
---
background: /background.png
---
<!-- Page 12 字句解析（分類） -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 100%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Lexer (字句解析)
## 分解したトークンの種類を判定して分類

<br>

<div class="compact-table">

| トークン | 種類（Lexerが判定） |
|---------|--------------|
| `SELECT`, `FROM`, `WHERE` | キーワード（予約語）   |
| `id`, `name`, `users` | 識別子          |
| `,` | デリミタ = 区切り文字 |
| `=` | 演算子          |
| `'Alice'` | 文字列リテラル      |

</div>

<style>
.compact-table {
  font-size: 1.5rem !important;
}
.compact-table table {
  line-height: 1.0 !important;
  border: 1px solid #e2e8f0 !important;
  border-collapse: collapse !important;
}
.compact-table td, .compact-table th {
  padding: 0.3rem 0.5rem !important;
  border: 1px solid #e2e8f0 !important;
}
</style>

</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
トークンの種類を
〜〜のように判定して分類します。

-->


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/lexer/select.png" alt="Parser diagram" style="width: auto; height: auto; margin-top: 24px;">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/lexer/keyword.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px;">
</div>
---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/lexer/tokenize.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px;">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/lexer/match_keyword.png" alt="Parser diagram" style="width: auto; height: auto; margin-top: 24px; ">
<img src="/lexer/eat_keyword.png" alt="Parser diagram" style="width: auto; height: auto; margin-top: 24px; ">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/lexer/match_id.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
<img src="/lexer/eat_id.png" alt="Parser diagram" style="width: auto; height: auto; margin-top: 20px; ">
</div>

---
background: /background.png
---

<!-- Page 16 構文解析-->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 100%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Parser (構文解析)
## トークン列をルールに従って構造化

<div style="text-align: center; font-size: 1.0em; margin-left: -8rem; margin-right: -8rem;">

### `SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`   
</div>

<div style="text-align: center; font-size: 1.2em;">⬇︎</div>


## **AST（抽象構文木: Abstract Syntax Tree）**

## SQL文をコンピュタが理解しやすい木構造に変換したもの

<style>
.slidev-code {
  font-size: 1.5rem !important;
}
</style>

```sql
  QueryData
  ├─ SELECT: [id, name]
  ├─ FROM: users
  └─ WHERE: (name = 'Alice')

```



</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
構文解析では、トークンをルールに従って構造化して、抽象構文木（AST）を作成します。
SQLの各部分が木構造のノードとして表現されます。
-->

---
background: /background.png
---

<!-- Page 13 Parser - 複雑な条件 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 100%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Parser - 複雑な条件

<style>
.slidev-code {
  font-size: 1.2rem !important;
}
</style>
```sql
WHERE price < 1000 
    AND (sweets = '牡蠣せんべい' OR sweets = 'もみじ饅頭')
```
<div style="text-align: center; font-size: 1.6em;">⬇︎</div>

```
condition → AND ─┬─ (price < 1000)
                 │
                 └─ OR ─┬─ (sweets = '牡蠣せんべい')
                        │
                        └─  (sweets = 'もみじ饅頭')
          
```

<br>


</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
今回のSQLでは単純すぎて、木構造があまり伝わらないと思いますが、
複雑な条件式になると、木構造がわかりやすいかなと思います。
-->

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/query.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/parser.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/select_list.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/table_list.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/return_table.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/predicate.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>
---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/term.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/return_predicate.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/parser/query_data.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/plan/query_data.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<!-- Page 14 実行計画 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/planner.png" alt="Parser diagram" style="width: auto; height: 92%; margin-top: 22px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Planner (実行計画)

## ASTを受け取って、実行方法を選択
<br>

<style>
.slidev-code {
  font-size: 1.5rem !important;
}
</style>

```python
ProjectPlan(
    fields=['id', 'name'],
    SelectPlan(
        predicate="name='Alice'",
        TablePlan('users')
    )
)
```


</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
ASTを受け取って、どうやってレコードを取得するかの実行計画を立てます。

SQLのパフォーマンスが出ない時に、先輩などに「実行計画見てみて」と言われることがあると思いますが、
それがこのQuery Plannerの部分です。

本格的なRDBMSは統計情報を使って最適な実行計画を選んだり、
インデックスを使ったりします。
-->

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/plan/create_plan.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/plan/table_plan.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/plan/select_plan.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/plan/project_plan.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>

---
background: /background.png
---

<div style="margin-left: -50px; margin-right: -50px;">
<img src="/plan/plan.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>


---
background: /background.png
---

<!-- Page 15 実行エンジン -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/executor.png" alt="Parser diagram" style="width: auto; height: 91%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Executor (実行エンジン)

<style>
.slidev-code {
  font-size: 1.4rem !important;
}
</style>

## 1️⃣ Plan（実行計画）を受け取る

## 2️⃣ Scan（実行オブジェクト）を作って、
```python
TableScan('users')        # テーブルから1行ずつ読む
SelectScan("name='Alice'") # 条件に合うか確認
ProjectScan(['id','name']) # 必要なカラムだけ取り出す
```

## 3️⃣ レコードを返す
## 🍋 実行エンジンのしくみを理解するには

<div style="margin-left: 30px;">

## ストレージ層の理解が必要

</div>


</div>
</template>
</CustomTwoCols>


<!-- スピーカーノート：
それぞれのスキャンオブジェクトが
協働して、1レコードずつ返します。

-->

---
background: /background.png
---


<!-- Page 16 ストレージ層の概要 -->
<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/buffer_file.png" alt="Parser diagram" style="width: auto; height: 94%; margin-top: 18px; margin-left: -10px;">
</template>
<template v-slot:right>

# ストレージ層の概要

## **担当コンポーネント**
## 🍋 Buffer ManagerとFile Manager
## **役割**
## 🍋 RDBMS自身でメモリ管理(OSにまかせない)
## 🍋 データの永続化

## **解決したい課題**
## 🍋 ディスクアクセスはメモリアクセスに比べて非常に遅い
## 🍋 大量のデータを扱いたい ↔️ でも高速に処理したい




</template>
</CustomTwoCols>

---
background: /background.png
---


<!-- Page 17 用語 -->

<CustomTwoCols :leftRatio="80">
<template v-slot:left>
<img src="/disk.png" style="width: auto; height: 90%; margin-top: 30px; margin-left: -30px;">
</template>
<template v-slot:right>
<div style="margin-left: -2rem;">

# 用語

<br>

### 🍋 ファイル : 
## OSのファイルシステムで内部的に定義される、ブロックの論理的な集まり
### 🍋 ブロック : 
## ディスクを固定長に区切った領域

</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
ファイル、ブロックとは何かを整理しておきます。

-->

---
background: /background.png
---

<!-- Page 18 バッファマネジャ-->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/buffer.png" alt="Parser diagram" style="width: auto; height: 100%; margin-top: 16px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Buffer Manager
<br>

## OSにまかせず、RDBMS側でメモリ管理する

## 🍋 ブロックをメモリに読み込む
## 🍋 頻繁にアクセスされるブロックをメモリに保持
## 🍋 使用頻度が低いブロックをメモリから追い出す



</div>
</template>
</CustomTwoCols>

---
background: /background.png
---



<!-- Page 19 ファイルマネジャー -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/file_manager.png" alt="Parser diagram" style="width: auto; height: 93%; margin-top: 21px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# File Manager
<br>

## データを永続化するため、
## 🍋 OSのファイルシステムとのやりとり
## 🍋 ブロックへのアクセスを提供
## 🍋 ディスク上のデータをブロックを指定して読み書き

</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
とは言っても、ディスクにどのように書き込むのか、という話が出てきます。
-->

---

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.1);" />
</div>

<div style="font-size: 12rem; text-align: center; margin-top: 200px; margin-left: 400px;">
🍹
</div>
<!--
スピーカーノート：
-->



---
background: /background.png
---

<!-- Page 20 レコードを探すしくみ -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/executor.png" alt="Parser diagram" style="width: auto; height: 92%; margin-top: 22px; margin-left: -10px;">
</template>
<template v-slot:right>

# name = 'Alice' のレコードを探すしくみ

## 🍋 usersテーブルのブロックを

<div style="margin-left: 30px;">

## （トランザクションを介して）1つずつ読む
</div>

## 🍋 ブロックの中は
<div style="margin-left: 30px;">

## スロットという単位でレコードが保存されている
</div>

<div style="margin-left: 10rem; font-size: 1.2rem;">⬇︎</div>

## 🍋 スロットの単位で探す

</template>
</CustomTwoCols>

<!-- スピーカーノート：
ファイル、ディスク、ブロックが何かを整理できたところで、実行エンジンの話ができます。

-->

---
background: /background.png
---


<!-- Page 21 スロットとは何か -->


<CustomTwoCols :leftRatio="50">
<template v-slot:left>
<div>

# スロットとは何か

## 🍋 テーブル情報から定義される

<div style="margin-left: 30px;">

## 固定長の領域
</div>
<br>

<div class="large-sql">

```sql
CREATE TABLE users (id int, name varchar(10))
```

</div>

<style scoped>
.large-sql pre code {
  font-size: 1.2rem !important;
}
</style>

<br>
<br>

## スロットの最初の領域は状態フラグ
## 01:使用中、00:空き

</div>
</template>
<template v-slot:right>
<br>


<div style="text-align: center;">

<br>

</div>
<img src="/slot5.png" alt="Slot layout diagram" style="width: auto; height: 90%; margin-left: 0rem;">
</template>
</CustomTwoCols>

<!-- スピーカーノート：
スロットとは何か。〜〜
idはint型なので、今回は4バイト分確保しています。nameはvarchar(10)なので、10バイト分確保しています。
文字列は文字サイズ情報も欲しいので、それ用に4バイト分確保しています。
先頭に状態フラグがあって、01が使用中、00が空きです。

-->

---
background: /background.png
---

<!-- Page 22 Appendix -->

# レコードの読み取り
## 🍋 スロットのレイアウトがわかれば、レコードにアクセスできる
## 🍋 スロット毎に、13バイト目から10バイト分を見て、
## 🍋 nameがAliceかどうかを確認
## 🍋 レコードを取得して指定されたカラムを出力する { id: 258, name: 'Alice' }

<img src="/slot7.png" alt="Slot layout diagram" style="width: auto; height: 35%; margin-left: 18rem; margin-top: 40px;">

<!-- スピーカーノート：
-->



---
background: /background.png
---


<!-- Page 23 データのインサート -->

<CustomTwoCols :leftRatio="50">
<template v-slot:left>


# レコードの追加(INSERT)


<div class="large-sql">

```sql
INSERT INTO users (id, name) VALUES (259, 'Bob')
```

</div>

<style scoped>
.large-sql pre code {
  font-size: 1.5rem !important;
}
</style>


## 🍋 状態フラグが00のスロットを探す
## 🍋 トランザクションを介して
## 🍋 Write-Ahead Logging/
<div style="margin-left: 30px;">

## ログ先行書き込みで障害対策をして
</div>

## 🍋 空きスロットに書き込む

</template>
<template v-slot:right>


<img src="/slot_adding.png" alt="Parser diagram" style="width: auto; height: 45%; margin-top: 228px; margin-left: -30px;">
</template>
</CustomTwoCols>

---
background: /background.png
---

<!-- Page 24 削除 -->

<CustomTwoCols :leftRatio="50">
<template v-slot:left>


# レコードの削除(DELETE)

<div class="large-sql">

```sql
DELETE FROM users WHERE id = 259
```

</div>

<style scoped>
.large-sql pre code {
  font-size: 1.5rem !important;
}
</style>

## 🍋 レコードはすぐには削除しない
## 🍋 (トランザクションを介して)

<div style="margin-left: 30px; margin-top: -20px;">

## スロットの状態フラグを00に更新
</div>

## 🍋 データはそのまま残る
## 🍋 後で新しいレコードを追加する時に

<div style="margin-left: 30px; margin-top: -20px;">

## 空きスロットとして再利用される
</div>

</template>
<template v-slot:right>
<div>

<img src="/slot_delete.png" alt="Transaction diagram" style="width: auto; height: 87%; margin-top: 300px;">
</div></template>
</CustomTwoCols>

<!-- スピーカーノート：
-->

---
background: /background.png
---
<!-- Page 25 ヘックスビュワー -->

# 動画

---
background: /background.png
---
<!-- Page 26 スクショで確認 -->

# ヘックスビュアーで確認
<br>

<img src="/hex.png" style="width: auto; height: 48%;  margin-top: -3rem; margin-left: -2rem; margin-right: -6rem;" />

<img src="/slot_delete.png" style="width: 61%; height: auto; margin-left: 17px;" />

<!-- スピーカーノート：
拡大したスクショで確認してみましょう。


あれ？int型のデータがおかしくないですか？
-->

---
background: /background.png
---

<!-- Page 27 エンディアン -->

# int型の並び順が逆になってる

<div style="width: 40%; margin: 0;">
<TransparentTable :items="[
  { label: '10進数', value: '16進数' },
  { label: '258', value: '0x0102' },
  { label: '259', value: '0x0103' }
]" :showOuterBorder="true" :showRowLines="true" />
</div>
<br>

<img src="/hex.png" style="width: auto; height: 38%;" />


<!-- スピーカーノート：

-->


---
background: /background.png
---

<!-- Page 28 エンディアン1 -->


# エンディアン

## バイト列の並び順の違い

## **リトルエンディアン（Intel, AMD, Apple Silicon）**
### 🍋 数値の最下位バイトがアドレスの低い方 → 258 (0x0102) は `02 01` 

## **ビッグエンディアン（ネットワーク標準）**
### 🍋 数値の最上位バイトがアドレスの低い方 → 258 (0x0102) は `01 02` 

## **なぜ重要？**
### 🍋異なるシステム間でバイナリデータをやり取りする時
### 🍋ネットワーク通信（ビッグエンディアン）


<!--　スピーカーノート：
リトルエンディアンとビッグエンディアンは、必ずしもどちらが優れている、というわけではなく、
歴史的経緯などもあって、2種類の方式が存在しています。
なので、、異なるシステム間でバイナリデータをやり取りする時やネットワーク通信の実装では、エンディアンに注意する必要があります。
-->
---
background: /background.png
---
<!-- Page 29 エンディアン2 -->

# Pythonのstructモジュール

<style>
.slidev-code {
  font-size: 1.8rem !important;
}
</style>

```python
import struct
# 16進数で0x0102をバイト列に変換
data = struct.pack('<i', 258)  # リトルエンディアン
```
<br>

<div style="width: 60%; margin: 0;">
<TransparentTable :items="[
  { label: '<', value: 'リトルエンディアン' },
  { label: '>', value: 'ビッグエンディアン' },
  { label: '!', value: 'ネットワークバイトオーダー' }
]" :showOuterBorder="true" :showRowLines="true" />
</div>

<!-- スピーカーノート：
Pythonでは、structモジュールを使うと、エンディアンを指定してバイト列に変換できます。
ネットワークバイトオーダーは実質ビッグエンディアンと同じです。
iはint型のiです
-->

---
background: /background.png
---

<!-- Page 30 まとめ -->

# まとめ

<div class="summary-content">
<CustomTwoCols :leftRatio="50">
<template v-slot:left>

1. **Lexer** - 字句解析でトークンに分解
2. **Parser** - 構文解析でASTを構築  
3. **Planner** - 実行計画を作成
### 🍋 TablePlan / SelectPlan / ProjectPlan
4. **Executor** - 実行エンジン
### 🍋 ProjectScan: カラム抽出
### 🍋 SelectScan: WHERE条件フィルタ
### 🍋 TableScan: ファイルアクセス

</template>
<template v-slot:right>
<div style="padding-left: 4rem;">

5. **Transaction**
### 🍋  ロック制御、ロールバック
6. **Buffer Manager**
### 🍋 メモリキャッシュ管理
### 🍋 ディスクI/O最小化
   7. **File Manager**
### 🍋 物理的なディスク読み書き
### 🍋 ブロック単位のデータ管理

</div>
</template>
</CustomTwoCols>
</div>

<style>
.summary-content h2 {
  font-size: 1.8rem !important;
  margin: 0.2rem 0 0.5rem 0 !important;
}
.summary-content li {
  font-size: 1.7rem !important;
  margin: 0.1rem 0 !important;
}
.summary-content ul {
  margin: 0.1rem 0 !important;
}
</style>

<!-- スピーカーノート：
これで、SQLの1行の裏側で、たくさんの仕組みが動いていることがわかってもらえたと思います。
-->

---

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.1);" />
</div>

<div style="font-size: 12rem; text-align: center; margin-top: 200px; margin-left: 400px;">
☕️
</div>
<!--
スピーカーノート：
-->



---
background: /background.png
---
<!-- Page 31 we are hiring -->

# 株式会社DeltaXでは、Webエンジニアを募集中です！
<br>
<br>

### 🍋 言語：Python／TypeScript
### 🍋 フレームワーク：FastAPI／Astro／React／Remix
### 🍋 インフラ：AWS／OpenSearch／PostgreSQL／DynamoDB他

<br>

### 🍋 フルリモート
### 🍋 生成AIを積極的に活用してます

---
background: /background.png
---
<!-- Page 32 挨拶 -->

# 最後に

## インデックス、ログ、トランザクション ...まだまだ話したいことが...
<br>

## KeiPyDBのソースコードは、GitHubに公開済みです
## <a href="https://github.com/kei-kmj/KeiPyDB" style="color: blue;">https://github.com/kei-kmj/KeiPyDB</a>

<br>

## **次にやりたいこと**
## 🍋ブラウザを自作して、KeiPyDBを組み込みたい‼️

<div style="margin-left: 180px;">

# ご清聴ありがとうございました
</div>

<img src="/thankyou.png" style="position: absolute; bottom: 30px; right: 0px; width: 240px; height: auto;" />


---