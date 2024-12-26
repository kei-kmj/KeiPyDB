from unittest.mock import Mock

from db.buffer.buffer import Buffer
from db.file.block_id import BlockID
from db.transaction.transaction import Transaction


def test_トランザクションのコミットが正しく動作することを確認する():
    # Given
    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    recovery_manager = Mock()
    transaction.recovery_manager = recovery_manager
    concurrency_manager = Mock()
    transaction.concurrency_manager = concurrency_manager
    buffer_list = Mock()
    transaction.buffer_list = buffer_list

    # When
    transaction.commit()

    # Then
    recovery_manager.commit.assert_called_once()
    concurrency_manager.release.assert_called_once()
    buffer_list.unpin_all.assert_called_once()
    print(f"Transaction {transaction.tx_number} committed")


def test_トランザクションのロールバックが正しく動作することを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    recovery_manager = Mock()
    transaction.recovery_manager = recovery_manager
    concurrency_manager = Mock()
    transaction.concurrency_manager = concurrency_manager
    buffer_list = Mock()
    transaction.buffer_list = buffer_list

    transaction.rollback()

    recovery_manager.rollback.assert_called_once()
    concurrency_manager.release.assert_called_once()
    buffer_list.unpin_all.assert_called_once()
    print(f"Transaction {transaction.tx_number} rolled back")


def test_指定したブロックをピンできることを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer_list = Mock()
    transaction.buffer_list = buffer_list
    block = BlockID("test", 1)

    transaction.pin(block)

    buffer_list.pin.assert_called_once_with(block)


def test_指定したブロックをアンピンできることを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer_list = Mock()
    transaction.buffer_list = buffer_list
    block = BlockID("test", 1)

    transaction.unpin(block)

    buffer_list.unpin.assert_called_once_with(block)


def test_指定したブロックの指定したオフセットの整数値を取得できるこを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer = Mock(spec=Buffer)
    buffer.get_int = Mock(return_value=0)
    buffer.contents = Mock()
    buffer.contents.get_int = Mock(return_value=0)
    buffer_manager.pin = Mock(return_value=buffer)
    block = BlockID("test", 1)
    offset = 1

    actual = transaction.get_int(block, offset)

    assert actual == 0
    buffer_manager.pin.assert_called_once_with(block)


def test_指定したブロックの指定したオフセットの文字列を取得できることを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer = Mock(spec=Buffer)
    buffer.get_int = Mock(return_value=0)
    buffer.contents = Mock()
    buffer.contents.get_string = Mock(return_value="")
    buffer_manager.pin = Mock(return_value=buffer)
    block = BlockID("test", 1)
    offset = 1

    actual = transaction.get_string(block, offset)

    assert actual == ""
    buffer_manager.pin.assert_called_once_with(block)


def test_共有ロックと排他ロックが正しく動作することを確認():
    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    another_transaction = Transaction(file_manager, log_manager, buffer_manager)

    block = BlockID("shared_block", 1)

    transaction.concurrency_manager.lock_shared(block)
    another_transaction.concurrency_manager.lock_shared(block)

    transaction.concurrency_manager.lock_exclusive(block)
    transaction.concurrency_manager.lock_shared(block)

    # 他のトランザクションが共有ロックを取得しているため、排他ロックは取得できない
    assert transaction.concurrency_manager.lock_shared(block) is None
    assert another_transaction.concurrency_manager.lock_shared(block) is None
    # 他のトランザクションが排他ロックを取得しているため、排他ロックは取得できない
    assert another_transaction.concurrency_manager.lock_exclusive(block) is None
