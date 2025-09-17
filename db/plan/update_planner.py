from abc import ABC, abstractmethod

from db.parse.create_index import CreateIndex
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.delete_data import DeleteData
from db.parse.insert_data import InsertData
from db.parse.modify_data import ModifyData
from db.transaction.transaction import Transaction


class UpdatePlanner(ABC):

    @abstractmethod
    def execute_insert(self, data: InsertData, transaction: Transaction) -> int:
        pass

    @abstractmethod
    def execute_delete(self, data: DeleteData, transaction: Transaction) -> int:
        pass

    @abstractmethod
    def execute_modify(self, data: ModifyData, transaction: Transaction) -> int:
        pass

    @abstractmethod
    def execute_create_table(self, data: CreateTable, transaction: Transaction) -> int:
        pass

    @abstractmethod
    def execute_create_view(self, data: CreateView, transaction: Transaction) -> int:
        pass

    @abstractmethod
    def execute_create_index(self, data: CreateIndex, transaction: Transaction) -> int:
        pass
