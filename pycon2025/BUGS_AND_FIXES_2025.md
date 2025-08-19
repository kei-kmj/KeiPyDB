# KeiPyDB バグ修正履歴 (2025年)

このドキュメントは、2025年にKeiPyDBで発見・修正されたバグの詳細をまとめたものです。

## 重要：アプリケーションクラッシュの主要原因

アプリケーションのクラッシュは主に以下の2つのバグが原因でした：

### 1. field_catalogへのテーブル名書き込み失敗（バグ #8）
- テーブル作成時にメタデータが正しく記録されない
- テーブル情報の取得時にNullPointerExceptionやValueErrorが発生
- データベースの基本的な操作（SELECT、INSERT等）が失敗

### 2. 無限ループによるハング（バグ #9）
- レコード挿入時に無限ループに陥る
- バッファマネージャーのピン管理で無限待機
- スロット検索アルゴリズムの終了条件不備

## 1. BlockIDの負の値バグ (2025年6月21日修正)

### 問題
- **コミット**: d8866f7 (Block number must be non-negative)
- **影響範囲**: `db/file/block_id.py`, `db/buffer/buffer.py`, `db/transaction/transaction.py`

### 詳細
BlockIDのブロック番号に負の値が設定される可能性があり、ファイルシステムの操作で予期しない動作を引き起こしていました。

### 修正内容
1. `BlockID`クラスのコンストラクタで負の値チェックを追加
2. `Buffer`クラスの初期化でBlockIDを`None`に変更（従来は`BlockID("", -1)`）
3. トランザクション処理でのnullチェックを追加

```python
# block_id.py
if block_number < 0:
    raise ValueError(f"Block number must be non-negative: {block_number}")
```

## 2. FileManagerのスレッドセーフティ問題 (2025年6月21日修正)

### 問題
- **コミット**: 2413a8b (fix file module)
- **影響範囲**: `db/file/file_manager.py`, `db/file/page.py`

### 詳細
複数スレッドから同時にファイルアクセスが発生した場合、データの整合性が保証されない問題がありました。

### 修正内容
1. `FileManager`にスレッドセーフなロック機構を追加
2. ファイル単位のロック（`_file_locks`）を実装
3. `Page.get_contents()`の戻り値を`bytearray`から`bytes`に変更（不変性の確保）

```python
# file_manager.py
self._lock = threading.RLock()
self._file_locks: Dict[str, threading.RLock] = {}
```

## 3. ファイルモジュールのリファクタリング (2025年7月1日)

### 問題
- **コミット**: ce5f5cc (refactor file module)
- **影響範囲**: 多数のテストファイル、バッファ管理

### 詳細
テストの安定性向上とコードの保守性改善のための大規模リファクタリング。

### 修正内容
1. バッファ管理の改善（`buffer.py`, `buffer_manager.py`）
2. テストファイルの整理と新規テストの追加
3. pytest設定の最適化（`pytest.ini`の追加）

## 4. インデックスモジュールの修正 (2025年7月5日)

### 問題
- **コミット**: 6288212 (fix index module)
- **影響範囲**: `db/index/hash/hash_index.py`, `db/metadata/*`

### 詳細
インデックス作成時のメタデータ管理に不整合が発生する問題がありました。

### 修正内容
1. `HashIndex`のエラーハンドリング改善
2. `IndexInfo`のデータ構造修正
3. `IndexManager`のトランザクション処理改善
4. `StatManager`の統計情報更新ロジック修正

## 5. ログモジュールの修正 (2025年7月6日)

### 問題
- **コミット**: e794356 (fix log module)
- **影響範囲**: `db/log/log_manager.py`, `db/transaction/recovery/*`

### 詳細
ログレコードのタイムスタンプ処理に不具合があり、リカバリ時に問題が発生していました。

### 修正内容
1. `LogManager`にタイムスタンプ検証を追加
2. 各種リカバリレコード（commit, rollback, start等）のタイムスタンプ処理を統一

## 6. プランモジュールの修正 (2025年7月6日)

### 問題
- **コミット**: 5c07e49 (fix plan module)
- **影響範囲**: `db/parse/lexer.py`, `db/parse/parser.py`, `db/plan/basic_update_planner.py`

### 詳細
SQL文の解析とクエリプラン生成で例外処理が不適切でした。

### 修正内容
1. `bad_syntax_exception.py`を`exception.py`にリネーム・統合
2. Lexerのトークン処理改善（34行の修正）
3. Parserのエラーハンドリング強化（36行の修正）
4. `BasicUpdatePlanner`にエラーチェック追加

## 7. テストの修正 (2025年7月8日)

### 問題
- **コミット**: 8bd27db (fix test)
- **影響範囲**: 多数のテストファイルとプロダクションコード

### 詳細
テストコードとプロダクションコードの不整合により、テストが失敗していました。

### 修正内容
1. `ProductPlan`のロジック修正（34行の変更）
2. `ProductScan`の最適化（41行の変更）
3. `Predicate`と`Term`のequals/hashCode実装改善
4. 多数のテストケースの修正・削除（約8,700行の削減）

## 8. field_catalogバグ (2025年5月7日) - クラッシュ原因1

### 問題
- **コミット**: ce28a0b (field_catalogにテーブル名が書き込まれないバグの修正)
- **影響範囲**: メタデータ管理全般
- **症状**: テーブル作成は成功するが、その後のテーブル操作（SELECT、INSERT等）で失敗

### 詳細
テーブル作成時にfield_catalogにテーブル名が正しく記録されない問題がありました。これにより、テーブルのスキーマ情報が取得できず、以下のエラーが発生：
- `ValueError: View {table_name} not found`
- テーブルが存在しないというエラー
- NullPointerExceptionによるクラッシュ

### 根本原因
1. **Parserの問題**: field_listの解析時に再帰的に`select_list()`を呼び出していた
2. **スキーマ構築の問題**: 複数フィールドの定義が正しく処理されない
3. **トランザクションコミットの欠如**: カタログテーブル作成後にコミットしていない

### 修正内容
```python
# parser.py - field_listの修正
def select_list(self) -> Collection[str]:
    field_list = [self.filed()]
    while self.lexer.match_delimiter(","):
        self.lexer.eat_delimiter(",")
        field_list.append(self.filed())  # 修正: extend → append
    return field_list

# table_manager.py - トランザクションコミット追加
if is_new:
    self.create_table("table_catalog", table_catalog_schema, transaction)
    self.create_table("field_catalog", field_catalog_schema, transaction)
    transaction.commit()  # 追加: カタログテーブルを確実に永続化
```

## 9. 無限ループバグ (2025年5月11日) - クラッシュ原因2

### 問題
- **コミット**: 33ff1bc (無限ループの解消)
- **影響範囲**: `db/buffer/*`, `db/record/*`
- **症状**: INSERT操作時にアプリケーションがハング、レスポンスが返らない

### 詳細
特定の条件下でバッファ管理とレコードスキャンが無限ループに陥る問題がありました。

### 根本原因

#### 1. RecordPageの無限ループ
```python
# record_page.py - 修正前
def _is_valid_slot(self, slot: int) -> bool:
    return self._offset(slot + 1) <= self.transaction.block_size()
    # 問題: slot + 1のオフセットが常に有効になる可能性

# 修正後
def _is_valid_slot(self, slot: int) -> bool:
    return self._offset(slot + 1) < self.transaction.block_size()
    # 修正: <= を < に変更して境界条件を正確に
```

#### 2. TableScanのinsertメソッドの致命的バグ
```python
# table_scan.py - 修正前の問題のあるコード
def insert(self) -> None:
    while True:
        slot = self.record_page.insert_after(self.current_slot)
        if slot is not None and slot >= 0:
            self.current_slot = slot
            return
        # ブロック移動処理...
        self.current_slot = slot  # バグ: slotはNoneまたは-1
        # 次のループでinsert_after(None/-1)が呼ばれて不正な動作

# 修正後
def insert(self) -> None:
    self.current_slot = self.record_page.insert_after(self.current_slot)
    
    while self.current_slot is None or self.current_slot < 0:
        # ブロック移動処理...
        self.current_slot = self.record_page.insert_after(self.current_slot)
```

#### 3. BufferManagerの無限待機
```python
# buffer_manager.py - 修正
while buffer is None and not self._waiting_too_long(time_stamp):
    try:
        self.condition.wait(self.MAX_TIME)
        buffer = self._try_to_pin(block)
    except KeyboardInterrupt:
        raise BufferAbortException()  # 追加: 無限待機から脱出可能に
```

### 修正内容
1. `RecordPage._is_valid_slot`の境界条件修正
2. `TableScan.insert`の状態管理ロジック全面改修
3. `BufferManager`に割り込み処理追加
4. デバッグ出力の追加（問題の特定用）

## まとめ

2025年に修正された主要なバグは以下のカテゴリに分類されます：

1. **データ整合性**: BlockIDの負値、field_catalog書き込み問題
2. **並行性制御**: FileManagerのスレッドセーフティ、共有ロック処理
3. **パフォーマンス**: 無限ループ、ProductScanの最適化
4. **エラーハンドリング**: 例外処理の統一、ログモジュールの改善
5. **テスト品質**: 大規模なテストリファクタリング（8,700行削減）

これらの修正により、KeiPyDBの安定性と性能が大幅に向上しました。