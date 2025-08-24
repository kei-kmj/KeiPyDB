

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
  font-size: 1.2em !important;
  line-height: 1.25 !important;
}
.slidev-layout h3 {
  font-size: 1.0em !important;
  line-height: 1.1 !important;
}
.slidev-layout p {
  font-size: 1.1em !important;
  line-height: 1.5 !important;
}
.slidev-layout ul li, .slidev-layout ol li {
  font-size: 1.1em !important;
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
上條 恵子@k-kamijo

---
layout: two-cols
---

<div class="pl-8">
<!-- Page 1 自己紹介-->
<br>
<br>
<br>

<div style="text-align: center;">

# 自己紹介

</div>
<br>

<TransparentTable :items="[
  { label: '名　前：', value: '上條 恵子@ k-kamijo' },
  { label: 'Github：', value: '@kei-kmj' },
  { label: '所　属：', value: '株式会社DeltaX' },
  { label: '趣　味：', value: '輪行<br>(電車旅 & サイクリング)' }
]" />

</div>
::right::

<div class="flex justify-center items-center h-full">
  <img src="/tokageusagi.png" class="w-64 h-64 rounded-full object-cover" />
</div>
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

<img src="/bestjuku.png" style="position: absolute; top: 0; left: 0; right: 0; bottom: 30px; width: 100%; height: calc(100% - 30px); object-fit: contain;" />

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

<!-- Page 4 本題 -->

<br>
<br>

# 話すこと
 
## 🐰SELECT文から欲しいレコードを取得するしくみ
<br>

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


## 🐰 エンディアンの話
<br>

### ※ なぜidが258と259なのかは、エンディアンのところで説明します。
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

<!-- Page 4 作ってみた -->

<CustomTwoCols :leftRatio="66" imageSrc="/simpledb.jpg" imageAlt="Database Design and Implementation book cover" imageClass="w-full h-full object-contain relative translate-x-5 translate-y-5">
  <template #left>

<br>
<br>

# 自作RDBMS:KeiPyDBの紹介
<br>

## Pythonの言語仕様とDBの内部構造を同時に学びたくて作ってみました。
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

## JavaでRDBMSを実装していく教科書っぽい英書

  </template>
</CustomTwoCols>

<!-- スピーカーノート：
仕組みを見ていくための、Python製RDBMSですが、これは自作しました。
Database Design and Implementation という一般にSimpleDB本と呼ばれる書籍を参考にしてます。
JavaでRDBMSを実装していく内容ですが、書籍を参考にPythonで実装しました。
-->
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

---
background: /background.png
---

<!-- Page 8 データベースとは -->
<br>
<br>

# データベースとは
## データベースとは、データを効率的に保存・検索・更新するためのシステム
<br>

##  データベースの種類
- RDBMS → PostgreSQL, MySQL
- NoSQL → MongoDB, Redis
- グラフDB → Neo4j

<br>

## RDBMS(Relational Database Management System)

- データをテーブルで管理
- SQLで操作
- ACID特性を保証（原子性・一貫性・隔離性・永続性）


<!-- スピーカーノート：
ビギナー向けの発表なので、基本的なところから始めます。

-->

---
background: /background.png
---

<!-- Page 9 SQLの性質 -->

<br>
<br>

# SQLは宣言型言語
```sql

SELECT id, name FROM users WHERE name = 'Alice'
```
        
## 何を取得したいかを指定するだけで、どうやって取得するかはRDBMSが決める
<br>

## これをPythonで命令型で書くと、
```python
# ファイルを開いて
with open('users.tbl', 'rb') as f:
    # 全レコードを読んで
    for record in read_records(f):
            # 条件に合うレコードを見つけて
            if record.name == 'Alice':
                # 見つかったら返す
                return record.id, record.name
```

## RDBMSは、宣言型のSQLを、命令型の処理に変換して実行する
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
<img src="/architecture.png" style="width: auto; height: 78%; margin-left: 20px;">


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
<img src="/Parser.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 18px; margin-left: -20px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Lexer (字句解析)
## 文字列をトークン（意味のある最小単位）に分解する
```sql
SELECT id, name FROM users WHERE name = 'Alice'
```
    ↓

`SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`   

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
<img src="/Parser.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 18px; margin-left: -20px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Parser (構文解析)
## トークン列をルールに従って構造化

`SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`

↓
- AST（抽象構文木）
```
  QueryData
  ├─ SELECT: [id, name]
  ├─ FROM: users
  └─ WHERE: (name = 'Alice')

```

## SQLの構造を木構造で表現
## SELECT句、FROM句、WHERE句がそれぞれノードに
## 条件や値が子ノードとして配置される


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
<img src="/Parser.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 18px; margin-left: -20px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Parser - 複雑な条件
```
WHERE age >= 20 AND (city = 'Shinjuku' OR city = 'Yokohama')
```
↓
```
condition → AND ─┬─ (age >= 20)
                 │
                 └─ OR ─┬─ (city = 'Shinjuku')
                        │
                        └─ (city = 'Yokohama')
```

<br>


</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：
パーサにも色々なアルゴリズムがありますが、
再帰的に処理できるように、このKeiPyDBでは再帰下降パーサという、一番シンプルなアルゴリズムを使っています。
-->
---
background: /background.png
---

<!-- Page 14 実行計画 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/planner.png" alt="Query Planner diagram" style="width: 100%; height: auto; margin-top: 18px; margin-left: -20px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Query Planner (実行計画)

## ASTを受け取って、実行方法を選択

```
SELECT
├─ columns: [id, name]
├─ table: users
└─ condition: name = 'Alice'
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
<img src="/executor.png" alt="Query Executor diagram" style="width: 100%; height: auto; margin-top: 18px; margin-left: -20px;">
</template>
<template v-slot:right>
<div>
<br>
<br>

# Query Executor (実行エンジン)
## 実行計画に従って、実際にデータを取得する

実行計画（前スライドから）：
1. テーブル`users`をフルスキャン
2. 各レコードの`name`をチェック
3. `name`が`'Alice'`のレコードを抽出
4. `id`と`name`を返す

</div>
</template>
</CustomTwoCols>

---
background: /background.png
---

<!-- Page 14.5 SQLクエリ実行フロー（アニメーション） -->

# SQLクエリ実行フロー

<div class="walking-rabbit">
  <div class="carrot">🥕</div>
  <div class="rabbit">🐰</div>
</div>

<div class="process-steps">
  <div class="step-marker step-1">📝 SQL Query</div>
  <div class="step-marker step-2">🔍 Parser</div>
  <div class="step-marker step-3">📋 Planner</div>
  <div class="step-marker step-4">⚙️ Executor</div>
  <div class="step-marker step-5">📊 Result</div>
</div>

<div class="query-example">
  <div class="sql-text">`SELECT id, name FROM users WHERE name = 'Alice'`</div>
</div>

<style>
.walking-rabbit {
  position: relative;
  height: 100px;
  margin: 2rem 0;
  overflow: hidden;
}

.carrot {
  position: absolute;
  font-size: 2.5rem;
  top: 50%;
  transform: translateY(-50%);
  animation: carrotRun 8s ease-in-out forwards;
}

.rabbit {
  position: absolute;
  font-size: 2.5rem;
  top: 50%;
  transform: translateY(-50%);
  animation: rabbitChase 8s ease-in-out forwards;
}

.process-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 2rem 1rem;
  position: relative;
}

.step-marker {
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
  padding: 1rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  opacity: 0.3;
  transition: all 0.5s ease;
}

.step-marker.active {
  opacity: 1;
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.query-example {
  text-align: center;
  margin-top: 2rem;
  opacity: 0;
  animation: fadeIn 1s ease-out 6s forwards;
}

.sql-text {
  font-size: 1rem;
  background: #f0f0f0;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  display: inline-block;
  font-family: 'Courier New', monospace;
  color: #333;
}

@keyframes carrotRun {
  0% {
    left: -100px;
    transform: translateY(-50%) rotate(0deg);
  }
  25% {
    left: 25%;
    transform: translateY(-50%) rotate(90deg);
  }
  50% {
    left: 45%;
    transform: translateY(-50%) rotate(180deg);
  }
  75% {
    left: 65%;
    transform: translateY(-50%) rotate(270deg);
  }
  100% {
    left: calc(100% - 100px);
    transform: translateY(-50%) rotate(360deg);
  }
}

@keyframes rabbitChase {
  0% {
    left: -200px;
    transform: translateY(-50%) scaleX(1);
  }
  12.5% {
    transform: translateY(-50%) scaleX(1) translateY(-10px);
  }
  25% {
    left: 15%;
    transform: translateY(-50%) scaleX(1) translateY(0px);
  }
  37.5% {
    transform: translateY(-50%) scaleX(1) translateY(-10px);
  }
  50% {
    left: 35%;
    transform: translateY(-50%) scaleX(1) translateY(0px);
  }
  62.5% {
    transform: translateY(-50%) scaleX(1) translateY(-10px);
  }
  75% {
    left: 55%;
    transform: translateY(-50%) scaleX(1) translateY(0px);
  }
  87.5% {
    transform: translateY(-50%) scaleX(1) translateY(-10px);
  }
  100% {
    left: calc(100% - 200px);
    transform: translateY(-50%) scaleX(1) translateY(0px);
  }
}

@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

/* ステップハイライト用のアニメーション */
.step-1 { animation: highlight 1s ease-out 1s forwards; }
.step-2 { animation: highlight 1s ease-out 2.5s forwards; }
.step-3 { animation: highlight 1s ease-out 4s forwards; }
.step-4 { animation: highlight 1s ease-out 5.5s forwards; }
.step-5 { animation: highlight 1s ease-out 7s forwards; }

@keyframes highlight {
  0% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
  100% { opacity: 0.8; transform: scale(1.05); }
}
</style>

---
background: /background.png
---

<!-- Page 15 デモ -->

# デモ: SELECT文の実行

<!-- スピーカーノート：


-->

---
background: /background.png
---

<!-- Page 16 ファイルI/O -->

# ディスク I/O（データの永続化）
## データの永続化と読み書き

```sql

SELECT id, name FROM users WHERE name = 'Alice';
```

## これでレコードを取得できることが分かりました。
<br>

## しかし、レコードをファイルに保存しないと、後から欲しいレコードを取り出せません。

<br>

## 次は、
```sql
INSERT INTO users (id, name) VALUES (259, 'Bob');
```

## を使って、ディスクに書き込むところを見ていきます。
<!-- スピーカーノート：
SELECTの処理は理解できました。でも、そもそもデータはどこから来るのでしょうか？
ディスクに保存して、データを永続化しないといけません。次はディスクへの書き込みの話です。
-->
---
background: /background.png
---

<!-- Page 17 ディスク書き込みの手順 -->


# よし！ディスクに書き込もう！
## でも、、、あれ？🤔

## ・毎回ディスクに書き込む？でもそれって遅いよね
## ・どこに書けばいいんだろう？
## ・他の人も同時に書き込んでいるかも？
## ・途中で電源が落ちてしまったら？

---
background: /background.png
---

<!-- Page 18 毎回ディスクに書く -->

# 毎回ディスクに書く？遅いよね。

## その通りです
## そこで、メモリを使う
## バッファを使って、メモリ上で作業して、後からディスクに書き込みます

---
background: /background.png
---

<!-- Page 19 ブロック管理 -->

# どこに書けばいいんだろう？
## 書き込めるブロックを探して(メモリに読み込んで)、そこに書き込みの指定をする(メモリ上)

users.tbl
┌─────────────┐
│  Block 0    │ 256バイト
│  ・id=255   │
│  ・Alice    │ ← 既存レコード
│             │
│  （空き）    │ ← ここにかける
│  （空き）    │ 
├─────────────┤
│  Block 1    │ （未使用）
└─────────────┘

## 📝 Bobを追加すると...
Block 0の空きスペースに `id=259, Bob` が入る

<!-- スピーカーノート：
ディスク上のデータは、ブロックという単位で管理します。
ブロックは、一定のサイズ（例えば256バイト）で区切られたデータの単位です。

今日は時間がないので、詳しい話はできませんが、実は、このブロック単位の管理があるからこそ、
インデックスが効果的に働きます。
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

# 他の人も同時に書き込んでたらどうしよう？

## トランザクションで同時書き込みを制御する

## 問題：同時に編集
ユーザーA：Block 0にBob追加
ユーザーB：Block 0にCarol追加
→ データが壊れる！😱

## 解決：順番に処理
ユーザーA：Block 0をロック → 編集 → 解除
ユーザーB：（待機） → 編集


<!-- スピーカーノート：
複数のユーザーが同時にデータベースを使うとき、
トランザクションがロックをかけて、
順番に処理することで、データの整合性を保ちます。
-->
---
background: /background.png
---

<!-- Page 21 途中で電源が落ちてしまったら？ -->

# 途中で電源が落ちてしまったら？
## WAL（Write-Ahead Log）で障害から復旧
## データより先にログを書き込む

## ログ：「Bob追加予定」→ ディスクへ
## メモリ：Bob追加
## 💥 停電！
## 再起動：ログを見る → Bobを復元！😊

- ログあり → 復元
- ログなし → なかったことに

<!-- スピーカーノート：
メモリは高速ですが、電源が切れると内容が消えます。
そこで、WAL（Write-Ahead Log）という仕組みを使います。

データを書く前に、必ず「何をするか」をログに記録。
ログはすぐにディスクに書きます。
これで、ログから復旧できます。
-->
---
background: /background.png
---

<!-- Page 22 最終的にディスクへ -->

# 最終的にディスクへ
## メモリ上で作業 → COMMITで永続化

## 1. メモリ上で編集
**Bob追加（まだメモリだけ）**

## 2. 変更時にWALログ記録
**「Bob追加する」→ ログに記録**

## 3. COMMIT実行
**変更されたバッファをディスクへ**

## 4. コミットログ記録
**「Commit完了」→ ログに記録**

## 5. バッファをクリーンな状態に
**次の処理の準備完了**

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
# デモ: INSERT文の実行



---
background: /background.png
---

<!-- Page 24 ディスク書き込みのまとめ -->

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
# エンディアンについて
## エンディアンとは、バイトの並び順のこと
## 258と259を使った理由がエンディアン
## 258と259は、16進数で0x0102と0x0103
## でも、ディスクには02 01と03 01と書かれる
## これはリトルエンディアンで書き込んでいるから

## これはPythonのstructモジュールを使って、意図的に逆に書き込んでいます
```python
# 例: 16進数で0x0102をバイト列に変換
import struct
data = struct.pack('<i', 258)  
```


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
<-!-- Page 26 エンディアン2 -->

# Pythonのstructモジュール
## Pythonでは、structモジュールを使ってバイト列の変換ができます
```python
import struct
# 例: 16進数で0x0102をバイト列に変換
data = struct.pack('<i', 258)  # リトルエンディアンで書き込む
```

## `<i`はリトルエンディアン
## `>i`はビッグエンディアン
## `!i`はネットワークバイトオーダー（ビッグエンディアン）



---
background: /background.png
---

<!-- Page27 デモ -->
# デモ: エンディアンの確認


---
background: /background.png
---

<!-- Page 26 まとめ -->

# まとめ
## KeiPyDBを使って、RDBMSの内部動作を追ってきました

---
background: /background.png
---
<!-- Page 27 we are hiring -->
## 株式会社DeltaXでは、Webエンジニアを募集中です！

・言語：Python／TypeScript
・フレームワーク：FastAPI／Astro／React／Remix
・インフラ環境：AWS／OpenSearch／PostgreSQL／DynamoDB／Docker／Google Cloud

## フルリモート可
## 生成AIを積極的に活用してます

---
background: /background.png
---
<!-- Page 28 挨拶 -->

# ご清聴ありがとうございました！


---