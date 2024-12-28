from unittest.mock import Mock

from db.query.product_scan import ProductScan


def test_直積スキャンが最初のレコードに戻ることを確認する():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    product_scan.before_first()

    left_scan.before_first.assert_any_call()
    right_scan.before_first.assert_any_call()


def test_直積スキャンが次のレコードに進むことを確認する():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    result = product_scan.next()

    assert result is True


def test_指定されたフィールドの整数値を取得できることを確認する():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    result = product_scan.get_int("field1")

    assert result == left_scan.get_int.return_value


def test_指定されたフィールドの文字列値を取得できることを確認する():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    result = product_scan.get_string("field1")

    assert result == left_scan.get_string.return_value


def test_指定されたフィールドが存在することを確認する():
    left_scan = Mock()
    right_scan = Mock()

    left_scan.has_field.return_value = True
    right_scan.has_field.return_value = False

    product_scan = ProductScan(left_scan, right_scan)

    assert product_scan.has_field("test_field") is True


def test_両方のスキャンをクローズできることを確認する():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.close()

    left_scan.close.assert_any_call()
    right_scan.close.assert_any_call()
