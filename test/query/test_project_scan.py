from unittest.mock import Mock

from db.query.project_scan import ProjectScan
from db.query.scan import Scan


def test_プロジェクトスキャンがフィールドリスト内の整数値を取得する():

    mock_scan = Mock(spec=Scan)
    mock_scan.get_int.return_value = 42
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.get_int("field1")

    assert result == 42
    mock_scan.get_int.assert_called_once_with("field1")


def test_プロジェクトスキャンがフィールドリスト外の整数値取得で例外を発生させる():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    try:
        project_scan.get_int("field3")
        assert False
    except RuntimeError as e:
        assert str(e) == "field 'field3' not in field_list"
        mock_scan.get_int.assert_not_called()


def test_プロジェクトスキャンがフィールドリスト内の文字列を取得する():

    mock_scan = Mock(spec=Scan)
    mock_scan.get_string.return_value = "42"
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.get_string("field1")

    assert result == "42"
    mock_scan.get_string.assert_called_once_with("field1")


def test_プロジェクトスキャンがフィールドリスト外の文字列取得で例外を発生させる():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    try:
        project_scan.get_string("field3")
        assert False
    except RuntimeError as e:
        assert str(e) == "field 'field3' not in field_list"
        mock_scan.get_string.assert_not_called()


def test_プロジェクトスキャンがフィールドリスト内の値を取得する():

    mock_scan = Mock(spec=Scan)
    mock_scan.get_value.return_value = "42"
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.get_value("field1")

    assert result == "42"
    mock_scan.get_value.assert_called_once_with("field1")


def test_プロジェクトスキャンがフィールドリスト外の値取得で例外を発生させる():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    try:
        project_scan.get_value("field3")
        assert False
    except RuntimeError as e:
        assert str(e) == "field 'field3' not in field_list"
        mock_scan.get_value.assert_not_called()


def test_プロジェクトスキャンが指定されたフィールドを持つか確認する():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.has_field("field1")

    assert result is True


def test_プロジェクトスキャンが基になるスキャンを閉じる():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    project_scan.close()

    mock_scan.close.assert_called_once()


def test_プロジェクトスキャンがスキャンを最初に戻す():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    project_scan.before_first()

    mock_scan.before_first.assert_called_once()


def test_プロジェクトスキャンが次のレコードに進む():

    mock_scan = Mock(spec=Scan)
    mock_scan.next.return_value = True
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.next()

    assert result is True
    mock_scan.next.assert_called_once()
