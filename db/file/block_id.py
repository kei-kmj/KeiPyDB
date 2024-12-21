class BlockID:
    def __init__(self, file_name, block_number):
        """ファイル名とブロック番号を指定してBlockIDを初期化
        :param file_name: ファイル名
        :param block_number: ブロック番号
        """
        self.file_name = file_name
        self.block_number = block_number

    # TODO: 後で、仮引数名を見直す
    def __eq__(self, target_block):
        """BlockIDが等しいかどうかを判定
        :param target_block: 比較対象のBlockID
        """
        return self.file_name == target_block.file_name and self.block_number == target_block.block_number


    def __str__(self):
        """BlockIDを文字列に変換
        """
        return f"[{self.file_name}, block {self.block_number}]"