from db.file.block_id import BlockID
from db.file.page import Page


class PlintLogFile:
    def __init__(self, db_name:str, block_size:int, log_buffer_size: int) -> None:

        #
        self.db = KeiPyDB(db_name, block_size, log_buffer_size)
        self.file_manager = self.db.file_manager
        self.log_manager = self.db.log_manager


    def read_and_print_log_file(self, file_name:str) -> None:
        """ログファイルを読み込んで内容を表示"""

        # ログファイルの最後のブロックを取得
        last_block = self.file_manager.length(file_name) -1
        block = BlockID(file_name, last_block)

        # ページの読み込み
        page = Page(self.file_manager.block_size)
        self.file_manager.read(block, page)

        # ログ内容を出力
        for bytes_data in self.log_manager.iterator():
            # TODO: ログレコードの作成
            log_record = ""
            # log_record = LogRecord.Create_log_record(bytes_data)
            print(log_record)
