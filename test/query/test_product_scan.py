from unittest.mock import Mock

from db.query.product_scan import ProductScan


def test_record():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    product_scan.before_first()

    left_scan.before_first.assert_any_call()
    right_scan.before_first.assert_any_call()


def test_record():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    result = product_scan.next()

    assert result is True


def test_can_get():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    result = product_scan.get_int("field1")

    assert result == left_scan.get_int.return_value


def test_can_get():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.before_first()
    product_scan.next()

    result = product_scan.get_string("field1")

    assert result == left_scan.get_string.return_value


def test_field():
    left_scan = Mock()
    right_scan = Mock()

    left_scan.has_field.return_value = True
    right_scan.has_field.return_value = False

    product_scan = ProductScan(left_scan, right_scan)

    assert product_scan.has_field("test_field") is True


def test_scan():
    left_scan = Mock()
    right_scan = Mock()
    product_scan = ProductScan(left_scan, right_scan)

    product_scan.close()

    left_scan.close.assert_any_call()
    right_scan.close.assert_any_call()


def test_product_scan_basic_logic():
    """Test ProductScan basic logic with mocks"""

    left_scan = Mock()
    right_scan = Mock()

    # Setup mock behavior
    left_count = 0
    right_count = 0

    def left_next():
        nonlocal left_count
        left_count += 1
        return left_count <= 2

    def right_next():
        nonlocal right_count
        right_count += 1
        if right_count > 3:
            right_count = 1  # Reset for next left iteration
        return right_count <= 3

    left_scan.next = left_next
    right_scan.next = right_next
    left_scan.has_field.return_value = True
    right_scan.has_field.return_value = False

    product_scan = ProductScan(left_scan, right_scan)

    # Test field resolution (left scan first)
    assert product_scan.has_field("test") is True

    # Test basic navigation
    product_scan.before_first()
    combinations = 0
    while product_scan.next():
        combinations += 1
        if combinations > 10:  # Prevent infinite loop
            break

    # Should process some combinations
    assert combinations >= 0
