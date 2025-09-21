<style>
/* グローバルフォントサイズの統一設定 */
.slidev-code {
  font-size: 1.44rem !important;
  margin-top: 20px !important;
}
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

<!--　スピーカーノート：
最初に自己紹介させてください
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

<img src="/cm.png" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; object-fit: contain;" />
<!--
スピーカーノート：
関東圏にお住まいの方であれば、お笑い芸人のかが屋さんのCMを見たことがある方がいらっしゃるかもしれません。
このCMのサービスの会社です。
手前味噌ですが、このCMはYou Tubeで公開されていて、塾に関心がなくても面白いCMになっているので、ぜひ見てみてほしいです。
-->


---

<!-- Page 4 本題への区切り -->

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.2);" />
</div>

<div style="margin-left: 20rem; margin-top: 15rem">

# はじめに
</div>



<!--
スピーカーノート：
データベースとは、から説明させてください。
-->


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
データベースとは〜
データベースにもいろいろ種類があって、〜などがあります。

その中で今日取り上げるRDBMSは、〜という特徴があります。
-->

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

<div style="margin-left: 2rem; font-size: 1.5rem; font-weight: bold;">
Pythonで、標準ライブラリのみを使って実装
</div>
  </template>
</CustomTwoCols>

<!-- スピーカーノート：
今日使う、Python製RDBMSですが、これは自作しました。
Database Design and Implementation という一般にSimpleDB本と呼ばれる書籍を参考にしてます。
JavaでRDBMSを実装していく内容ですが、書籍を参考に、Pythonで標準ライブラリのみ使って実装しています。
-->

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
SQLは、〜〜があって、機能としては〜〜があります。
このRDBMSを使って話すことは、

-->


---

<!-- Page 8.5 話すこと -->

# 話すこと

## 🍋 RDBMSがSQLをどのように処理するか

<br>
<div style="margin-left: 30px;">

## ⚪︎ CREATE TABLE
## ⚪︎ INSERT INTO
## ⚪︎ SELECT
## ⚪︎ DELETE

</div>
<br>

<div style="margin-left: 45px;">

##   を使って、コードを逐次追いながらみていきます
</div>



<!-- スピーカーノート：
RDBMSがSQLをどのように処理するかをコードを逐次追いながらみていきます。
-->
---


<!-- Page 8 話さないこと -->


# 話さないこと
<br>

## ❌ 特定のデータベース製品の性質や使い方
## ❌ SQL文の書き方
## ❌ インデックス戦略
## ❌ パフォーマンスチューニング
## ❌ テーブル設計や正規化


<!-- スピーカーノート：
RDBMSのしくみを見ていくことで、DB君は裏側でこんな感じで頑張っているんだな、
とイメージが湧いて、トラブルシューティングの時などに、仕組みがこうだから、ここを疑ってみよう、
みたいな感じで役に立つといいかなと思います。
-->

---

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.2);" />
</div>

<div style="margin-left: 25rem; margin-top: 15rem">

#  全体像

</div>

<!--
スピーカーノート：
-->
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
        
## クライアントは、何を取得したいかを伝えるだけで、
## どうやって取得するかはRDBMSが決める
<br>


<!-- スピーカーノート：
さて、RDBMSの特徴の一つはSQLを使うことです。
RDBMSは、宣言型のSQLを、命令型の処理に変換して実行するわけですが、
どうやっているのか。アーキテクチャを見ていきます。
-->

---

<!-- Page 10 アーキテクチャ -->

# RDBMSのアーキテクチャ
<img src="/architecture.png" style="width: 73%; height: 86%; margin-left: 160px; margin-top: -22px">


<!-- スピーカーノート：
クライアントからSQLを受け取ると、まずParserがSQLを解析します。
Parserはさらに、LexerとParserに分かれています。
Lexerが文字列を単語に分解して、Parserが単語から意味を理解します。
Plannerが実行計画を立てて
Executorが実行します。
Executorはストレージ層とやりとりします。そこでは
Buffer Managerがメモリを管理して、
File Manager:がディスクの読み書きをする
-->

---

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.2);" />
</div>

<div style="margin-left: 20rem; margin-top: 15rem">

#  SELECT 文

</div>

<!--
スピーカーノート：
SELECT文を使って、細かく見ていきます
-->
---

# SELECT 文

```sql
SELECT id, name FROM users WHERE name = 'Alice'
```

<img v-click="1" src="/select_alice.png" alt="Parser diagram" style="width: 90%; height: auto; margin-left: -10px; margin-top: 30px;">


<!-- スピーカーノート：
今回利用するSELECT文です。
なぜidが258という中途半端な値なのかは、あとで説明します。
今は気にしなくて大丈夫です。
-->

---

<!-- Page 11 字句解析 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 92%; margin-top: 24px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Lexer (字句解析)
## SQLをトークン（意味のある最小単位）に分解する
<br>

<style scoped>
.slidev-code {
  font-size: 1.48rem !important;
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
一つ一つ見ていくと、まずLexerで、〜〜SQLを一つ一つ分解します

-->
---

<!-- Page 12 字句解析（分類） -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 92%; margin-top: 24px; margin-left: -10px;">
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

<style scoped>
.slidev-code {
font-size: 1.44rem !important;
margin-left: -40px !important;
margin-right: -40px !important;
}
</style>

```python {all|7}
class StartServer:
    
    @staticmethod
    def main() -> None:
        # SELECT
        tx_select = db.new_transaction()
        select_sql = "SELECT id, name FROM users WHERE name = 'Alice';"
        print(f"Executing: {select_sql}")
        plan = planner.create_query_plan(select_sql, tx_select)
        scan = plan.open()

```

<!-- スピーカーノート：
実際のコードを見てみます。
select文を実行する部分です。

-->

---


```python
class Lexer:
    def __init__(self, sql: str) -> None:
        """SQL文を解析するための字句解析器"""
        self.keywords = {
            "select",
            "from",
            "where",
            "and",
            "insert",
            "into",
            "values",
            "delete"
        }

```
<!-- スピーカーノート：
最初の字句解析の部分です。
予約語を定義していて、Lexerクラスで初期化します。

-->

---

```python{all|1-5|1-3,6|all}

class Lexer:
    def _tokenize(self, sql: str) -> list[str]:
        """SQL文をトークンに分割"""
        token_pattern = (r"[a-zA-Z_][a-zA-Z_0-9]*|'(?:[^']|'')*'"
                         r"|\d+(?:\.\d+)?|[=,()<>*+-/;]|\s+|.")
        token_list = re.findall(token_pattern, sql)
```

<!-- スピーカーノート：

tokenizeメソッドで、正規表現をマッチさせてトークンに分解します。
-->

---

```python {all|1-6|1,7-13|all}
class Lexer:
    def match_keyword(self, keyword: str) -> bool:
        """指定されたキーワードと現在のトークンが一致するかどうかを返す"""
        if self.current_token is None:
            return False
        return self.current_token.lower() == keyword.lower()

    def eat_keyword(self, keyword: str) -> None:
        """指定されたキーワードを認識して次のトークンに進む"""
        if self.current_token.lower() != keyword.lower():
            raise SyntaxError

        self.next_token()
```

<!-- スピーカーノート：
Lexerクラスには、予約語かどうかを判定するmatch_keywordメソッドと、
予約語を認識して次のトークンの処理に進むeat_keywordメソッドがあります。
eat_keywordメソッドにnext_tokenメソッドがあることで、
トークンを左から右に、かつ一度だけ処理し、次の解析ステップへ進めることができます

※ 再帰下降パーサ

-->

---


```python {all|1-6|1,7-13|all}
class Lexer:
    def match_id(self) -> bool:
        """現在のトークンが識別子かどうかを返す"""
        
        return (self.current_token.isidentifier() and
                self.current_token not in self.keywords)

    def eat_id(self) -> str:
        """識別子を認識して次のトークンに進む"""
        
        identifier = self.current_token
        self.next_token()
        return identifier
```

<!-- スピーカーノート：
また、予約語と同じように識別子かどうかを判定するmatch_idメソッドと、
識別子を認識して次のトークンの処理に進むeat_idメソッドがあります。

これは、他にも、区切り文字、演算子、リテラルなどに対しても同様のメソッドがあります。
-->

---

<!-- Page 16 構文解析-->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 92%; margin-top: 24px; margin-left: -20px;">
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

```
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
SQL文をコンピュータが理解しやすい木構造に変換したものです。
-->

---

<!-- Page 13 Parser - 複雑な条件 -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/parser.png" alt="Parser diagram" style="width: auto; height: 92%; margin-top: 24px; margin-left: -20px;">
</template>
<template v-slot:right>
<div>

# Parser - 複雑な条件

```sql
WHERE price < 1000 AND 
 ( sweets = '牡蠣せんべい' OR sweets = 'もみじ饅頭')
```
<div style="text-align: center; font-size: 1.6em;">⬇︎</div>

```
condition → AND ─┬─ price < 1000
                 │
                 └─ OR ─┬─ sweets = '牡蠣せんべい'
                        │
                        └─  sweets = 'もみじ饅頭'
          
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

<!-- Page 14 Parser - ASTの詳細 -->

```python {all|5}
class Planner:
    def create_query_plan(self, query: str, tx: TX) -> Plan:
        """クエリを実行するための計画を作成する"""
        parser = Parser(query)
        parsed_query = parser.query()

        self.verify_query()
```

<!-- スピーカーノート：
クエリメソッドを実行していきます
-->

---

```python {all|1-4}
class Parser:
    def query(self) -> QueryData:
        self.lexer.eat_keyword("select")
        field_list = self.select_list()
        self.lexer.eat_keyword("from")
        table_list = self.table_list()

        predicate = Predicate()
        if self.lexer.match_keyword("where"):
            self.lexer.eat_keyword("where")
            predicate = self.predicate()

        return QueryData(field_list, table_list, predicate)

```

<!-- スピーカーノート：
このクエリメソッドが構文解析のメインの部分で、
SELECT文の解析を開始するエントリポイントです
まず、現在のトークンがSELECTであることを確認すると、次のトークンの処理に進みます。


-->
---

```python {all|1-3|1-2,4-6|all}
class Parser:
    def select_list(self) -> list[str]:
        field_list = [self.field()]
        while self.lexer.match_delimiter(","):
            self.lexer.eat_delimiter(",")
            field_list.append(self.field())
        return field_list
```

<!-- スピーカーノート：
次のトークンは、フィールド名として処理されます。
select_listメソッドは、最初のフィールド名（これはカラム名に相当します）を解析してリストに追加します。
その後、カンマが続く限り、カンマを認識して次のフィールド名をリストに追加できるので、
全てのカラム名をフィールドリストとして返すことができます。

-->

---


```python {1-2,5-6}
class Parser:
    def query(self) -> QueryData:
        self.lexer.eat_keyword("select")
        field_list = self.select_list()
        self.lexer.eat_keyword("from")
        table_list = self.table_list()

        predicate = Predicate()
        if self.lexer.match_keyword("where"):
            self.lexer.eat_keyword("where")
            predicate = self.predicate()

        return QueryData(field_list, table_list, predicate)

```
<!-- スピーカーノート：

次に、FROMキーワードを認識して、次のトークン処理に進んで、テーブルリストを作成します。

-->

---

```python {all|1-5|6-11|6-12|all}

class Parser:
    def table_list(self) -> Collection[str]:
        table_name = self.lexer.eat_id()

        table_list: list[str] = [table_name]
        
        while self.lexer.match_delimiter(","):
            self.lexer.eat_delimiter(",")
            table_name = self.lexer.eat_id()
            table_list.append(table_name)
            
        return table_list
        
```
<!-- スピーカーノート：
このtable_list()メソッドでも、最初のテーブル名を解析してリストに追加して、
カンマが続く限り、カンマを認識して次のテーブル名をリストに追加していきます。
-->


---

```python {1-2,8-12}
class Parser:
    def query(self) -> QueryData:
        self.lexer.eat_keyword("select")
        field_list = self.select_list()
        self.lexer.eat_keyword("from")
        table_list = self.table_list()

        predicate = Predicate()
        if self.lexer.match_keyword("where"):
            self.lexer.eat_keyword("where")
            predicate = self.predicate()

        return QueryData(field_list, table_list, predicate)

```

<!-- スピーカーノート：
最後に、WHERE句を認識して、次のトークンの処理に進んで、条件式を解析します。
predicateはname = Aliceのような条件式のことです。

-->
---

```python {all|1,3}
class Parser:
    def predicate(self) -> Predicate:
        predicate = Predicate([self.term()])
        if self.lexer.match_keyword("and"):
            self.lexer.eat_keyword("and")
            predicate.conjoin_with(self.predicate())
```

<!-- スピーカーノート：
predicateメソッドで条件式の処理をするのですが、まずはtermメソッドが呼ばれます。

-->
---

```python {all|1,8-9|1-9|1,10|1,11|1-7,11|12|all}
class Parser:
    def expression(self) -> Expression:
        if self.lexer.match_id():
            return Expression(self.field())
        else:
            return Expression(self.constant())
        
    def term(self) -> Term:
        left = self.expression()
        self.lexer.eat_delimiter("=")
        right = self.expression()
        return Term(left, right)
```

<!-- スピーカーノート：

termメソッドで、左辺を解析しています。
expressionメソッドで、識別子かリテラルを解析しています。

でイコールを認識して、
右辺も識別子かリテラルか解析して、条件式を形成して返します。

-->

---

```python {1-2,4-6|all} 
class Parser:
    def predicate(self) -> Predicate:
        predicate = Predicate([self.term()])
        if self.lexer.match_keyword("and"):
            self.lexer.eat_keyword("and")
            predicate.conjoin_with(self.predicate())
```

<!-- スピーカーノート：
また、ANDで条件記が続く場合、再帰的にpredicateメソッドを呼び出して、
条件式を連結しています。
-->

---

```python {1-2,13|all}
class Parser:
    def query(self) -> QueryData:
        self.lexer.eat_keyword("select")
        field_list = self.select_list()
        self.lexer.eat_keyword("from")
        table_list = self.table_list()

        predicate = Predicate()
        if self.lexer.match_keyword("where"):
            self.lexer.eat_keyword("where")
            predicate = self.predicate()

        return QueryData(field_list, table_list, predicate)

```

<!-- スピーカーノート：
これで、最初のqueryメソッドに戻ってきて、Queryオブジェクトを作成して返します。
これがASTです。
-->

---

<div style="margin-left: -50px; margin-right: -50px;">

<img src="/query_data.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 24px; ">
</div>

<!-- スピーカーノート：
これはデバッガーでの実行画面です。
query_dataが構造化されているのがわかります。
-->

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
ASTを受け取って、どのテーブルから、どのような順序と方法でレコードを取得するかという、実行計画を立てます。
例えば、複数のテーブルを結合（join）する時に、joinの順序を変えるだけでも、実行時間が大きく変わることもあります。

そのために、本格的なRDBMSは統計情報を使って最適な実行計画を選んだり、
インデックスを使ったりしますが、ここではシンプルな実行計画を作成します。
-->

---

```python {1-6|7|9|all}
class Planner:
    def create_query_plan(self, query: str, tx: TX) -> Plan:
        """クエリを実行するための計画を作成する"""
        parser = Parser(query)
        parsed_query = parser.query()

        self.verify_query()

        return self.query_planner.create_plan(parsed_query, tx)
```

<!-- スピーカーノート：
ParserでSQLを解析して、ASTが作成されているので、
値や式の妥当性を検証した後に、
Query PlannerにASTを渡して、実行計画を作成します。
-->

---

```python {all|1-5|1-2,7-9|1-2,11-13|all}

class BasicQueryPlanner(QueryPlanner, ABC):
    def create_plan(self, query: Query, tx: TX) -> Plan:

        plan_list: list[Plan] = []
        plan_list.append(TablePlan(tx, table_name, self.mdm))

        plan = SelectPlan(plan, query.get_predicate())

        field_list = query.get_fields()

        return ProjectPlan(plan, field_list)

```

<!-- スピーカーノート：
実行計画を作成します。
まず、どのテーブルからレコードを取得するかを決めて、
TablePlanを作成します。
次に、WHERE句の条件式を使って、必要なレコードだけを取得するSelectPlanを加えます。
最後に、SELECT句のカラム名リストを使って、必要なカラムだけを取り出すProjectPlanを加えます。
ちなみに、SelectPlanのSelectの意味は、SELECT文のSelectではなくて、WHERE句で選択する、の意味です。
このselectとprojectは数学的な演算から来ている名前です

※ リレーショナル代数演算
-->

---

<div style="margin-left: -50px; margin-right: -50px;">

<img src="/plan_obj.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 30px;">
</div>


<!-- スピーカーノート：
ここもデバッガーでの実行を確認すると、
ProjectPlanの中にSelectPlanがあって、その中にTablePlanが作られていて、
プランの階層構造になっていることがわかります。
この階層構造をとることで、パイプライン処理と言って、データアクセスが一度で済んで、処理中の中間テーブルなどの作成が必要ないので、
効率的にデータ処理できます。

-->

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

## 2️⃣ Scan（実行オブジェクト）を作る
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
実行エンジンのしくみを理解するには、ストレージ層の理解が必要になるので、ここで一旦ストレージ層の話に移ります。

-->

---

<!-- Page 16 ストレージ層の概要 -->
<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/buffer_file.png" alt="Parser diagram" style="width: auto; height: 94%; margin-top: 18px; margin-left: -10px;">
</template>
<template v-slot:right>

# ストレージ層の概要

## **担当**
## 🍋 Buffer ManagerとFile Manager
## **解決したい課題**
## 🍋 大量のデータを扱いたい ↔️ 高速に処理したい

<div style="margin-left: 30px;">

## ディスクアクセスはメモリアクセスに比べて非常に遅い
</div>

## **役割**
## 🍋 RDBMS自身でメモリ管理(OSにまかせない)
## 🍋 データの永続化






</template>
</CustomTwoCols>

<!-- スピーカーノート：
大量のデータを扱いたいけど、高速に処理したい、という相反する要求をできるだけ
両立させようとしています。
-->

---

<!-- Page 17 用語 -->

<CustomTwoCols :leftRatio="80">
<template v-slot:left>
<img src="/disc.png" style="width: auto; height: 90%; margin-top: 30px; margin-left: -30px;">
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

<!-- Page 18 バッファマネジャ-->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/buffer.png" alt="Parser diagram" style="width: auto; height: 100%; margin-top: 16px; margin-left: -10px;">
</template>
<template v-slot:right>
<div>

# Buffer Manager
<br>

## RDBMS自身でメモリ管理(OSにまかせない)

## 🍋 ブロックのメモリへの読み込み
## 🍋 頻繁にアクセスされるブロックをメモリに保持
## 🍋 使用頻度が低いブロックのメモリからの追い出し



</div>
</template>
</CustomTwoCols>

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
## 🍋 ディスク上のデータをブロック単位で読み書き

</div>
</template>
</CustomTwoCols>

<!-- スピーカーノート：

-->

---

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.2);" />
</div>

<div style="font-size: 12rem; text-align: center; margin-top: 200px; margin-left: 400px;">
🍹
</div>
<!--
スピーカーノート：
-->



---

<!-- Page 20 レコードを探すしくみ -->

<CustomTwoCols :leftRatio="30">
<template v-slot:left>
<img src="/executor.png" alt="Parser diagram" style="width: auto; height: 92%; margin-top: 22px; margin-left: -10px;">
</template>
<template v-slot:right>

# レコード取得のしくみ


<style scoped>
.slidev-code {
  font-size: 1.35rem !important;
  margin-left: -32px !important;
  margin-right: -32px !important;
}
</style>

```python
ProjectPlan(
    fields=['id', 'name'],
    SelectPlan(predicate="name='Alice'",
        TablePlan('users')))
```

## 🍋 usersテーブルのブロックをストレージ層から

<div style="margin-left: 30px;">

## （トランザクションを介して）1つずつ読む
</div>

## 🍋 ブロックの中は
<div style="margin-left: 30px;">

## **スロット**という単位でレコードが保存されている
</div>

<div style="margin-left: 10rem; margin-top: -10px; margin-bottom: -20px; font-size: 1.2rem;">⬇︎</div>

## 🍋 **スロット**の単位で探す

</template>
</CustomTwoCols>

<!-- スピーカーノート：
ストレージ層、ファイル、ブロックなどの説明ができたので、
Executorに戻って、実際にレコードを取得するしくみを見ていきます。

-->

---

<!-- Page 21 スロットとは何か -->


<CustomTwoCols :leftRatio="50">
<template v-slot:left>
<div>

# スロットとは何か

## 🍋 テーブル情報から定義される

<div style="margin-left: 30px;">

## ブロック内の固定長の領域
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

<!-- Page 22 Appendix -->

# レコードの読み取り
## 🍋 スロットのレイアウトがわかれば、レコードにアクセス可能
## 🍋 スロット毎に、13バイト目から10バイト分を確認
## 🍋 nameがAliceかどうかの確認
## 🍋 レコードを取得して指定されたカラムの出力 { id: 258, name: 'Alice' }

<img src="/slot7.png" alt="Slot layout diagram" style="width: auto; height: 35%; margin-left: 18rem; margin-top: 40px;">

<!-- スピーカーノート：
1スロットが22バイトだとわかれば、22バイトずつ探していけばいいわけです。
1スロットずつ、スロットの中の13バイト目から10バイト分を見て、nameがAliceかどうかを確認します。
-->

---

<style scoped>
.slidev-code {
font-size: 1.45rem !important;
margin-left: -44px !important;
margin-right: -44px !important;
}
</style>

```python {1-5,9-10}
class StartServer:
    
    @staticmethod
    def main() -> None:
        # SELECT
        tx_select = db.new_transaction()
        select_sql = "SELECT id, name FROM users WHERE name = 'Alice';"

        plan = planner.create_query_plan(select_sql, tx_select)
        scan = plan.open()

```

<!-- スピーカーノート：
実際のコードを見てみます。
planが作成できたところからです。
planはopenメソッドを持っているので、openしてscanを開始します
-->

---

<style scoped>
.slidev-code {
margin-left: -35px !important;
margin-right: -32px !important;
}
</style>

```python {all|1-5|1-4,6-10}
class TableScan(UpdateScan, ABC):   
    def get_value(self, field_name: str) -> Constant:
        """現在のスロットの指定されたフィールドの値を返す"""
        
        field_type = self.layout.get_schema().get_type(field_name)
        
        if field_type == FieldType.Integer:
            return Constant(self.get_int(field_name))
        elif field_type == FieldType.Varchar:
            return Constant(self.get_string(field_name))
        else:
            raise ValueError(f"Unknown field type {field_type}")

```

<!-- スピーカーノート：
テーブル定義情報をもとに、指定されたフィールドの型を調べて、
get_intメソッドかget_stringメソッドを呼び出して、値を取得します。
-->

---

```python {all|1-4,8-9|all}
class TableScan(UpdateScan, ABC):
    def get_string(self, field_name: str) -> str:
        """現在のスロットの指定されたフィールドの文字列を返す"""
    
        if self.record_page is None:
            raise RuntimeError
    
        slot = self.current_slot
        return self.record_page.get_string(slot, field_name)


```
<!-- スピーカーノート：
get_stringメソッドの例ですが、カレントスロットのフィールド名を指定して、
値を取得していることがわかると思います。
-->

---

```python

class SelectScan(UpdateScan, ABC):
    def next(self) -> bool:
        while self.scan.next():
            if self.predicate.is_satisfied(self):
                return True
        return False
```

<!-- スピーカーノート：
SelectScanメソッドで、ループ処理で条件式(name = 'Alice')を満たすかどうかを確認しています。
-->

---

```python
class ProjectScan(Scan, ABC):
    def get_value(self, field_name: str) -> Constant:
        
        if self.has_field(field_name):
            return self.scan.get_value(field_name)
        else:
            raise RuntimeError

```

<!-- スピーカーノート：
最後に、ProjectScanメソッドで、必要なカラムだけを取り出しています。
-->
---

<style scoped>
.slidev-code {
font-size: 1.4rem !important;
margin-left: -40px !important;
margin-right: -40px !important;
}
</style>

```python {13-14}
class StartServer:
    @staticmethod
    def main() -> None:
        # SELECT
        tx_select = db.new_transaction()
        select_sql = "SELECT id, name FROM users WHERE name = 'Alice';"
        plan = planner.create_query_plan(select_sql, tx_select)
        scan = plan.open()
        while scan.next():
            print(f"id = {scan.get_int('id')}, "
                  f"name = {scan.get_string('name')}")

        scan.close()
        tx_select.commit()
```

<!-- スピーカーノート：
scan.close()でexecutorを終了させて、commitして終了です
-->

---

<!-- Page 20 レコードを探すしくみ -->

<img src="/select_alice.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 130px;">

<!-- スピーカーノート：
実行すると、id = 258, name = 'Alice'が出力されます。
-->


---

<div class="absolute inset-0" style="z-index: -1;">
  <img src="/back_top.png" class="w-full h-full object-contain" style="filter: brightness(1.2);" />
</div>
<div style="margin-left: 16rem; margin-top: 15rem">

# INSERT 文 & DELETE 文
</div>

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
## 🍋 トランザクションを介す
## 🍋 Write-Ahead Logging/
<div style="margin-left: 30px;">

## ログ先行書き込みで障害対策をする
</div>

## 🍋 空きスロットに書き込む

</template>
<template v-slot:right>


<img src="/slot_adding.png" alt="Parser diagram" style="width: auto; height: 45%; margin-top: 228px; margin-left: -30px;">
</template>
</CustomTwoCols>

<!-- スピーカーノート：
idが259、nameがBobのレコードを追加します。
-->

---

<!-- Page 25 ヘックスビュワー -->

<style scoped>
.slidev-code {
font-size: 1.45rem !important;
margin-left: -40px !important;
margin-right: -40px !important;
}

</style>

```python {all|1-7|1-3,8-11|1-3,13-14|all}
class BasicUpdatePlanner(UpdatePlanner, ABC):
    AFFECTED = 1
    def execute_insert(self, data: InsertData, tx: TX) -> int:
        """レコードを挿入する"""

        fields = data.get_fields()
        values = iter(data.get_values())

        for field_name in fields:
            value = next(values)
            scan.set_value(field_name, value)

        scan.close()
        return self.AFFECTED
```

<!-- スピーカーノート：
プランを作成して実行するところまではSELECTと同じです。
get_fields()でカラム名のリストを取得して、
set_valueで対応するカラムに値をセットしています。
close()で、scanを閉じて、処理されたレコード数を返しています。


-->

---

```python

class FileManager:
    def write(self, block: BlockID, page: Page) -> None:
        """ブロックIDに対応するファイルにデータを書き込む"""
        try:
            f = self._get_file(block.file_name)
            f.seek(block.block_number * self.block_size)
            f.write(page.buffer)
            f.flush()
            os.fsync(f.fileno())  # 確実にディスクに書き込み
```

<!-- スピーカーノート：
FileManagerのwriteメソッドで、ファイルの指定したブロックにデータを書き込んでいます。
-->
---

<!-- Page 24 削除 -->

<CustomTwoCols :leftRatio="50">
<template v-slot:left>


# レコードの削除(DELETE)

```sql
DELETE FROM users WHERE id = 259
```

## 🍋 データはすぐには消さない
## 🍋 (トランザクションを介して)

<div style="margin-left: 30px; margin-top: -20px;">

## スロットの状態フラグを00に更新
## データはそのまま残る
</div>

## 🍋 後でレコードを追加する時に

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
id = 259のレコードを削除するのですが、

---

<style scoped>
.slidev-code {
margin-left: -40px !important;
margin-right: -40px !important;
}
</style>

```python {all|1-7|1-5,9-11|all}

class RecordPage:
    EMPTY = 0
    USED = 1

    def delete(self, slot: int) -> None:
        """指定されたスロットを削除する"""
        self._set_flag(slot, RecordPage.EMPTY)
        
    def _set_flag(self, slot: int, flag: int) -> None:
        """スロットの状態を設定する"""
        self.tx.set_int(self.block, self._offset(slot), flag, True)

```

<!-- スピーカーノート：
deleteメソッドで、指定されたスロットの状態フラグをEMPTYに更新しています。
-->

---

<img src="/bob_delete.png" alt="Parser diagram" style="width: 100%; height: auto; margin-top: 50px; margin-left: -10px;">


<!-- スピーカーノート：
デバッガーで確認すると、
黄色の星印のところで、Aliceのレコードの後に、Bobのレコードが追加されました。
その後、usersテーブルをSELECTすると、
AliceとBobの2つのレコードが出力されて
その後、DELETE文でBobのレコードを削除すると、
Aliceのレコードだけが出力されることがわかります
-->
---

<!-- Page 26 スクショで確認 -->

# ヘックスビュアーで確認
<br>

<img src="/hex.png" style="width: 110%; max-width: none; image-rendering: crisp-edges; margin-top: -3rem; margin-left: -40px; margin-right: -35px;" />

<img src="/slot_delete.png" style="width: 77%; height: auto; margin-left: 16px;" />

<!-- スピーカーノート：
実際にバイナリファイルの中身を確認して、データが正しく保存されているか見てみましょう。
このスクリーンショットは、バイナリファイルを16進数で表示したものです。

左側に16進数の値が並んでいて、右側にはそれに対応するASCII文字が表示されています。
- 黄色　最初の4バイト：状態フラグ（int）
- 水色　次の4バイト：ID（int）  
- 薄いピンク　次の4バイト：文字列長（int）
- 濃いピンク　続く10バイト：name（char配列）

で、ここで注目してほしいのが、int型のデータの並び方なんですが...
なんか直感と違いませんか？
-->

---

<!-- Page 27 エンディアン -->

# int型の並び順が逆

<div style="width: 40%; margin: 0;">
<TransparentTable :items="[
  { label: '10進数', value: '16進数' },
  { label: '258', value: '0x0102' },
  { label: '259', value: '0x0103' }
]" :showOuterBorder="true" :showRowLines="true" />
</div>
<br>

<div style="position: relative;">
  <img src="/hex.png" style="width: auto; height: 38%;" />

  <!-- 258 (0x0102) の矢印 -->
  <div v-click="1" style="position: absolute; top: -70%; left: 30%;">
    <div style="color: red; font-size: 8rem; font-weight: bold;">
      <span style="display: inline-block;">↓</span>
      <span style="display: inline-block; position: relative; top: 2rem; left: 3rem;">↓</span>
    </div>
  </div>
</div>


<!-- スピーカーノート：

-->


---

<!-- Page 28 エンディアン1 -->


# エンディアン

## バイト列の並び順の設定の違い

## **リトルエンディアン** 
### 🍋 数値の最下位バイトがアドレスの低い方 → 258 (0x0102) は `02 01` 

## **ビッグエンディアン** 
### 🍋 数値の最上位バイトがアドレスの低い方 → 258 (0x0102) は `01 02` 

## **なぜ重要？**
### 🍋異なるシステム間でバイナリデータをやり取りする時
### 🍋ネットワーク通信（ビッグエンディアン）


<!--　スピーカーノート：
リトルエンディアンとビッグエンディアンは、必ずしもどちらが優れている、というわけではなく、
歴史的経緯などもあって、2種類の方式が存在しています。
なので、、異なるシステム間でバイナリデータをやり取りする時やネットワーク通信の実装では、エンディアンに注意する必要があります。

今私が使っているM3MacのCPUはリトルエンディアンです。
-->
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

<!-- Page 30 まとめ -->



<div class="summary-content">
<CustomTwoCols :leftRatio="30">
<template v-slot:left>
  <img src="/architecture1.png" style="width: auto; height: auto; margin-top: 20px;"/>


</template>
<template v-slot:right>
<div style="padding-left: 4rem;">

# まとめ
## 🍋 **Lexer (字句解析)** - SQLをトークンに分解

## 🍋 **Parser (構文解析)** - トークンからAST構築

## 🍋 **Planner (実行計画)** - 最適な実行順を決定

## 🍋 **Executor (実行エンジン)**
<div style="margin-left: 30px;">

## 実行計画に従ってデータにアクセス
</div>

## 🍋 **Buffer Manager** - データのメモリ保持

## 🍋 **File Manager**
<div style="margin-left: 30px;">

## エンディアン変換
## ディスクへの読み書き

</div>
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

<!-- Page 32 挨拶 -->

# 最後に

## インデックス、ログ、トランザクション ...まだまだ話したいことが...
<br>

## KeiPyDBのソースコードは、GitHubに公開済みです
## [https://github.com/kei-kmj/KeiPyDB](https://github.com/kei-kmj/KeiPyDB)


<br>

## **次にやりたいこと**
## 🍋ブラウザを自作して、KeiPyDBを組み込みたい‼️

<div style="margin-left: 180px;">

# ご清聴ありがとうございました
</div>

<img src="/thankyou.png" style="position: absolute; bottom: 30px; right: 0px; width: 240px; height: auto;" />
