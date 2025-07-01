from unittest.mock import Mock

from db.query.project_scan import ProjectScan
from db.query.scan import Scan


def test_project_scan_gets_integer_values_from_field_list():

    mock_scan = Mock(spec=Scan)
    mock_scan.get_int.return_value = 42
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.get_int("field1")

    assert result == 42
    mock_scan.get_int.assert_called_once_with("field1")


def test_project_scan_raises_exception_for_integer_values_outside_field_list():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    try:
        project_scan.get_int("field3")
        assert False
    except RuntimeError as e:
        assert str(e) == "field 'field3' not in field_list"
        mock_scan.get_int.assert_not_called()


def test_project_scan_gets_string_values_from_field_list():

    mock_scan = Mock(spec=Scan)
    mock_scan.get_string.return_value = "42"
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.get_string("field1")

    assert result == "42"
    mock_scan.get_string.assert_called_once_with("field1")


def test_project_scan_raises_exception_for_string_values_outside_field_list():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    try:
        project_scan.get_string("field3")
        assert False
    except RuntimeError as e:
        assert str(e) == "field 'field3' not in field_list"
        mock_scan.get_string.assert_not_called()


def test_project_scan_gets_values_from_field_list():

    mock_scan = Mock(spec=Scan)
    mock_scan.get_value.return_value = "42"
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.get_value("field1")

    assert result == "42"
    mock_scan.get_value.assert_called_once_with("field1")


def test_project_scan_raises_exception_for_values_outside_field_list():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    try:
        project_scan.get_value("field3")
        assert False
    except RuntimeError as e:
        assert str(e) == "field 'field3' not in field_list"
        mock_scan.get_value.assert_not_called()


def test_project_scan_checks_if_it_has_specified_field():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.has_field("field1")

    assert result is True


def test_project_scan_closes_underlying_scan():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    project_scan.close()

    mock_scan.close.assert_called_once()


def test_project_scan_resets_scan_to_beginning():

    mock_scan = Mock(spec=Scan)
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    project_scan.before_first()

    mock_scan.before_first.assert_called_once()


def test_project_scan_advances_to_next_record():

    mock_scan = Mock(spec=Scan)
    mock_scan.next.return_value = True
    field_list = ["field1", "field2"]
    project_scan = ProjectScan(mock_scan, field_list)

    result = project_scan.next()

    assert result is True
    mock_scan.next.assert_called_once()
