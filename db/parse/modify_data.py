from db.query.expression import Expression


class ModifyData:

    def __init__(self, table_name: str, field_name: str, new_value: Expression, predicate: Expression) -> None:
        self.table_name = table_name
        self.field_name = field_name
        self.new_value = new_value
        self.predicate = predicate

    def get_table_name(self) -> str:
        return self.table_name

    def get_field_name(self) -> str:
        return self.field_name

    def get_new_value(self) -> Expression:
        return self.new_value

    def get_predicate(self) -> Expression:
        return self.predicate
