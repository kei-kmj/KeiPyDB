from db.parse.create_index import CreateIndex
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.delete_data import DeleteData
from db.parse.insert_data import InsertData
from db.parse.modify_data import ModifyData
from db.parse.parser import Parser
from db.plan.plan import Plan
from db.plan.query_planner import QueryPlanner
from db.plan.update_planner import UpdatePlanner
from db.transaction.transaction import Transaction


class Planner:

    def __init__(self, query_planner: QueryPlanner, update_planner: UpdatePlanner):
        self.query_planner = query_planner
        self.update_planner = update_planner

    def create_query_plan(self, query: str, transaction: Transaction) -> Plan:
        """クエリを実行するための計画を作成する"""
        parser = Parser(query)
        data = parser.query()

        self.verify_query()

        return self.query_planner.create_plan(data, transaction)

    def execute_update(self, command: str, transaction: Transaction) -> int:
        """更新コマンドを実行する"""
        parser = Parser(command)
        data = parser.update_command()
        self.verify_update()

        if isinstance(data, InsertData):
            return self.update_planner.execute_insert(data, transaction)
        elif isinstance(data, DeleteData):
            return self.update_planner.execute_delete(data, transaction)
        elif isinstance(data, ModifyData):
            return self.update_planner.execute_modify(data, transaction)
        elif isinstance(data, CreateTable):
            return self.update_planner.execute_create_table(data, transaction)
        elif isinstance(data, CreateView):
            return self.update_planner.execute_create_view(data, transaction)
        elif isinstance(data, CreateIndex):
            return self.update_planner.execute_create_index(data, transaction)
        else:
            return 0

    def verify_query(self) -> None:
        pass

    def verify_update(self) -> None:
        pass
