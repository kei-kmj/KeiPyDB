from abc import ABC
from typing import List

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


class BetterQueryPlanner(QueryPlanner, ABC):

    def __init__(self, metadata_manager: MetadataManager):
        self.metadata_manager = metadata_manager

    def create_plan(self, query_data: QueryData, transaction: Transaction) -> Plan:

        # Step 1: Create a plan for each mentioned table or view.
        plan_list: List[Plan] = []
        for table_name in query_data.tables:
            view_def = self.metadata_manager.get_view_definition(table_name, transaction)
            if view_def is not None:
                parser = Parser(view_def)

                view_query = parser.query()
                plan_list.append(self.create_plan(view_query, transaction))
            else:
                plan_list.append(TablePlan(transaction, table_name, self.metadata_manager))

        # Step 2: Create the product of all table plans.
        plan = plan_list.pop(0)

        for next_plan in plan_list:
            choice_first = ProductPlan(next_plan, plan)
            choice_second = ProductPlan(plan, next_plan)

            if choice_first.blocks_accessed() < choice_second.blocks_accessed():
                plan = choice_first
            else:
                plan = choice_second

        # Step 3: Add a selection plan for the predicate.
        plan = SelectPlan(plan, query_data.get_predicate())

        # Step 4: Project on the field names.

        plan = ProjectPlan(plan, query_data.get_fields())

        return plan
