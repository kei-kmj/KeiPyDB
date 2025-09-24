# PyCon JP 2025 プロポーザル技術ダイジェスト

## タイトル
**Python製RDBMSで理解する、データベースのピース**
〜コードのステップ実行とヘックスビューワーで内部動作を追ってみよう〜

## 概要
Pythonで自作したRDBMS「KeiPyDB」を使って、データベースの内部動作を可視化しながら理解する技術セッション。SQL文がどのように処理され、データがディスクに保存されるまでの過程を、実際のコードとヘックスビューワーを使って追跡する。

## 主要な技術トピック

### 1. RDBMSアーキテクチャ: Lexer→Parser→Planner→Executorの処理フロー

#### Lexer（字句解析）の実装
- SQL文字列を正規表現で分割してトークン配列を生成
- 各トークンを5種類に分類：キーワード（SELECT、FROM等）、識別子（テーブル名、カラム名）、デリミタ（カンマ、括弧）、演算子（=、<、>）、リテラル（文字列、数値）
- `match_keyword()`と`eat_keyword()`メソッドでトークンの種別判定と解析位置の前進を実装
- 現在のトークンを保持しながら、`next_token()`で順次処理を進める設計

#### Parser（構文解析）の実装
- 再帰下降パーサによるトップダウン構文解析
- `query()`メソッドから開始し、`select_list()`、`table_list()`、`predicate()`を再帰的に呼び出し
- WHERE句の条件式を`Term`（左辺・演算子・右辺）と`Predicate`（複数Termの論理積）で表現
- ANDで連結された条件は`conjoin_with()`で再帰的に処理
- 最終的にQueryDataオブジェクト（AST）を生成：フィールドリスト、テーブルリスト、条件式を構造化

#### Planner（実行計画）の実装
- ASTから物理的な実行計画への変換
- 3層の計画オブジェクトを生成：
  - `TablePlan`: テーブルスキャンの計画（最下層）
  - `SelectPlan`: WHERE句による行フィルタリング（中間層）
  - `ProjectPlan`: SELECT句による列選択（最上層）
- 各計画は`open()`メソッドでScanオブジェクトを生成
- 計画の階層構造により、中間結果を生成せずにパイプライン処理を実現

#### Executor（実行エンジン）の実装
- Scanインターフェースによるイテレータパターン
- `next()`でレコードを1つずつ取得、`get_value()`で値を取得
- SelectScanは条件を満たすレコードが見つかるまで内部スキャンをループ
- ProjectScanは必要なカラムのみを上位に返す
- ストリーム処理により大量データでもメモリ効率的に処理

### 2. ストレージ層: Buffer Manager、File Manager、スロット管理

#### Buffer Managerの実装
- 固定サイズのバッファプール（デフォルト1024ページ）
- ページ単位（4KB）でディスクデータをメモリにキャッシュ
- LRU（Least Recently Used）アルゴリズムでページ置換
- `pin()`でページを固定、`unpin()`で解放、参照カウント管理
- ダーティページの追跡と`flush_all()`での一括書き込み

#### File Managerの実装
- ブロック（ページと同サイズ）単位でファイルアクセス
- `BlockID`でファイル名とブロック番号を管理
- `read()`と`write()`でディスクI/Oを抽象化
- `os.fsync()`で確実にディスクへ書き込み
- ファイルサイズの動的拡張とブロックの追加

#### スロット管理の実装
- 各ページ内でレコードを格納する固定長スロット
- スロットごとにEMPTY/INUSEフラグで使用状態を管理
- `RecordPage`クラスでスロットレベルの操作を提供
- DELETEは論理削除（EMPTYフラグをセット）、物理削除なし
- 新規レコード挿入時は空きスロットを検索して再利用

### 3. データ表現: エンディアン、structモジュール、16進数表現

#### エンディアン処理
- x86アーキテクチャのリトルエンディアン形式でデータ格納
- 整数値の格納例：0x0102（258）→ メモリ上では`02 01`の順序
- 文字列は長さ（4バイト整数）+ UTF-8バイト列で格納
- ページヘッダー、レコードヘッダーもリトルエンディアンで統一

#### structモジュールの活用
```python
# 整数の書き込み（リトルエンディアン）
struct.pack('<i', value)  # '<'がリトルエンディアン指定

# 文字列の書き込み
length = len(string.encode('utf-8'))
struct.pack('<I', length) + string.encode('utf-8')

# 読み込み
value = struct.unpack('<i', buffer[offset:offset+4])[0]
```

#### ヘックスビューワーでの確認
- 実データファイル（.tbl拡張子）を16進数表示
- スロットのEMPTY（00）/INUSE（01）フラグの確認
- 整数値のバイト順序（リトルエンディアン）の視覚的確認
- 文字列の長さプレフィックスとUTF-8エンコーディングの確認

### 4. SQL処理実装: SELECT/INSERT/DELETE文の具体的な実装

#### SELECT文の処理実装
```python
# SELECT id, name FROM users WHERE name = 'Alice'

# 1. Lexerによるトークン分割
tokens = ['SELECT', 'id', ',', 'name', 'FROM', 'users', 'WHERE', 'name', '=', "'Alice'"]

# 2. Parserによる構文解析
def query(self):
    self.lexer.eat_keyword("select")
    field_list = self.select_list()  # ['id', 'name']
    self.lexer.eat_keyword("from")
    table_list = self.table_list()   # ['users']
    predicate = self.predicate()     # name = 'Alice'
    return QueryData(field_list, table_list, predicate)

# 3. Plannerによる実行計画構築
plan = ProjectPlan(
    SelectPlan(
        TablePlan(tx, 'users', metadata_mgr),
        predicate  # WHERE name = 'Alice'
    ),
    field_list  # SELECT id, name
)

# 4. Executorによる実行
scan = plan.open()
while scan.next():
    id_val = scan.get_int('id')
    name_val = scan.get_string('name')
```

#### INSERT文の処理実装
```python
# INSERT INTO users (id, name) VALUES (1, 'Alice')

class BasicUpdatePlanner:
    def execute_insert(self, data: InsertData, tx: Transaction):
        table_name = data.table_name
        plan = TablePlan(tx, table_name, self.mdm)
        scan = plan.open()
        scan.insert()  # 新規スロット確保

        # フィールドに値をセット
        fields = data.fields  # ['id', 'name']
        values = data.values  # [1, 'Alice']

        for field, value in zip(fields, values):
            scan.set_value(field, value)

        scan.close()
        return 1  # 影響を受けたレコード数
```

#### DELETE文の処理実装
```python
# DELETE FROM users WHERE name = 'Bob'

class DeleteScan:
    def delete(self):
        # 現在のスロットを論理削除
        self.record_page.delete(self.current_slot)

class RecordPage:
    def delete(self, slot: int):
        # EMPTYフラグ（0x00）をセット
        flag = self._flag_value(slot)
        flag &= ~INUSE  # INUSEビットをクリア
        self._set_flag(slot, flag)
        # データ自体は残るが、フラグで無効化
```

#### スロットレベルでのデータ操作
```python
# RecordPageクラスの実装
class RecordPage:
    def __init__(self, tx, block, layout):
        self.tx = tx
        self.block = block
        self.layout = layout
        self.tx.pin(block)

    def get_int(self, slot: int, field_name: str) -> int:
        position = self._offset(slot) + self.layout.offset(field_name)
        return self.tx.get_int(self.block, position)

    def set_int(self, slot: int, field_name: str, value: int):
        position = self._offset(slot) + self.layout.offset(field_name)
        self.tx.set_int(self.block, position, value)

    def _offset(self, slot: int) -> int:
        # スロット番号から物理オフセットを計算
        return slot * self.layout.slot_size()
```

### 5. デバッグとトラブルシューティングの実例

#### デバッガーでの実行状態確認
- ASTオブジェクトの階層構造を可視化（QueryData内のフィールド、テーブル、条件式）
- 実行計画の入れ子構造を確認（ProjectPlan → SelectPlan → TablePlan）
- Scanの状態遷移を追跡（current_slot、record_page、buffer状態）

#### ヘックスビューワーでの物理データ確認
```
# users.tbl ファイルの16進数表示
00000000: 01 00 00 00 02 01 00 00  05 00 00 00 41 6C 69 63  |............Alic|
00000010: 65 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |e...............|

# 解釈：
# 01 00 00 00: INUSEフラグ（スロット使用中）
# 02 01 00 00: ID = 258（リトルエンディアン）
# 05 00 00 00: 文字列長 = 5
# 41 6C 69 63 65: "Alice"のUTF-8
```

#### パフォーマンス分析ポイント
- バッファヒット率の測定（pin()の呼び出し回数とディスクI/O回数）
- スキャンの効率性（next()の呼び出し回数と実際に返されたレコード数）
- インデックス使用時と全テーブルスキャンの比較

## 技術的なポイント

### パーサーの実装技術
- **再帰下降パーサ**: 文法規則に従って再帰的にトークンを処理
- **Predicateの構築**: WHERE句の条件式を木構造で表現
- **ANDによる条件連結**: 再帰的なpredicate処理

### スキャンの階層構造
```
ProjectScan（カラム選択）
  └─ SelectScan（WHERE条件）
      └─ TableScan（テーブルアクセス）
```

### トランザクション対応
- 各操作はトランザクション内で実行
- commit()による永続化
- ログマネージャーによる障害回復（今回は詳細説明なし）

## デモンストレーション要素
1. SQL文のステップ実行によるデバッグ表示
2. ASTや実行計画のオブジェクト構造の可視化
3. ヘックスエディタでのデータファイル内容確認
4. エンディアン変換の実例

## 対象者に提供する価値
- RDBMSのブラックボックスを開けて内部動作を理解
- トラブルシューティング時の問題解決能力向上
- データベース最適化の基礎知識習得
- Pythonでの低レベルデータ処理技術の学習

## 実装リポジトリ
GitHub: https://github.com/kei-kmj/KeiPyDB

## 使用技術
- Python（標準ライブラリのみ）
- structモジュール（バイナリ変換）
- osモジュール（ファイルシステム操作）
- ヘックスビューワー（データ可視化）