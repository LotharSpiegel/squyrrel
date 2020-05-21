from squyrrel.sql.query import (Query, UpdateQuery, InsertQuery,
    DeleteQuery, CreateTableQuery)
from squyrrel.sql.clauses import *
from squyrrel.sql.expressions import (Equals, NumericalLiteral,
    StringLiteral, Like, And, Or, Parameter)
from squyrrel.sql.references import ColumnReference, TableReference
from squyrrel.sql.join import OnJoinCondition, JoinConstruct, JoinType
from squyrrel.sql.utils import sanitize_column_reference
from squyrrel.orm.exceptions import *
from squyrrel.orm.field import (ManyToOne, ManyToMany, StringField,
    DateTimeField, IntegerField)
from squyrrel.orm.filter import ManyToOneFilter, ManyToManyFilter, StringFieldFilter


def listify(obj):
    if not isinstance(obj, (list, tuple)):
        return [obj]
    return obj


class QueryBuilder:

    def __init__(self, model, qw):
        self.model = model
        self.qw = qw
        self.m2m_relations = []
        self.m2m_joined_models = []
        self.select_fields = []

    def init_select_fields(self, select_fields=None):
        if select_fields is None:
            for field_name, field in self.model.fields():
                self.select_fields.append(ColumnReference(field_name, table=self.model.table_name))
        else:
            self.select_fields = select_fields

    def build_filter_conditions(self, filter_condition, filters, fulltext_search):
        # todo: extract/refactor into own method the build of whereclause
        # todo: remove filter_condition (only use filters)
        # and check how to use include_many_to_many_join...

        # todo: at the moment not symmetric:
        # ex: if Country has M2M fiedl to films but Films not to Country,
        # and you do country get_by_id -> Film.get_all(coutry_id=...), then we do not catch m2m countries

        # todo: extract -> refactor
        # todo: check when needed to include relations joins (to have fields available for filtering)

        self.filter_conditions = []
        if filters is not None:
            for filter_ in filters:
                if isinstance(filter_, ManyToOneFilter):
                    conditions = []
                    for id_value in filter_.id_values:
                        conditions.append(
                            Equals.column_as_parameter(
                                ColumnReference(filter_.key, table=self.model.table_name),
                                id_value
                            )
                        )
                    if conditions:
                        self.filter_conditions.append(Or.concat(conditions))
                elif isinstance(filter_, ManyToManyFilter):
                    conditions = []
                    filter_foreign_model = self.qw.get_model(filter_.foreign_model)
                    for id_value in filter_.id_values:
                        conditions.append(
                            Equals.column_as_parameter(
                                ColumnReference(filter_.key, table=filter_foreign_model.table_name),
                                id_value
                            )
                        )
                    if conditions:
                        self.filter_conditions.append(Or.concat(conditions))
                    #raise NotImplementedError('m2m filter build query')
                elif isinstance(filter_, StringFieldFilter):
                    self.filter_conditions.append(
                        Like.column_as_parameter(
                            ColumnReference(filter_.key, table=self.model.table_name),
                            search_value=filter_.value
                        )
                    )
        #print('\n')
        #print('filters:')
        #print(filters)
        #print('filter_conditions:')
        #print(self.filter_conditions)

        if filter_condition is not None:
            self.filter_conditions.append(filter_condition)

        if fulltext_search is not None:
            self.filter_conditions.append(
                self.build_search_condition(search_value=fulltext_search))

    def build_where_clause(self):
        #print('filter_conditions:', self.filter_conditions)
        if self.filter_conditions:
            self.where_clause = WhereClause(And.concat(self.filter_conditions))
        else:
            self.where_clause = None

    def build_search_condition(self, search_value, search_columns=None):
        # todo: enable or concatenation
        if search_columns is None:
            search_columns = self.model.fulltext_search_columns
            # for column in search_columns:
            #     if isinstance(column, str) and not '.' in column:
            #         column = ColumnReference(column, table=model.table_name)
        if search_columns is None:
            raise Exception('build_search_condition needs search_columns (either via argument or from model.fulltext_search_columns)')

        conditions = []
        for search_column in search_columns:
            search_column = sanitize_column_reference(search_column)
            conditions.append(Like.column_as_parameter(search_column, search_value=search_value))
        return Or.concat(conditions)

    def include_column(self, column_reference):
        # print('model, table_name', self.model.table_name)
        # print('include_column', column_reference.table, self.model.table_name)
        if column_reference.table != self.model.table_name:
            foreign_model = self.qw.get_model_by_table(column_reference.table)
            #print('\nforeign_model', foreign_model)
            try:
                relation_name, relation = self.model.get_relation_by_foreign_model(foreign_model.__name__)
            except RelationNotFoundException as exc:
                raise
            else:
                # TODO: handle m21 and 12m
                #print(relation_name)
                #print(relation)
                if isinstance(relation, ManyToMany):
                    self.add_m2m_relation(foreign_model=foreign_model, relation_name=relation_name) # relation_name=search_column.table

    def does_filter_condition_concern_relation(self, filter_condition, relation):
        if isinstance(filter_condition, (Equals, Like)):
            if filter_condition.lhs == relation.foreign_key_field:
                return True
        return False

    def join_to_from_clause(self, join_type, table, join_condition):
        self.from_clause.table_reference = self.from_clause.table_reference.join(
            join_type=join_type,
            table2=table,
            join_condition=join_condition
        )
        #print('after join_to_from_clause')
        #print(self.from_clause.table_reference)

    def include_many_to_many_join(self, relation):
        # !! todo: first check if not already joined!!

        # foreign_model = self.qw.get_model(relation.foreign_model)
        # foreign_select_fields = self.build_select_fields(foreign_model)
        junction_join_condition = OnJoinCondition(
            Equals(ColumnReference(self.model.id_field_name(), table=self.model.table_name),
                   ColumnReference(self.model.id_field_name(), table=relation.junction_table)))
        self.join_to_from_clause(
            join_type=JoinType.INNER_JOIN,
            table=relation.junction_table,
            join_condition=junction_join_condition)
        foreign_model = self.qw.get_model(relation.foreign_model)
        foreign_table = foreign_model.table_name
        join_condition = OnJoinCondition(
            Equals(ColumnReference(foreign_model.id_field_name(), table=relation.junction_table),
                   ColumnReference(foreign_model.id_field_name(), table=foreign_table))
        )
        self.join_to_from_clause(
            join_type=JoinType.INNER_JOIN,
            table=foreign_table,
            join_condition=join_condition)

    def build_joins(self):
        columns_to_check = set()
        for condition in self.filter_conditions:
            for column in condition.columns:
                columns_to_check.add(column)
        #print('columns_to_check:', columns_to_check)
        for column_reference in list(columns_to_check):
            self.include_column(column_reference)

        for relation_name, relation in self.m2m_relations:
            #if self.does_filter_condition_concern_relation(filter_condition, relation):
            #print('include_many_to_many_join:', relation_name)
            self.include_many_to_many_join(relation=relation)

    def add_m2m_relation(self, foreign_model, relation_name):
        if not foreign_model in self.m2m_joined_models:
            self.m2m_joined_models.append(foreign_model)
            relation = self.model.get_relation(relation_name)
            self.m2m_relations.append((relation_name, relation))
    #     column_model = self.qw.get_model_by_table(column.table)

    def build_orderby_clause(self, columns, ascending=None):
        """ args:
        columns is either a single column (ColumnReference or str) or a list of columns (or ColumnReferences)
        ascending is a dictionary containig as keys the order columns and values if ascending (otherwise descending)"""

        #print('build_orderby_clause, columns:', columns)
        if columns is None:
            if self.model.default_orderby:
                columns = self.model.default_orderby
            else:
                self.orderby_clause = None
                return
        ascending = {}
        columns_ = []
        #print(columns)
        for column in listify(columns):
            #print('check column:', column)
            if isinstance(column, ColumnReference):
                if column.table is None:
                    column.table = self.model.table_name
            else:
                column = ColumnReference(column, table=self.model.table_name)
            columns_.append(column)
            column_model = self.qw.get_model_by_table(column.table)
            try:
                ascending[column] = ascending[column]
            except KeyError:
                field = column_model.get_field(column.name)
                ascending[column] = field.default_ascending
        if not columns_:
            self.orderby_clause = None
        else:
            self.orderby_clause = OrderByClause(columns=columns_, ascending=ascending)

    def build_pagination(self, active_page, page_size):
        if active_page is None or page_size is None:
            self.pagination = None
        else:
            self.pagination = Pagination(active_page=active_page, page_size=page_size)

    def build_get_all_query(self,
                            select_fields=None,
                            filter_condition=None,
                            filters=None,
                            fulltext_search=None,
                            orderby=None,
                            ascending=None,
                            page_size=None,
                            active_page=None):
        if filters is not None and filter_condition is not None:
            raise Exception('filters and filter_condition cannot be both not None')

        self.init_select_fields(select_fields)

        self.build_pagination(active_page=active_page, page_size=page_size)

        self.from_clause = FromClause(self.model.table_name)

        self.build_filter_conditions(
            filter_condition=filter_condition,
            filters=filters,
            fulltext_search=fulltext_search)

        self.build_where_clause()

        self.build_orderby_clause(orderby, ascending)

        self.build_joins()

        return self.build_query()

    def build_query(self):
        return Query(
            select_clause=SelectClause.build(*self.select_fields),
            from_clause=self.from_clause,
            where_clause=self.where_clause,
            orderby_clause=self.orderby_clause,
            pagination=self.pagination
        )
