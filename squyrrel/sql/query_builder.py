from typing import Type

from squyrrel.orm.field import ManyToMany, OneToMany
from squyrrel.orm.exceptions import RelationNotFoundException
from squyrrel.sql.join import OnJoinCondition, JoinType
from squyrrel.sql.utils import sanitize_column_reference, listify
from squyrrel.orm.filter import ManyToOneFilter, ManyToManyFilter, StringFieldFilter
from squyrrel.sql.references import ColumnReference
from squyrrel.orm.model import Model
from squyrrel.sql.clauses import SelectClause, FromClause, WhereClause, Pagination, OrderByClause
from squyrrel.sql.expressions import Equals, Or, Like, And
from squyrrel.sql.query import Query


# todo: options: use paramters or not:
# where dummy_id = ?


class QueryBuilder:
    """ Usage:
    query = QueryBuilder(DummyModel).select().model_filters().pagination().build()
    """

    def __init__(self, model: Type[Model], qw):
        self._qw = qw
        self._model = self.get_model(model)

        self._from_clause = FromClause(self._model.table_name)

        self._select_fields = None
        self._select_clause = None

        self._filter_conditions = []
        self._where_clause = None

        self._groupby_clause = None
        self._having_clause = None

        self._orderby_columns = []
        self._ascending = {}
        self._orderby_clause = None

        self._pagination = None
        self._alias = None
        self._is_subquery = None
        self._options = None

        self._m2m_relations = []
        self._m2m_joined_models = []

        self._one_to_many_relations = []
        self._one_to_many_joined_models = []

    def get_model(self, model):
        if self._qw is not None:
            return self._qw.get_model(model)
        return model

    def build(self):

        if self._from_clause is None:
            raise ValueError('From clause is missing!')

        self._build_select_clause()

        self._build_where_clause()

        self._build_orderby_clause()

        self._build_necessary_joins()

        query = Query(
            select_clause=self._select_clause,
            from_clause=self._from_clause,
            where_clause=self._where_clause,
            groupby_clause=self._groupby_clause,
            having_clause=self._having_clause,
            orderby_clause=self._orderby_clause,
            pagination=self._pagination,
            alias=self._alias,
            is_subquery=self._is_subquery,
            options=self._options
        )
        query.model = self._model
        return query

    def select(self, *args):
        self._select_fields = args
        return self

    def model_filters(self, filters):
        if filters is None:
            return self
        for filter in filters:
            if isinstance(filter, ManyToOneFilter):
                conditions = []
                # print(filter.id_values)
                for id_value in filter.id_values:
                    conditions.append(
                        Equals.column_as_parameter(
                            ColumnReference(filter.key, table=self._model.table_name),
                            id_value
                        )
                    )
                if conditions:
                    self._filter_conditions.append(Or.concat(conditions))
            elif isinstance(filter, ManyToManyFilter):
                conditions = []
                filterforeign_model = self.get_model(filter.foreign_model)
                for id_value in filter.id_values:
                    conditions.append(
                        Equals.column_as_parameter(
                            ColumnReference(filter.key, table=filterforeign_model.table_name),
                            id_value
                        )
                    )
                if conditions:
                    self._filter_conditions.append(Or.concat(conditions))
            elif isinstance(filter, StringFieldFilter):
                self._filter_conditions.append(
                    Like.column_as_parameter(
                        ColumnReference(filter.key, table=self._model.table_name),
                        search_value=filter.value
                    )
                )
        return self

    def add_filter_condition(self, condition):
        if condition is not None:
            self._filter_conditions.append(condition)
        return self

    def by_id(self, instance_id):
        self._filter_conditions.append(
            Equals.id_as_parameter(self._model, instance_id)
        )
        return self

    def fulltext_search(self, search_value):
        if search_value:
            self._filter_conditions.append(self.build_search_condition(search_value))
        return self

    def build_search_condition(self, search_value, search_columns=None):
        # todo: enable or concatenation
        if search_columns is None:
            search_columns = self._model.fulltext_search_columns
            # for column in search_columns:
            #     if isinstance(column, str) and not '.' in column:
            #         column = ColumnReference(column, table=model.table_name)
        if search_columns is None:
            raise ValueError(
                'build_search_condition needs search_columns (either via argument or from model.fulltext_search_columns)')

        conditions = []
        for search_column in search_columns:
            search_column = sanitize_column_reference(search_column)
            conditions.append(Like.column_as_parameter(search_column, search_value=search_value))
        return Or.concat(conditions)

    def pagination(self, active_page, page_size):
        if active_page is None or page_size is None:
            self._pagination = None
        else:
            self._pagination = Pagination(active_page=active_page, page_size=page_size)
        return self

    def orderby(self, columns, ascending=None):
        """ args:
        columns is either a single column (ColumnReference or str) or a list of columns (or ColumnReferences)
        ascending is a dictionary containig as keys the order columns and values if ascending (otherwise descending)"""

        if columns is None:
            if self._model.default_orderby:
                columns = self._model.default_orderby
            else:
                self._orderby_clause = None
                return self

        self._orderby_columns = []
        self._ascending = {}

        for column in listify(columns):
            if isinstance(column, ColumnReference):
                if column.table is None:
                    column.table = self._model.table_name
            else:
                column = ColumnReference(column, table=self._model.table_name)
            self._orderby_columns.append(column)

            column_model = self._get_model_by_table(column.table)
            if ascending is not None:
                try:
                    self._ascending[column] = ascending[column]
                except KeyError:
                    field = column_model.get_field(column.name)
                    self._ascending[column] = field.default_ascending

        return self

    def _build_where_clause(self):
        if self._filter_conditions:
            self._where_clause = WhereClause(And.concat(self._filter_conditions))
        else:
            self._where_clause = None

    def _build_orderby_clause(self):
        if not self._orderby_columns:
            self._orderby_clause = None
        else:
            orderby_columns = []
            for column in self._orderby_columns:
                if column in self._select_fields:
                    orderby_columns.append(column)
                else:
                    print(f'Warning: The orderby column <{column}> is not specified in the select clause')
            self._orderby_clause = OrderByClause(columns=orderby_columns, ascending= self._ascending)

    def _get_model_by_table(self, table):
        if self._qw is None:
            raise Exception('Need query wizzard here!')
        return self._qw.get_model_by_table(table)

    def _build_select_clause(self):
        select_fields = []
        if self._select_fields is None:
            for field_name, field in self._model.fields():
                select_fields.append(ColumnReference(field_name, table=self._model.table_name))
        else:
            select_fields = self._select_fields
        self._select_fields = select_fields

        if not select_fields:
            # replace by warning and select * by default
            raise ValueError('Select clause is missing!')

        self._select_clause = SelectClause(*select_fields)

    def _build_necessary_joins(self):
        columns_to_check = set()

        for condition in self._filter_conditions:
            for column in condition.columns:
                columns_to_check.add(column)

        if self._orderby_clause is not None:
            for column in self._orderby_clause.columns:
                columns_to_check.add(column)

        for column_reference in list(columns_to_check):
            self._include_column(column_reference)

        for relation_name, relation in self._m2m_relations:
            # if self.does_filter_condition_concern_relation(filter_condition, relation):
            # print('include_many_to_many_join:', relation_name)
            self._include_many_to_many_join(relation=relation)

    def _include_column(self, column_reference):
        # print('model, table_name', self.model.table_name)
        # print('include_column', column_reference.table, self._model.table_name)
        if column_reference.table != self._model.table_name:
            foreign_model = self._get_model_by_table(column_reference.table)
            # print('\nforeign_model', foreign_model)
            try:
                relation_name, relation = self._model.get_relation_by_foreign_model(foreign_model.__name__)
            except RelationNotFoundException as exc:
                raise
            else:
                # TODO: handle m21
                if isinstance(relation, ManyToMany):
                    self._add_m2m_relation(foreign_model=foreign_model,
                                           relation_name=relation_name)  # relation_name=search_column.table
                elif isinstance(relation, OneToMany):
                    self._add_one_to_many_relation(foreign_model=foreign_model,
                                                   relation_name=relation_name)

    # todo: def _include_many_to_one_join()

    def _include_many_to_many_join(self, relation):
        # todo: refactor: compare with QueryWizzard.include_many_to_many_join

        # !! todo: first check if not already joined!!

        # foreign_model = self.qw.get_model(relation.foreign_model)
        # foreign_select_fields = self.build_select_fields(foreign_model)
        junction_join_condition = OnJoinCondition(
            Equals(ColumnReference(self._model.id_field_name(), table=self._model.table_name),
                   ColumnReference(self._model.id_field_name(), table=relation.junction_table)))
        self._join_to_from_clause(
            join_type=JoinType.INNER_JOIN,
            table=relation.junction_table,
            join_condition=junction_join_condition)

        foreign_model = self.get_model(relation.foreign_model)
        foreign_table = foreign_model.table_name
        join_condition = OnJoinCondition(
            Equals(ColumnReference(foreign_model.id_field_name(), table=relation.junction_table),
                   ColumnReference(foreign_model.id_field_name(), table=foreign_table))
        )
        self._join_to_from_clause(
            join_type=JoinType.INNER_JOIN,
            table=foreign_table,
            join_condition=join_condition)

    def _join_to_from_clause(self, join_type, table, join_condition):
        self._from_clause.table_reference = self._from_clause.table_reference.join(
            join_type=join_type,
            table2=table,
            join_condition=join_condition
        )

    def _add_m2m_relation(self, foreign_model, relation_name):
        if foreign_model not in self._m2m_joined_models:
            self._m2m_joined_models.append(foreign_model)
            relation = self._model.get_relation(relation_name)
            self._m2m_relations.append((relation_name, relation))
    #     column_model = self.qw.get_model_by_table(column.table)

    def _add_one_to_many_relation(self, foreign_model, relation_name):
        if foreign_model not in self._one_to_many_joined_models:
            self._one_to_many_joined_models.append(foreign_model)
            relation = self._model.get_relation(relation_name)
            self._one_to_many_relations.append((relation_name, relation))
