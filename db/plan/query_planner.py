from abc import ABC, abstractmethod

from db.parse.query_data import QueryData
from db.plan.plan import Plan
from db.transaction.transaction import Transaction


class QueryPlanner(ABC):

    @abstractmethod
    def create_plan(self, query_data: QueryData, transaction: Transaction) -> Plan:
        pass
