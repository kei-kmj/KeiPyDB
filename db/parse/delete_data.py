from db.query.predicate import Predicate


class DeleteData:
    def __init__(self, table_name: str, predicate: Predicate) -> None:
        self.table_name = table_name
        self.predicate = predicate

    def get_table_name(self) -> str:
        return self.table_name

    def get_predicate(self) -> Predicate:
        return self.predicate
