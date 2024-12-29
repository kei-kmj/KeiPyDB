from db.parse.query_data import QueryData


class CreateView:
    def __init__(self, view_name: str, query: QueryData) -> None:
        self.view_name = view_name
        self.query = query

    def get_view_name(self) -> str:
        return self.view_name

    def get_query(self) -> str:
        return self.query.__str__()
