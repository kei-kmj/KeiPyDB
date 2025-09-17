from db.metadata.stat_info import StatInfo


def test_blocks_accessed_returns_correct_value():
    stat = StatInfo(num_blocks=10, num_records=30)
    assert stat.blocks_accessed() == 10


def test_records_output_returns_correct_value():
    stat = StatInfo(num_blocks=5, num_records=25)
    assert stat.records_output() == 25


def test_distinct_values_returns_expected_result():
    stat = StatInfo(num_blocks=8, num_records=30)
    expected = 1 + (30 // StatInfo.ESTIMATED_VALUE)
    assert stat.distinct_values() == expected


def test_distinct_values_returns_minimum_one():
    stat = StatInfo(num_blocks=0, num_records=0)
    assert stat.distinct_values() == 1
