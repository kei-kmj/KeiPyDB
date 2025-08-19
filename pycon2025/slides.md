

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

<!-- Page 2 塾選紹介-->

<img src="/bestjuku.png" style="position: absolute; top: 0; left: 0; right: 0; bottom: 30px; width: 100%; height: calc(100% - 30px); object-fit: contain;" />

<!--
スピーカーノート：
塾選のバックエンドはPython FastAPIでできています。
-->
---


<!-- Page 3 CMスクショ-->

<img src="/cm.png" style="position: absolute; top: 0; left: 0; right: 0; bottom: 30px; width: 100%; height: calc(100% - 30px); object-fit: contain;" />
<!--
スピーカーノート：
関東圏にお住まいの方であれば、お笑い芸人のかが屋さんのCMを見たことがあるかもしれません。
このCMの会社です。
手前味噌ですが、このCMはYou Tubeで公開されているので、ぜひ見てみてください。
-->

---

<div class="absolute inset-0">
  <img src="/background3.png" class="w-full h-full object-cover" />
</div>

<!-- Page 4 作ってみた -->

# 自作RDBMS:KeiPyDBを作ってみた
<br>

## Pythonの言語仕様とDBの内部構造を同時に学ぼうと思い立ち、RDBMS:KeiPyDBを作ってみました。
<br>

## 主に参考にしたのは、
# 「Database Design and Implementation」
## JavaでRDBMSを実装していく内容
<br>

## それを元にPythonでミニマルなRDBMSを実装してみました。
<!-- スピーカーノート：
-->
---

<div class="absolute inset-0">
  <img src="/background3.png" class="w-full h-full object-cover" />
</div>

<!-- Page 5 KeiPyDBの機能 -->

# KeiPyDBの機能
- SQL文の実行
  - CREATE TABLE
  - INSERT
  - SELECT
  - UPDATE 
  - DELETEなどの基本的なSQL文
  - CROSS JOIN
- トランザクション
- ハッシュインデックス
- Btreeインデックス
<br>

## 今日はこのKeiPyDBを使って、RDBMSの内部動作を追っていきたいと思います。

---
background: /background.png
---

<!-- Page 6 Goal-->
# GOAL

### データベースの内部動作がを見て理解できる

<br>

#### 具体的には...
## 1. SELECT
```sql
  SELECT id, name FROM users WHERE name = 'Alice';  # id = 258 name = 'Alice'
```

  → RDBMSがどうやってAliceを見つけるか分かる
## 2. INSERT
```sql
  INSERT INTO users (id, name) VALUES (259, 'Bob');
```
  → どのようにディスクに書き込まれるか分かる
<br>
 
※ idが258と259である理由は、あとで、ヘックスビュワーのところで説明します。今は特に気にしないでください。

---
background: /background.png
---

<!-- Page 7 NO GOAL -->
# NO GOAL
### ❌ 難しいSQL文が書けるようになる
### ❌ 適切なインデックス戦略やパフォーマンスチューニングが分かるようになる  
### ❌ PostgreSQLやMySQLなどの特定のRDBMSの使い方が分かる
<br>
<br>
<br>

### データベースがちょっと身近に感じられるかも


---
background: /background.png
---

<!-- Page 8 データベースとは -->
# データベースとは
## データベースとは、データを効率的に保存・検索・更新するためのシステム
<br>

##  データベースの種類
- RDBMS → PostgreSQL, MySQL
- NoSQL → MongoDB, Redis
- グラフDB → Neo4j

<br>

## RDBMS
### Relational Database Management System

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
# SQLは宣言型言語
```sql

SELECT id, name FROM users WHERE name = 'Alice'
```
        
### 何を取得したいかを指定するだけで、どうやって取得するかはRDBMSが決める

これをPythonで命令型で書くと、
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

### RDBMSは、宣言型のSQLを、命令型の処理に変換して実行する



---
background: /background.png
---

<!-- Page 10 アーキテクチャ -->
# RDBMSのアーキテクチャ

### SQL Query   
#### ↓   
### Parser   
###  ├─ Lexer (字句解析): 文字列を単語に分解   
###  └─ Parser (構文解析): 単語から意味を理解   
#### ↓   
### Query Planner: どうやって実行するか計画を立てる    
#### ↓   
### Query Executor: 実際に実行する   
#### ↓   
### Buffer Manager: メモリを管理する   
#### ↓   
### File Manager: ディスクを読み書きする   
#### ↓   
### Disk


---
background: /background.png
---

<!-- Page 11 字句解析 -->
# Lexer (字句解析)
## 文字列をトークン（意味のある最小単位）に分解する
`SELECT id, name FROM users WHERE name = 'Alice'`   
↓   
`SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`   

| トークン | 種類（Lexerが判定） |
|---------|--------------|
| `SELECT`, `FROM`, `WHERE` | キーワード（予約語）   |
| `id`, `name`, `users` | 識別子          |
| `,` | デリミタ = 区切り文字 |
| `=` | 演算子          |
| `'Alice'` | 文字列リテラル      |

---
background: /background.png
---

<!-- Page 12 構文解析-->
# Parser (構文解析)
## トークンを解析して、SQLの意味を理解

## トークン列をルールに従って構造化

`SELECT` `id` `,` `name` `FROM` `users` `WHERE` `name` `=` `'Alice'`  
↓
## AST（抽象構文木）
```
  QueryData
  ├─ SELECT: [id, name]
  ├─ FROM: users
  └─ WHERE: (name = 'Alice')

```

## 複雑な条件の場合
```
condition → AND ─┬─ (age >= 20)
                 │
                 └─ OR ─┬─ (city = 'Shinjuku')
                        │
                        └─ (city = 'Yokohama')
```

<!-- スピーカーノート：
構文解析では、トークンをルールに従って構造化して、抽象構文木（AST）を作成します。
このSQLの例では木構造になっていることが分かりにくいですが、
複雑な条件がある場合でも、木構造で表現できます。
-->
---
background: /background.png
---

<!-- Page 13 実行計画 -->
# Query Planner (実行計画)
## ASTから「どうやってデータを取得するか」を決める

## ASTを受け取って、実行方法を選択

```
SELECT
├─ columns: [id, name]
├─ table: users
└─ condition: name = 'Alice'
```

↓
## 実行計画

1. テーブル`users`をフルスキャン
2. 各レコードの`name`をチェック
3. `name`が`'Alice'`のレコードを抽出
4. `id`と`name`を返す

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

# Query Executor (実行エンジン)
## 実行計画に従って、実際にデータを取得する

実行計画（前スライドから）：
1. テーブル`users`をフルスキャン
2. 各レコードの`name`をチェック
3. `name`が`'Alice'`のレコードを抽出
4. `id`と`name`を返す
---
background: /background.png
---

<!-- Page 15 デモ -->

# デモ: SELECT文の実行

1. **Lexer**: 文字列 → トークン列
   - `"SELECT id, name..."` → `['SELECT', 'id', ',', ...]`

2. **Parser**: トークン → AST
   - トークン列 → ASTの構築

3. **Planner**: AST → 実行計画
   - AST → フルスキャンの計画

4. **Executor**: 実行計画 → 結果
  - データにアクセスして結果を返す
  - （メモリorファイル、詳細は後ほど）

---
background: /background.png
---

<!-- Page 16 ファイルI/O -->

# ディスク I/O（データの永続化）
## データの永続化と読み書き

```sql

SELECT id, name FROM users WHERE name = 'Alice';
```

### これでレコードを取得できることが分かりました。
<br>

### しかし、レコードをファイルに保存しないと、後から欲しいレコードを取り出せません。

<br>

### 次は、
```sql
INSERT INTO users (id, name) VALUES (259, 'Bob');
```

### を使って、ディスクに書き込むところを見ていきます。
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

### ・毎回ディスクに書き込む？でもそれって遅いよね
### ・どこに書けばいいんだろう？
### ・他の人も同時に書き込んでいるかも？
### ・途中で電源が落ちてしまったら？

---
background: /background.png
---

<!-- Page 18 毎回ディスクに書く -->

# 毎回ディスクに書く？遅いよね。

## その通りです
### そこで、メモリを使う
### バッファを使って、メモリ上で作業して、後からディスクに書き込みます

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

### 📝 Bobを追加すると...
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

### 問題：同時に編集
ユーザーA：Block 0にBob追加
ユーザーB：Block 0にCarol追加
→ データが壊れる！😱

### 解決：順番に処理
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

### ログ：「Bob追加予定」→ ディスクへ
### メモリ：Bob追加
### 💥 停電！
### 再起動：ログを見る → Bobを復元！😊

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

### 1. メモリ上で編集
**Bob追加（まだメモリだけ）**

### 2. 変更時にWALログ記録
**「Bob追加する」→ ログに記録**

### 3. COMMIT実行
**変更されたバッファをディスクへ**

### 4. コミットログ記録
**「Commit完了」→ ログに記録**

### 5. バッファをクリーンな状態に
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