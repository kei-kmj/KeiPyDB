from db.query.constant import Constant


class DirectoryEntry:

    def __init__(self, data_value: Constant, block_number: int) -> None:
        self.data_value = data_value
        self.block_number = block_number
