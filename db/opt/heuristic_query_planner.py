from abc import ABC
from collections import deque
from typing import Optional

from db.metadata.metadata_manager import MetadataManager
from db.opt.table_planner import TablePlanner
from db.parse.query_data import QueryData
from db.plan.plan import Plan
from db.plan.planner import Planner
from db.plan.project_plan import ProjectPlan
from db.plan.query_planner import QueryPlanner
from db.transaction.transaction import Transaction


class HeuristicQueryPlanner(QueryPlanner, ABC):
    def __init__(self, metadata_manager: MetadataManager) -> None:
        self.metadata_manager = metadata_manager
        self.table_planners: deque[TablePlanner] = deque()

    def create_plan(self, query_data: QueryData, transaction: Transaction) -> Plan:

        for table_name in query_data.get_tables():
            table_planner = TablePlanner(table_name, query_data.get_predicate(), transaction, self.metadata_manager)
            self.table_planners.append(table_planner)

        current_plan = self._get_lowest_select_plan()

        while self.table_planners:
            best_join_plan = self._get_lowest_join_plan(current_plan)

            if best_join_plan:
                current_plan = best_join_plan
            else:
                current_plan = self._get_lowest_product_plan(current_plan)

        return ProjectPlan(current_plan, query_data.get_fields())

    def _get_lowest_select_plan(self) -> Plan:

        best_table_planner = None
        best_plan = None

        for table_planner in self.table_planners:
            select_plan = table_planner.make_select_plan()

            if best_plan is None or select_plan.records_output() < best_plan.records_output():
                best_table_planner = table_planner
                best_plan = select_plan

        if best_table_planner:
            self.table_planners.remove(best_table_planner)

        if not best_plan:
            raise ValueError("No suitable select plan found")

        return best_plan

    def _get_lowest_join_plan(self, current_plan: Plan) -> Optional[Plan]:
        best_table_planner = None
        best_plan = None

        for table_planner in self.table_planners:
            join_plan = table_planner.make_join_plan(current_plan)

            if join_plan and (best_plan is None or join_plan.records_output() < best_plan.records_output()):
                best_table_planner = table_planner
                best_plan = join_plan

        if best_table_planner:
            self.table_planners.remove(best_table_planner)

        return best_plan

    def _get_lowest_product_plan(self, current_plan: Plan) -> Plan:
        best_table_planner = None
        best_plan = None

        for table_planner in self.table_planners:
            product_plan = table_planner.make_product_plan(current_plan)

            if best_plan is None or product_plan.records_output() < best_plan.records_output():
                best_table_planner = table_planner
                best_plan = product_plan

        if best_table_planner:
            self.table_planners.remove(best_table_planner)

        if not best_plan:
            raise ValueError("No suitable product plan found")

        return best_plan

    def set_planner(self, planner: Planner) -> None:
        pass
