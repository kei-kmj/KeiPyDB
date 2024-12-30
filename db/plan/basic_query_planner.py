from abc import ABC
from typing import List

from db.parse.parser import Parser
from db.parse.query_data import QueryData
from db.plan.plan import Plan
from db.plan.query_planner import QueryPlanner
from db.plan.table_plan import TablePlan
from db.transaction.transaction import Transaction


class BasicQueryPlanner(QueryPlanner, ABC):

    def __init__(self, metadata_manager):
        self.metadata_manager = metadata_manager

    def create_plan(self, query_data: QueryData, transaction:Transaction) -> Plan:

        plans: List[Plan] = []
        for table_name in query_data.tables:
            view_def = self.metadata_manager.get_view_definition(table_name, transaction)
            if view_def is not None:
                parser = Parser(view_def)
                view_query_data = parser.query()
                plans.append(self.create_plan(view_query_data, transaction))
            else:
                plans.append(TablePlan(transaction, table_name, self.metadata_manager))


