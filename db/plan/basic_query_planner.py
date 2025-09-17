from abc import ABC

from db.metadata.metadata_manager import MetadataManager
from db.parse.parser import Parser
from db.parse.query_data import QueryData
from db.plan.plan import Plan
from db.plan.product_plan import ProductPlan
from db.plan.project_plan import ProjectPlan
from db.plan.query_planner import QueryPlanner
from db.plan.select_plan import SelectPlan
from db.plan.table_plan import TablePlan
from db.transaction.transaction import Transaction


class BasicQueryPlanner(QueryPlanner, ABC):

    def __init__(self, metadata_manager: MetadataManager):
        self.metadata_manager = metadata_manager

    def create_plan(self, query_data: QueryData, transaction: Transaction) -> Plan:

        plan_list: list[Plan] = []
        for table_name in query_data.tables:

            view_def = self.metadata_manager.get_view_definition(table_name, transaction)
            if view_def:

                parser = Parser(view_def)

                view_query = parser.query()
                plan_list.append(self.create_plan(view_query, transaction))
            else:

                plan_list.append(TablePlan(transaction, table_name, self.metadata_manager))

        plan = plan_list.pop(0)

        for next_plan in plan_list:
            plan = ProductPlan(plan, next_plan)

        plan = SelectPlan(plan, query_data.get_predicate())

        fields = query_data.get_fields()

        plan = ProjectPlan(plan, fields)

        return plan
