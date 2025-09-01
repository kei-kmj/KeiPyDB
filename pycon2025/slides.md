

<style>
/* グローバルフォントサイズの統一設定 */
.slidev-layout {
  font-size: 1.1rem !important;
}
.slidev-layout h1 {
  font-size: 2.0em !important;
  line-height: 1.2 !important;
}
.slidev-layout h2 {
  font-size: 1.4em !important;
  line-height: 1.25 !important;
}
.slidev-layout h3 {
  font-size: 1.2em !important;
  line-height: 1.1 !important;
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
</style>

<div class="absolute inset-0">
  <img src="/background.png" class="w-full h-full object-cover" />
</div>
<!-- タイトル -->

<br>
<br>

# Python製RDBMSで理解する、データベースのピース

<br>

## 〜 コードのステップ実行とヘックスビュアーで内部動作を追ってみよう 〜

<br>
<br>

PyCon JP 2025
<br>
k-kamijo

---

<!-- Page 1 自己紹介-->

<CustomTwoCols :leftRatio="60">
<template v-slot:left>
<br>
<br>
<br>

<div style="text-align: center;">

# 自己紹介

</div>
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
塾選のバックエンドはPython FastAPIでできています。
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
手前味噌ですが、このCMはYou Tubeで公開されていて、塾に関心がなくても面白いCMになっているので、ぜひ見てみてください。
-->

---
background: /background.png
---

<!-- Page 8 データベースとは -->
<br>
<br>

# データベースとは
## データを効率的に保存・検索・更新するためのシステム
<br>

##   **データベースの種類**
- RDBMS → PostgreSQL, MySQL
- NoSQL → MongoDB, Redis
- グラフDB → Neo4j

<br>

## **RDBMS(Relational Database Management System)**

- データをテーブルで管理
- SQLで操作
- ACID特性を保証（原子性・一貫性・隔離性・永続性）


<!-- スピーカーノート：
ビギナー向けの発表なので、基本的なところから始めます。

-->

---
background: /background.png
---
<!-- Page 4 作ってみた -->

<CustomTwoCols :leftRatio="66" imageSrc="/simpledb.jpg" imageAlt="Database Design and Implementation book cover" imageClass="w-90% h-90% object-contain relative translate-x-2 translate-y-8">
  <template #left>

<br>
<br>

# 自作RDBMS:KeiPyDBの紹介
<br>

## Pythonの言語仕様とDBの内部構造を学びたくて作ってみました。
<br>

## [https://github.com/kei-kmj/keiPyDB](https://github.com/kei-kmj/keiPyDB)

<style>
.slidev-layout a {
  color: #3b82f6 !important;
}
</style>

<br>

## 参考にした書籍：
## **「Database Design and Implementation: Second Edition 」** Edward Sciore (著)
<br>

## JavaでRDBMSを実装していく教科書っぽい洋書

  </template>
</CustomTwoCols>

<!-- スピーカーノート：
仕組みを見ていくための、Python製RDBMSですが、これは自作しました。
Database Design and Implementation という一般にSimpleDB本と呼ばれる書籍を参考にしてます。
JavaでRDBMSを実装していく内容ですが、書籍を参考にPythonで実装しました。
-->

---
background: /background.png
---

<!-- Page 5 KeiPyDBの機能 -->
<br>
<br>

# KeiPyDBの機能

<div class="grid grid-cols-2 gap-8">
<div class="ml-20">

## SQL
- CREATE TABLE 
- INSERT
- SELECT
- UPDATE 
- DELETE
- WHERE
- CROSS JOIN

</div>
<div>

## その他
- トランザクション
- ハッシュインデックス
- Btreeインデックス

</div>
</div>



<!-- Page 4 本題 -->

<br>
<br>

---
background: /background.png
---
<br>
<br>


# 話すこと
 
<br>

## 🐰SELECT文で欲しいレコードを取得するしくみ
<br>

<style>
.slidev-code {
  font-size: 1.2rem !important;
  margin-top: -24px !important;
}
</style>

```sql
SELECT id, name FROM users WHERE name = 'Alice'   # id = 258, name = 'Alice'
``` 
<br>

## 🐰INSERT文でレコードをディスクに書き込むしくみ
<br>

```sql
INSERT INTO users (id, name) VALUES (259, 'Bob')
```
<br>
<br>
<br>
<br>


## ※ なぜidが258と259なのかは、あとで説明します


---
background: /background.png
---


<!-- Page 5 本題 -->

<br>
<br>

# 話さないこと
<br>

## ❌ 特定のデータベース製品の性質や使い方
<br>

## ❌ 難しいSQL文の書き方
<br>

## ❌ インデックス戦略やパフォーマンスチューニングについて
<br>

## ❌ テーブル設計や正規化の話


<!-- スピーカーノート：
RDBMSのしくみを見ていくことで、DB君は裏側でこんな感じで頑張っているんだな、
と愛着を持ってもらえたらいいかな、と思っています。
-->

---
background: /background.png
---

<!-- Page 9 SQLの性質 -->

<br>
<br>

# SQLは宣言型言語
<style>
.slidev-code {
  font-size: 1.5em !important;
}
</style>
<br>
<br>

```sql

SELECT id, name FROM users WHERE name = 'Alice'
```
<br>
<br>
<br>
        
## 何を取得したいかを指定する。どうやって取得するかはRDBMSが決める
<br>


<!-- スピーカーノート：
RDBMSは、宣言型のSQLを、命令型の処理に変換して実行するわけですが、
どうやっているのか。アーキテクチャを見ていきます。
-->

---
background: /background.png
---

<!-- Page 10 アーキテクチャ -->
<br>
<br>

# RDBMSのアーキテクチャ
<img src="/architecture.png" style="width: 76%; height: 84%; margin-left: 160px; margin-top: -22px">


<!-- スピーカーノート：
# RDBMSのアーキテクチャ

## SQL Query   
## ↓   
## Parser   
##  ├─ Lexer (字句解析): 文字列を単語に分解   
##  └─ Parser (構文解析): 単語から意味を理解   
## ↓   
## Query Planner: 実行計画を立てる    
## ↓   
## Query Executor: 実行する   
## ↓   
## Buffer Manager: メモリを管理する   
## ↓   
## File Manager: ディスクを読み書きする   
## ↓   
## Disk
-->
---
background: /background.png
---
<!-- Page 11 字句解析 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 80%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Lexer (字句解析)
## 文字列をトークン（意味のある最小単位）に分解する
<style>
.slidev-code {
  font-size: 1.2em !important;
}
</style>
```sql
SELECT id, name FROM users WHERE name = 'Alice'
```

<div style="text-align: center; font-size: 1.2em;">⬇︎</div>

### `SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`   

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

---
background: /background.png
---

<!-- Page 12 構文解析-->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 80%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Parser (構文解析)
## トークン列をルールに従って構造化
<br>

### `SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`

<div style="text-align: center; font-size: 1.2em;">⬇︎</div>


## **AST（抽象構文木: Abstract Syntax Tree）**
<br>

## SQL文の構造を木構造にする

<style>
.slidev-code {
  font-size: 1.2rem !important;
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
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 80%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Parser - 複雑な条件

<style>
.slidev-code {
  font-size: 1.1rem !important;
}
</style>
```sql
WHERE age >= 20 AND (city = 'Hiroshima' OR city = 'Kure')
```
<div style="text-align: center; font-size: 1.2em;">⬇︎</div>
```
condition → AND ─┬─ (age >= 20)
                 │
                 └─ OR ─┬─ (city = 'Hiroshima')
                        │
                        └─ (city = 'Kure')
```

<br>


</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：

-->
---
background: /background.png
---

<!-- Page 14 実行計画 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/planner.png" alt="Parser diagram" style="width: auto; height: 80%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Query Planner (実行計画)

## ASTを受け取って、実行方法を選択
<br>

<style>
.slidev-code {
  font-size: 1.2rem !important;
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
今回は単純なフルスキャンをしています。
KeiPyDBにもインデックス機能はありますが、今日は話をそこまで広げられないので、省略します。
-->
---
background: /background.png
---

<!-- Page 14 実行エンジン -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/executor.png" alt="Parser diagram" style="width: auto; height: 80%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Query Executor (実行エンジン)

<style>
.slidev-code {
  font-size: 1.0rem !important;
}
</style>

## 1️⃣ Plan（実行計画）を受け取る
<br>

## 2️⃣ Scan（実行オブジェクト）を作って、
```python
TableScan('users')        # テーブルから1行読む
SelectScan("name='Alice'") # 条件に合うか確認
ProjectScan(['id','name']) # 必要な列だけ取り出す
```
<br>

## 3️⃣ レコードを1行ずつ処理して、結果を返す

<br>

### {id: 258, name: 'Alice'} 

</div>
</template>
</CustomTwoCols>

---
background: /background.png
---

<!-- Page 15 デモ -->
<br>
<br>

# デモ: SELECT文の実行

<!-- スピーカーノート：


-->
---
background: /background.png
---

<!-- Page 15 デモ -->
<br>
<br>

# SELECT文の処理のまとめ
## 1️⃣ SQL文をトークンに分解（Lexer）
## 2️⃣ トークンからASTを作る（Parser）
## 3️⃣ ASTから実行計画を立てる（Planner）
## 4️⃣ テーブルを1行ずつ読んで条件チェック（Executor）
## 5️⃣ 必要なカラムだけ取り出して結果を返す
<br>
✅ Aliceのレコードを取得できました！
<br>
<br>
🤔 でも、ちょっと待って...
そもそもAliceのデータはどこから来たの？

<!-- スピーカーノート：
→ データが永続化されていないと、取り出せません。

-->

---
background: /background.png
---

<!-- Page 16 ファイルI/O -->

<br>
<br>

# データの永続化
<br>
<br>

<style>
.slidev-code {
  font-size: 1.5em !important;
}
</style>

```sql 
INSERT INTO users (id, name) VALUES (259, 'Bob');
```


<br>

<!-- スピーカーノート：
INSERT 文で、データをディスクに書き込むところを見ていきます。
-->

---
background: /background.png
---

<!-- Page 17 ディスク書き込みの手順 -->
<br>
<br>


# ディスクに書き込もう！
## でも、、、あれ？🤔
<br>


## ・どこに書き込むか？
<br>

## ・いつ書き込むか？
<br>


## ・他の人も同時に書き込んでいるかも？
<br>

## ・途中で電源が落ちてしまったら？

---
background: /background.png
---

<!-- Page 18 毎回ディスクに書く -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/buffer.png" alt="Parser diagram" style="width: auto; height: 80%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Buffer Manager (バッファマネージャー)
<br>

## ディスクアクセスは、メモリアクセスに比べて遅い。
## DBは大量のデータを扱いたい。でも高速に処理したい
<br>
<div style="text-align: center; font-size: 1.2em;">⬇︎</div>

## OSにまかせず、RDBMS側でメモリ管理する
<br>

## 編集は、メモリ上のバッファで行う
## 都度書き込まず、最後にまとめてディスクに書き込む


</div>
</template>
</CustomTwoCols>

---
background: /background.png
---
<!-- Page 19 ファイルマネジャー -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/file_manager.png" alt="Parser diagram" style="width: auto; height: 80%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# File Manager (ファイルマネージャー)

## OSのファイルシステムとやりとり
<br>

## ファイル情報の取得
<br>

## ブロック単位での読み書き
<br>

## ブロックの追加
<br>

</div>
</template>
</CustomTwoCols>

---
background: /background.png
---

<!-- Page 19 ブロック管理 -->

<CustomTwoCols :leftRatio="35">
<template v-slot:left>
<img src="/block.png" alt="Block diagram" style="width: auto; height: 89%; margin-top: 15px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# どこに書き込むか？

- ディスク上のデータは、ブロックという単位で管理
- ブロックは、ディスクを固定長に区切った領域
- 読み書きはブロック単位で行う

<br>

<style>
.slidev-code {
  font-size: 1.0em !important;
}
</style>

```sql 
INSERT INTO users (id, name) VALUES (259, 'Bob');
```
<br>

## Bobを追加すると...
Block 0の空きスペースに `id=259, Bob` が入る

</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
ディスク上のデータは、ブロックという単位で管理します。
ブロックは、一定のサイズ（例えば256バイト）で区切られたデータの単位です。

ブロック0には、Aliceのレコードがあり、
今からBobのレコードも同じBlock 0に書き込まれます。
今回は1ブロック256バイトとしていますが、実際のRDBMSではもっと大きくて、
4KiBや8KiBなどのサイズが一般的です。
これは、OSやファイルシステムのブロックサイズに合わせることで、
I/O効率を最適化するためです。
-->



---
background: /background.png
---

<!-- Page 20 トランザクション -->

<CustomTwoCols :leftRatio="35">
<template v-slot:left>
<img src="/transaction.png" alt="Transaction diagram" style="width: auto; height: 84%; margin-top: 14px;">
</template>
<template v-slot:right>
<div>
<br>
<br>


# 誰かが同時に書き込んでいるかも？

<br>

## ⚠️ 同時書き込み
ユーザーA：Block 0にBob追加  
ユーザーB：Block 0にCarol追加  
→ データが壊れる！😱

<br>

## **トランザクションで制御**
ユーザーA：Block 0をロック → 編集 → 解除  
ユーザーB：（待機） → 編集

</div>
</template>
</CustomTwoCols>


<!-- スピーカーノート：
複数のユーザーが同時にデータベースを使うとき、
トランザクションがロックをかけて、
順番に処理することで、データの整合性を保ちます。
-->
---
background: /background.png
---

<!-- Page 21 途中で電源が落ちてしまったら？ -->
<br>
<br>


# 途中で電源が落ちてしまったら？
<br>

## WAL（Write-Ahead Log）
**データより先にログを書き込む**

"Bobのレコード追加"という更新ログを先にディスクに書き込む   
変更されたバッファをディスクに書き込む(実際にBobのレコードが追加される)   
ログにcommitログが書き込まれる(追加完了)   
<div style="text-align: center; font-size: 1.2em;">⬇︎</div>
クラッシュした時に、ログがあるけどコミットされていなければ、ロールバックする   
コミットログがある場合は、ディスクへの保存が保証されている


<!-- スピーカーノート：
データベースの永続性を保証するために、途中で電源が落ちてしまった場合の対策が必要です。
そこで、WAL（Write-Ahead Log）という仕組みを使います。
WALでは、データの変更をディスクに書き込む前に、まずログに記録します。

-->
---
background: /background.png
---

<!-- Page 22 最終的にディスクへ -->

<CustomTwoCols :leftRatio="50">
<template v-slot:left>
<div>
<br>
<br>


# ディスクに書き込み

## ブロックをスロットに分割する
## スロットのサイズは
## テーブルのスキーマ情報から計算する
<br>

<div class="large-sql">

```sql
CREATE TABLE users (id int, name varchar(10))
```

</div>

<style scoped>
.large-sql pre code {
  font-size: 1.1rem !important;
}
</style>
<br>
<br>

## スロットの最初の領域は状態フラグ
## 01:使用中なので、次の空きスロットに書き込む

</div>
</template>
<template v-slot:right>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>


<div style="text-align: center;">

## スロット内のレコードレイアウト

</div>
<img src="/slot.png" alt="Slot layout diagram" style="width: auto; height: 35%;">
</template>
</CustomTwoCols>

<!-- スピーカーノート：
最終的なディスク書き込みの流れです。

重要なのは、WALログは2回書かれること：
1回目：データ変更時（set_string時）に操作ログ
2回目：コミット時にコミットログ

これで、障害が起きた時でも復旧可能になります。

バッファがクリーンな状態に戻され、
次のトランザクションで再利用可能になります。
-->
---
background: /background.png
---
<!-- Page 23 デモ -->
<br>
<br>

# デモ: INSERT文の実行


---
background: /background.png
---
<!-- Page 23 ヘックスビュワー -->
<br>
<br>

# デモ: ヘックスビュワーでの確認

---
background: /background.png
---
<!-- Page 23 スクショで確認 -->
<br>
<br>
 

<img src="/endian.png" style="width: auto; height: 45%;" />

<img src="/slot2.png" style="width: 70%; height: auto; margin-left: 40px;" />

<!-- スピーカーノート：

-->

---
background: /background.png
---

<!-- Page 24 ディスク書き込みのまとめ -->
<br>
<br>

# ディスク書き込みのまとめ
1. **メモリ上で編集**: データをバッファに書き込む
2. **WALログ記録**: 変更内容をログに記録
3. **COMMIT実行**: バッファの内容をディスクに書き込む
4. **コミットログ記録**: トランザクションの完了をログに記録
5. **バッファをクリーンに**: 次のトランザクションの準備

<!--スピーカーノート：

-->
---
background: /background.png
---

<!-- Page 25 エンディアン -->
<br>
<br>

# Int型の並び順が逆になってる

<div style="width: 40%; margin: 0;">
<TransparentTable :items="[
  { label: '10進数', value: '16進数' },
  { label: '258', value: '0x0102' },
  { label: '259', value: '0x0103' }
]" :showOuterBorder="true" :showRowLines="true" />
</div>
<br>

<img src="/endian.png" style="width: auto; height: 30%;" />


<!-- スピーカーノート：
最後に、少しマニアックになりますが、エンディアンの話をさせてください
エンディアンとは、バイトの並び順のことです。
例えば、258と259を使った理由は、エンディアンの違いを示すためです。
258は16進数で0x0102、259は0x0103ですが、
ディスクにはリトルエンディアンで書き込まれます。
つまり、258は02 01、259は03 01と書かれます。
これはPythonのstructモジュールを使って、意図的に逆に書き込んでいます。
-->


---
background: /background.png
---

<!-- Page 26 エンディアン1 -->
<br>
<br>


# エンディアン

## バイト列の並び順の違い
<br>

## **リトルエンディアン（Intel, AMD, Apple Silicon）**
### 数値の最下位バイトがバイト列の先頭 (アドレスの低い方) → 258 (0x0102) は `02 01` として保存
<br>

## **ビッグエンディアン（ネットワーク標準）**
### 数値の最上位バイトがバイト列の先頭 (アドレスの低い方) → 258 (0x0102) は `01 02` として保存
<br>

## なぜ重要？
<br>

### - 異なるシステム間でバイナリデータをやり取りする時
### - ネットワーク通信（ビッグエンディアン）
### - バイナリファイルをデバッグする時

---
background: /background.png
---
<!-- Page 26 エンディアン2 -->
<br>
<br>

# Pythonのstructモジュールを使う

<style>
.slidev-code {
  font-size: 1.2rem !important;
}
</style>

```python
import struct
# 例: 16進数で0x0102をバイト列に変換
data = struct.pack('<i', 258)  # リトルエンディアンで書き込む
```
<br>

<div style="width: 60%; margin: 0;">
<TransparentTable :items="[
  { label: '<i', value: 'リトルエンディアン' },
  { label: '>i', value: 'ビッグエンディアン' },
  { label: '!i', value: 'ネットワークバイトオーダー' }
]" :showOuterBorder="true" :showRowLines="true" />
</div>


---
background: /background.png
---

<!-- Page 26 INSERTのまとめ -->
<br>
<br>

# INSERTのまとめ
1. メモリ上で編集
2. Write Ahead Log ログ記録
3. COMMIT実行
4. コミットログ記録
5. エンディアンも気にしつつ、
6. 空きブロックの空きスロットにレコードを書き込む


---
background: /background.png
---

<!-- Page 26 まとめ -->
<br>
<br>

# まとめ

## SQLの1行の裏側で、たくさんの仕組みが動いてる！

<br>

### まだまだ話したいことが...
- トランザクションの詳細
- インデックスの仕組み

<br>

## 次は
#### ブラウザを自作して、KeiPyDBと繋げてみたい！

---
background: /background.png
---
<!-- Page 27 we are hiring -->
<br>
<br>

# 株式会社DeltaXでは、Webエンジニアを募集中です！

## 言語：Python／TypeScript
## フレームワーク：FastAPI／Astro／React／Remix
## インフラ環境：AWS／OpenSearch／PostgreSQL／DynamoDB／Docker／Google Cloud

## フルリモート
## 生成AIを積極的に活用してます

---
background: /background.png
---
<!-- Page 28 挨拶 -->
<br>
<br>
<br>
<br>
<br>

# ご清聴ありがとうございました！

<img src="/thankyou.png" style="position: absolute; bottom: 30px; right: 0px; width: 240px; height: auto;" />


---