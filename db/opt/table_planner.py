from typing import Dict, Optional

from db.index.planner.index_join_plan import IndexJoinPlan
from db.index.planner.index_select_plan import IndexSelectPlan
from db.metadata.index_info import IndexInfo
from db.metadata.metadata_manager import MetadataManager
from db.multi_buffer.multi_buffer_product_plan import MultiBufferProductPlan
from db.plan.plan import Plan
from db.plan.select_plan import SelectPlan
from db.plan.table_plan import TablePlan
from db.query.predicate import Predicate
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class TablePlanner:

    def __init__(
        self, table_name: str, predicate: Predicate, transaction: Transaction, metadata_manager: MetadataManager
    ) -> None:
        self.predicate = predicate
        self.transaction = transaction
        self.my_plan = TablePlan(transaction, table_name, metadata_manager)
        self.my_schema = self.my_plan.schema()
        self.indexes: Dict[str, IndexInfo] = metadata_manager.get_index_info(table_name, transaction)

    def make_select_plan(self) -> Plan:
        plan = self._make_index_select()
        if plan is None:
            return self.my_plan
        return self._add_select_predicate(plan)

    def make_join_plan(self, current: Plan) -> Optional[Plan]:
        current_schema = current.schema()
        join_predicate = self.predicate.join_sub_predicate(self.my_schema, current_schema)

        if join_predicate is None:
            return None

        plan = self._make_index_join(current, current_schema)
        if plan is None:
            plan = self._make_product_join(current, current_schema)

        return plan

    def make_product_plan(self, current: Plan) -> Plan:
        plan = self._add_select_predicate(self.my_plan)

        return MultiBufferProductPlan(self.transaction, current, plan)

    def _make_index_select(self) -> Optional[Plan]:
        for filed_name, index_info in self.indexes.items():
            value = self.predicate.equates_with_constant(filed_name)

            if value is not None:
                print(f"Index on {filed_name} used")
                return IndexSelectPlan(self.my_plan, index_info, value)

        return None

    def _make_index_join(self, current: Plan, current_schema: Schema) -> Optional[Plan]:

        for field_name, index_info in self.indexes.items():
            outer_field = self.predicate.equates_with_field(field_name)
            if outer_field is not None and current_schema.has_field(outer_field):
                plan = IndexJoinPlan(current, self.my_plan, index_info, outer_field)
                predicate_plan = self._add_select_predicate(plan)

                return self._add_join_predicate(predicate_plan, current_schema)

        return None

    def _make_product_join(self, current: Plan, current_schema: Schema) -> Plan:
        product_plan = self.make_product_plan(current)
        return self._add_join_predicate(product_plan, current_schema)

    def _add_select_predicate(self, plan: Plan) -> Plan:
        select_predicate = self.predicate.select_sub_predicate(self.my_schema)

        if select_predicate is not None:
            return SelectPlan(plan, select_predicate)

        return plan

    def _add_join_predicate(self, plan: Plan, current_schema: Schema) -> Plan:
        join_predicate = self.predicate.join_sub_predicate(self.my_schema, current_schema)

        if join_predicate is not None:
            return SelectPlan(plan, join_predicate)

        return plan
