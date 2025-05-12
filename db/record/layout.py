from typing import Dict, Optional

from db.constants import ByteSize, FieldType
from db.file.page import Page
from db.record.schema import Schema


class Layout:
    def __init__(
        self, schema: Schema, offsets: Optional[Dict[str, int]] = None, slot_size: Optional[int] = None
    ) -> None:

        self.schema = schema
        if offsets is None or slot_size is None:
            self.offsets = {}
            position = ByteSize.Int

            for field_name in schema.get_fields():
                self.offsets[field_name] = position
                position += self._length_in_bytes(field_name)

            self.slot_size = position
        else:
            self.offsets = offsets
            self.slot_size = slot_size

    def get_schema(self) -> Schema:
        """テーブルのスキーマを返す"""
        return self.schema

    def get_offset(self, field_name: str) -> int:
        """指定されたフィールドのオフセットを返す"""
        if field_name not in self.offsets:
            raise ValueError(f"Unknown field name {field_name}")
        return self.offsets[field_name]

    def get_slot_size(self) -> int:
        """スロットのサイズを返す"""
        return self.slot_size

    def _length_in_bytes(self, field_name: str) -> int:
        """指定されたフィールドが必要とするバイト数を返す"""

        field_type = self.schema.get_type(field_name)

        if field_type == FieldType.Integer:
            return ByteSize.Int
        elif field_type == FieldType.Varchar:
            return Page.get_max_length(self.schema.get_length(field_name))
        else:
            raise ValueError(f"Unknown field type {field_type}")
