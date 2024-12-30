from typing import Collection

from db.parse.create_index import CreateIndex
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.delete_data import DeleteData
from db.parse.insert_data import InsertData
from db.parse.lexer import Lexer
from db.parse.modify_data import ModifyData
from db.parse.query_data import QueryData
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.predicate import Predicate
from db.query.term import Term
from db.record.schema import Schema


class Parser:

    def __init__(self, sql: str) -> None:
        self.lexer = Lexer(sql)

    def filed(self) -> str:
        return self.lexer.eat_id()

    def constant(self) -> Constant:
        if self.lexer.match_int_constant():
            value = self.lexer.eat_string_constant()
            assert value is not None
            return Constant(value)
        elif self.lexer.match_string_constant():
            value = self.lexer.eat_int_constant()
            assert value is not None
            return Constant(value)
        else:
            raise SyntaxError(f"Expected constant, but not found {self.lexer.current_token}")


    def expression(self) -> Expression:
        value = Constant(self.lexer.eat_string_constant())

        if self.lexer.match_id():
            return Expression(self.filed())
        else:
            return Expression(self.constant())


    def term(self) -> Term:
        left = self.expression()
        self.lexer.eat_delimiter('=')
        right = self.expression()
        return Term(left, right)

    def predicate(self) -> Predicate:
        predicate = Predicate([self.term()])
        if self.lexer.match_keyword('and'):
            self.lexer.eat_keyword('and')
            predicate.conjoin_with(self.predicate())

        return predicate

    def query(self) -> QueryData:
        self.lexer.eat_keyword('select')
        field_list = self.select_list()
        self.lexer.eat_keyword('from')
        tables = self.table_list()

        predicate = Predicate()
        if self.lexer.match_keyword('where'):
            self.lexer.eat_keyword('where')
            predicate = self.predicate()

        return QueryData(field_list, tables, predicate)


    def select_list(self) -> list[str]:
        field_list = [self.filed()]
        while self.lexer.match_delimiter(','):
            self.lexer.eat_delimiter(',')
            field_list.extend(self.select_list())
        return field_list

    def table_list(self) -> Collection[str]:
        tables = [self.lexer.eat_id()]
        if self.lexer.match_delimiter(','):
            self.lexer.eat_delimiter(',')
            tables.extend(self.table_list())
        return tables

    def update_command(self) -> InsertData | DeleteData | ModifyData | object:
        if self.lexer.match_keyword('insert'):
            return self.insert()

        elif self.lexer.match_keyword('delete'):
            return self.delete()

        elif self.lexer.match_keyword('update'):
            return self.modify()
        else:
            return self.create()


    def create(self) -> object:
        self.lexer.eat_keyword('create')
        if self.lexer.match_keyword('table'):
            return self.create_table()
        elif self.lexer.match_keyword('view'):
            return self.create_view()
        else:
            return self.create_index()


    def delete(self) -> DeleteData:
        self.lexer.eat_keyword('delete')
        self.lexer.eat_keyword('from')
        table_name = self.lexer.eat_id()
        predicate = Predicate()
        if self.lexer.match_keyword('where'):
            self.lexer.eat_keyword('where')
            predicate = self.predicate()
        return DeleteData(table_name, predicate)


    def insert(self) -> InsertData:
        self.lexer.eat_keyword('insert')
        self.lexer.eat_keyword('into')
        table_name = self.lexer.eat_id()
        self.lexer.eat_delimiter('(')
        # TODO: filed_listの実装確認
        field_list = [self.filed()]
        values = [self.constant()]
        while self.lexer.match_delimiter(','):
            self.lexer.eat_delimiter(',')
            values.append(self.constant())
        self.lexer.eat_delimiter(')')
        return InsertData(table_name, field_list, values)


    def const_list(self) -> list[Constant]:
        values = [self.constant()]
        if self.lexer.match_delimiter(','):
            self.lexer.eat_delimiter(',')
            values.append(self.constant())
        return values

    def modify(self) -> ModifyData:
        self.lexer.eat_keyword('update')
        table_name = self.lexer.eat_id()
        self.lexer.eat_keyword('set')
        field_name = self.filed()
        self.lexer.eat_delimiter('=')
        value = self.expression()
        predicate = Predicate()
        if self.lexer.match_keyword('where'):
            self.lexer.eat_keyword('where')
            predicate = self.predicate()
        return ModifyData(table_name, field_name, value, predicate)


    def create_table(self) -> CreateTable:
        self.lexer.eat_keyword('table')
        table_name = self.lexer.eat_id()
        self.lexer.eat_delimiter('(')
        schema = self.field_defs()
        self.lexer.eat_delimiter(')')
        return CreateTable(table_name, schema)

    def field_defs(self) -> Schema:
        field_name = self.filed()

        return self.field_type(field_name)

    def field_type(self, field_name: str) -> Schema:
        schema = Schema()
        if self.lexer.eat_keyword('int'):
            self.lexer.eat_delimiter('int')
            schema.add_int_field(field_name)
        else:
            self.lexer.eat_keyword('varchar')
            self.lexer.eat_delimiter('(')
            string_length = self.lexer.eat_int_constant()
            self.lexer.eat_delimiter(')')
            schema.add_string_field(field_name, string_length)
        return schema

    def create_view(self) -> object:
        self.lexer.eat_keyword('view')
        view_name = self.lexer.eat_id()
        self.lexer.eat_keyword('as')
        query = self.query()

        return CreateView(view_name, query)


    def create_index(self) -> CreateIndex:
        self.lexer.eat_keyword('index')
        index_name = self.lexer.eat_id()
        self.lexer.eat_keyword('on')
        table_name = self.lexer.eat_id()
        self.lexer.eat_delimiter('(')
        field_name = self.filed()
        self.lexer.eat_delimiter(')')
        return CreateIndex(index_name, table_name, field_name)



