class BlockID:
    def __init__(self, file_name: str, block_number: int):
        """ファイル名とブロック番号を指定してBlockIDを初期化
        :param file_name: ファイル名
        :param block_number: ブロック番号
        """
        self.file_name = file_name
        self.block_number = block_number

    # TODO: 後で、仮引数名を見直す
    def __eq__(self, target_block: object) -> bool:
        """BlockIDが等しいかどうかを判定
        :param target_block: 比較対象のBlockID
        """
        if not isinstance(target_block, BlockID):
            return NotImplemented
        return self.file_name == target_block.file_name and self.block_number == target_block.block_number

    def __str__(self) -> str:
        """BlockIDを文字列に変換"""
        return f"[{self.file_name}, block {self.block_number}]"

    def __hash__(self) -> int:
        """__str__の結果をもとにハッシュ値を生成する"""
        return hash((self.file_name, self.block_number))
