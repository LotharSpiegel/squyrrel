from squyrrel.sql.query import (Query, UpdateQuery, InsertQuery,
    DeleteQuery)
from squyrrel.sql.clauses import *
from squyrrel.sql.expressions import (Equals, NumericalLiteral,
    StringLiteral, Like, And, Or, Parameter)
from squyrrel.sql.references import (OnJoinCondition, JoinConstruct, ColumnReference,
    JoinType, TableReference)
from squyrrel.orm.exceptions import *
from squyrrel.orm.field import ManyToOne, ManyToMany, StringField
from squyrrel.orm.filter import ManyToOneFilter
from squyrrel.orm.signals import model_loaded_signal
from squyrrel.orm.utils import extract_ids


class QueryWizzard:

    def __init__(self, db, builder):
        self.db = db
        self.builder = builder
        self.last_sql_query = None
        self.models = {}
        model_loaded_signal.connect(self.on_model_loaded)

    def execute_query(self, sql, params=None):
        self.last_sql_query = sql
        self.db.execute(sql=sql, params=params)

    def commit(self):
        print('COMMIT')
        self.db.commit()

    def rollback(self):
        print('ROLLBACK')
        self.db.rollback()

    def execute_queries_in_transaction(self, queries):
        print(f'start transaction, {len(queries)} queries')
        try:
            for query in queries:
                sql = self.builder.build(query)
                print('\n'+sql+'\n')
                print('params:', query.params)
                self.execute_query(sql, query.params)
        except Exception as exc:
            self.rollback()
            raise self.sql_exc(sql, exc) from exc
        else:
            self.commit()
            print('successfully committed all queries in transaction')

    def on_model_loaded(self, *args, **kwargs):
        new_model_class_meta = kwargs.get('class_meta') or args[0]
        new_model_class = new_model_class_meta.class_reference
        self.register_model(
            model_cls_meta=new_model_class_meta,
            table_name=new_model_class.table_name)

    def register_model(self, model_cls_meta, table_name):
        if table_name is None:
            print(f'Warning: Model {model_cls_meta.class_name} has table_name=None. Will not be registered.')
            return
        key = model_cls_meta.class_name
        if key in self.models.keys():
            print(f'There is already a model on key <{key}>')
            return
        self.models[key] = model_cls_meta.class_reference
        print('register_model:', key)

    def get_model(self, model):
        if isinstance(model, str):
            try:
                return self.models[model]
            except KeyError:
                models = ', '.join(self.models.keys())
                raise Exception(f'Orm: did not find model {model}. Registered models are: {models}')
        return model

    def sql_exc(self, sql, exc):
        return Exception(f'Error during execution of query: \n{sql}\nSql Exc.: {str(exc)}')

    def build_select_fields(self, model, select_fields=None):
        if select_fields is None:
            select_fields = []
            for field_name, field in model.fields():
                select_fields.append(ColumnReference(field_name, table=model.table_name))
        return select_fields

    def build_where_clause(self, model, filter_condition=None, **kwargs):
        if filter_condition is None:
            filter_conditions = []
            for key, value in kwargs.items():
                filter_conditions.append(Equals(
                    ColumnReference(key, table=model.table_name), NumericalLiteral(value)))
            if filter_conditions:
                return WhereClause(filter_conditions[0])
            else:
                return None
        else:
            print('build_where_clause, filter_condition: ', filter_condition)
            return WhereClause(filter_condition)

    def get_by_id(self, model, id, select_fields=None, m2m_options=None, **kwargs):
        model = self.get_model(model)
        filter_condition = Equals(ColumnReference(model.id_field_name(), table=model.table_name),
                                  NumericalLiteral(id))
        return self.get(model=model,
                        select_fields=select_fields,
                        filter_condition=filter_condition,
                        m2m_options=m2m_options,
                        **kwargs)

    def get(self, model, select_fields=None,
            filter_condition=None, m2m_options=None, **kwargs):

        model = self.get_model(model)
        select_fields = self.build_select_fields(model, select_fields)

        where_clause = self.build_where_clause(model, filter_condition=filter_condition, **kwargs)

        from_clause = FromClause(model.table_name)

        many_to_one_entities = self.handle_many_to_one_entities(model=model,
            select_fields=select_fields, from_clause=from_clause)

        one_to_many_aggregations = []
        for relation_name, relation in model.one_to_many_relations():
            if not relation.lazy_load:
                self.handle_one_to_many(model=model,
                        relation_name=relation_name, relation=relation, from_clause=from_clause,
                        select_fields=select_fields, one_to_many_aggregations=one_to_many_aggregations)

        query = Query(
            select_clause=SelectClause(*select_fields),
            from_clause=from_clause,
            where_clause=where_clause,
            pagination=None
        )

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception as exc:
            raise self.sql_exc(sql, exc) from exc

        data = self.db.fetchone()

        if data is None:
            return None

        entity = self.build_entity(model, data, select_fields,
                                many_to_one_entities, one_to_many_aggregations)
        self.handle_many_to_many(entity, m2m_options=m2m_options)
        return entity

    def handle_many_to_one(self, model, select_fields, relation_name, relation, from_clause):
        relation.foreign_model = self.get_model(relation.foreign_model)
        foreign_model = self.get_model(relation.foreign_model)
        foreign_select_fields = self.build_select_fields(foreign_model)
        join_condition = OnJoinCondition(
            Equals(ColumnReference(relation.foreign_key_field, table=model.table_name),
                   ColumnReference(relation.foreign_model_key_field, table=foreign_model.table_name))
        )
        from_clause.table_reference = JoinConstruct(
            table1=from_clause.table_reference,
            join_type=JoinType.LEFT_OUTER_JOIN,
            table2=foreign_model.table_name,
            join_condition=join_condition
        )
        select_fields.extend(foreign_select_fields)

    def handle_many_to_one_entities(self, model, select_fields, from_clause):
        many_to_one_entities = []
        for relation_name, relation in model.many_to_one_relations():
            if relation.lazy_load:
                continue
            self.handle_many_to_one(model=model,
                                    select_fields=select_fields,
                                    relation_name=relation_name,
                                    relation=relation,
                                    from_clause=from_clause)
            many_to_one_entities.append((relation_name, relation))
        return many_to_one_entities

    def handle_one_to_many(self, model, relation_name, relation, from_clause, select_fields, one_to_many_aggregations):
        relation.foreign_model = self.get_model(relation.foreign_model)
        if relation.aggregation is not None:
            one_to_many_aggregations.append(
                self.handle_one_to_many_aggregation(model,
                                                    relation_name, relation,
                                                    from_clause, select_fields)
            )

    def handle_one_to_many_aggregation(self, model, relation_name, relation, from_clause, select_fields):
        subquery_tablename = f'{model.table_name}_{relation_name}'
        aggregation = relation.aggregation
        aggregation.alias = 'aggr'
        subquery = Query(
            select_clause=SelectClause(ColumnReference(model.id_field_name(), alias=model.id_field_name()),
                                      aggregation),
            from_clause=FromClause(relation.foreign_model.table_name),
            groupby_clause=GroupByClause(model.id_field_name()),
            is_subquery=True,
            alias=subquery_tablename
        )

        join_condition = OnJoinCondition(
            Equals(ColumnReference(model.id_field_name(), table=subquery.alias),
                   ColumnReference(model.id_field_name(), table=model.table_name))
        )
        from_clause.table_reference = JoinConstruct(
            table1=from_clause.table_reference,
            join_type=JoinType.LEFT_OUTER_JOIN,
            table2=subquery,
            join_condition=join_condition
        )
        column_reference = ColumnReference('aggr', table=subquery_tablename)
        select_fields.append(column_reference)
        relation.table_name = subquery_tablename
        return (relation_name, relation)

    def handle_many_to_many(self, entity, m2m_options):
        #get_all(self, model, select_fields=None, filter_condition=None, orderby=None, page_size=None, page_number=None, **kwargs):

        #many_to_many_entities = []
        for relation_name, relation in entity.many_to_many_relations():
            if relation.lazy_load:
                continue
            filter_condition = Equals(ColumnReference(entity.model.id_field_name()), NumericalLiteral(entity.id))

            orderby = None
            page_size = None
            page_number = None
            if m2m_options is not None:
                options = m2m_options.get(relation_name, None)
                if options is not None:
                    orderby = options.get('orderby', None)
                    page_size = options.get('page_size', None)
                    page_number = options.get('page_number', None)

            relation.entities = self.get_all(relation.foreign_model,
                                    filter_condition=filter_condition,
                                    orderby=orderby,
                                    page_size=page_size, page_number=page_number)
            print('set entities:')
            print(relation.entities)
            #self.handle_many_to_many(model, relation=relation, from_clause=from_clause)
            #many_to_many_entities.append((relation_name, relation))
        #return many_to_many_entities

    # def handle_many_to_many(self, model, relation, from_clause):
    #     relation.foreign_model = self.get_model(relation.foreign_model)
    #     # foreign_select_fields = self.build_select_fields(foreign_model)
    #     junction_join_condition = OnJoinCondition(
    #         Equals(ColumnReference(model.id_field_name(), table=model.table_name),
    #                ColumnReference(model.id_field_name(), table=relation.junction_table))
    #     )
    #     from_clause.table_reference = JoinConstruct(
    #         table1=from_clause.table_reference,
    #         join_type=JoinType.INNER_JOIN,
    #         table2=relation.junction_table,
    #         join_condition=junction_join_condition
    #     )

    def does_filter_condition_concerns_relation(self, filter_condition, relation):
        if isinstance(filter_condition, Equals):
            print(filter_condition.lhs)
            if filter_condition.lhs == relation.foreign_key_field:
                return True
        return False

    def include_many_to_many_join(self, model, relation, from_clause):
        foreign_model = self.get_model(relation.foreign_model)
        # foreign_select_fields = self.build_select_fields(foreign_model)
        junction_join_condition = OnJoinCondition(
            Equals(ColumnReference(model.id_field_name(), table=model.table_name),
                   ColumnReference(model.id_field_name(), table=relation.junction_table))
        )
        from_clause.table_reference = JoinConstruct(
            table1=from_clause.table_reference,
            join_type=JoinType.INNER_JOIN,
            table2=relation.junction_table,
            join_condition=junction_join_condition
        )

    def build_get_all_query(self,
            model, select_fields=None, filter_condition=None, filters=None,
            orderby=None, page_size=None, page_number=None):
        """filters and filter_condition cannot be both not None"""

        if filters is not None and filter_condition is not None:
            raise Exception('filters and filter_condition cannot be both not None')

        model = self.get_model(model)

        select_fields = self.build_select_fields(model, select_fields)

        if page_number is None:
            pagination = None
        else:
            pagination = Pagination(page_number=page_number, page_size=page_size)

        from_clause = FromClause(model.table_name)

        where_clause = None
        if filter_condition is not None:
            where_clause = self.build_where_clause(model, filter_condition=filter_condition)
            for relation_name, relation in model.many_to_many_relations():
                if self.does_filter_condition_concerns_relation(filter_condition, relation):
                    self.include_many_to_many_join(model=model, relation=relation, from_clause=from_clause)
        # todo: at the moment not symmetric:
        # ex: if Country has M2M fiedl to films but Films not to Country,
        # and you do country get_by_id -> Film.get_all(coutry_id=...), then we do not catch m2m countries

        if filters is not None:
            kwargs = {}
            for filter_ in filters:
                if isinstance(filter_, ManyToOneFilter):
                    many_to_one_relation = getattr(model, filter_.relation)
                    kwargs[many_to_one_relation.foreign_model_key_field] = filter_.id_value
            where_clause = self.build_where_clause(model=model, **kwargs)

        orderby_clause = None
        if orderby is not None:
            if isinstance(orderby, ColumnReference):
                if orderby.table is None:
                    orderby.table = model.table_name
            orderby_clause = OrderByClause(expr=orderby, ascending=True)

        return Query(
            select_clause=SelectClause(*select_fields),
            from_clause=from_clause,
            where_clause=where_clause,
            orderby_clause=orderby_clause,
            pagination=pagination
        )

    def get_all(self, model, select_fields=None, filter_condition=None, filters=None,
                 orderby=None, page_size=None, page_number=None):

        query = self.build_get_all_query(model, select_fields=select_fields, filter_condition=filter_condition,
                        filters=filters, orderby=orderby, page_size=page_size, page_number=page_number)
        model = self.get_model(model)

        from_clause = query.from_clause
        select_fields = query.select_clause.items

        # war vorher vor filter_condition is not None..
        many_to_one_entities = self.handle_many_to_one_entities(model=model,
            select_fields=select_fields, from_clause=from_clause)

        one_to_many_aggregations = []
        for relation_name, relation in model.one_to_many_relations():
            if not relation.lazy_load:
                self.handle_one_to_many(model=model,
                        relation_name=relation_name, relation=relation, from_clause=from_clause,
                        select_fields=select_fields, one_to_many_aggregations=one_to_many_aggregations)

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception as exc:
            raise self.sql_exc(sql, exc) from exc

        res = self.db.fetchall()
        # print('get_all -> res:', res)
        if not res:
            return []
        entities = []
        for data in res:
            entities.append(self.build_entity(model, data, select_fields, many_to_one_entities,
                                one_to_many_aggregations=one_to_many_aggregations))
        return entities

    def build_entity(self, model, data, select_fields,
                     many_to_one_relations, one_to_many_aggregations):
        kwargs = {}
        for i, column_reference in enumerate(select_fields):
            if column_reference.table == model.table_name:
                kwargs[column_reference.name] = data[i]

        for relation_name, relation in many_to_one_relations:
            foreign_kwargs = {}
            for i, column_reference in enumerate(select_fields):
                if column_reference.table == relation.foreign_model.table_name:
                    foreign_kwargs[column_reference.name] = data[i]
            kwargs[relation_name] = relation.foreign_model(**foreign_kwargs)

        for relation_name, relation in one_to_many_aggregations:
            for i, column_reference in enumerate(select_fields):
                if column_reference.table == relation.table_name:
                    kwargs[relation_name] = data[i]
                    break

        #print('build_entity:')
        #print(kwargs)
        return model(**kwargs)

    def count_m2m(self, entity, relation_name):
        model = entity.model
        relation = getattr(entity, relation_name)

        # count({ColumnReference(model.id_field_name(), table=model.table_name)})
        filter_condition = Equals(ColumnReference(entity.id_field_name(), table=model.table_name), NumericalLiteral(entity.id))
        query = self.build_get_all_query(model, select_fields=[f'count (*)'],
                filter_condition=filter_condition, orderby=None, page_size=None, page_number=None)

        self.include_many_to_many_join(model, relation, query.from_clause)

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception as exc:
            raise self.sql_exc(sql, exc) from exc

        data = self.db.fetchone()
        return int(data[0])

    # todo: refactor: def build_count_query(self, ):

    def count(self, model, filter_condition=None, filters=None):
        model = self.get_model(model)


        query = self.build_get_all_query(model,
            select_fields=[f'count ({ColumnReference(model.id_field_name(), table=model.table_name)})'],
            filter_condition=filter_condition,
            filters=filters,
            orderby=None,
            page_size=None,
            page_number=None)

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception as exc:
            raise self.sql_exc(sql, exc) from exc

        data = self.db.fetchone()
        return int(data[0])

    def build_simple_search_query(self, model, select_fields, search_column, value):
        model = self.get_model(model)

        literal = value
        if isinstance(value, str):
            literal = StringLiteral(value)
        elif isinstance(value, int):
            literal = NumericalLiteral(value)
        filter_condition = Equals(ColumnReference(search_column, table=model.table_name),
                                  literal)
        where_clause = self.build_where_clause(model, filter_condition=filter_condition)

        query = Query(
            select_clause=SelectClause(*select_fields),
            from_clause=FromClause(model.table_name),
            where_clause=where_clause,
            pagination=None
        )
        return query

    def prepare_data(self, instance):
        data = instance.data
        prepared_data = dict(data)
        model = instance.model
        # todo: can substitute by same method as m2m fields below..
        # no need for lookup, except not loaded yet
        for column, value in data.items():
            try:
                relation_name, relation = model.get_relation_by_fk_id_column(column)
            except TypeError:
                # did not find relation
                pass
            else:
                print(f'\n did find relation in column {column}')
                if isinstance(relation, ManyToOne):
                    # if columns not equal
                    prepared_value = self.retrieve_value_by_value(
                        model=relation.foreign_model,
                        lookup_column=relation.update_search_column,
                        filter_column=relation.foreign_model.id_field_name(),
                        filter_value=value
                    )
                    prepared_data[relation_name] = prepared_value
                else:
                    raise Exception(f'Error during data preparation: Could not handle {relation}')
        # m2m fields:
        for m2m_relation_name, m2m_relation in model.many_to_many_relations():
            prepared_data[m2m_relation_name] = getattr(instance, m2m_relation_name).entities
        return prepared_data

    def retrieve_value_by_value(self, model, lookup_column, filter_column, filter_value):
        # todo generalize to search function

        if filter_value is None:
            return None
        model = self.get_model(model)
        query = self.build_simple_search_query(model,
            select_fields=[lookup_column],
            search_column=filter_column,
            value=filter_value
        )
        sql = self.builder.build(query)
        print(sql)
        try:
            self.execute_query(sql)
        except Exception as exc:
            raise self.sql_exc(sql, exc) from exc

        data = self.db.fetchone()
        if data is None:
            return None
        # todo: handle case if more than one row is returned
        return data[0]

    def build_like(self, search_column, table, search_value):
        return Like(
            lhs=ColumnReference(search_column, table=table),
            rhs=StringLiteral(f'%{search_value}%')
        )

    def build_search_condition(self, model, search_value, search_columns=None):
        model = self.get_model(model)
        # todo: enable or concatenation
        if search_columns is None:
            search_columns = model.fulltext_search_columns
        if search_columns is None:
            raise Exception('wizzard.build_search_condition needs search_columns (either via argument or from model.fulltext_search_columns)')
        conditions = [self.build_like(search_column=search_column, table=model.table_name, search_value=search_value)
                        for search_column in search_columns]
        return Or.concat(conditions)

    def search(self, model, search_condition, pagesize, active_page, include_count=True, json=False):
        data = {}
        data['list'] = self.get_all(
            model=model,
            page_size=pagesize,
            page_number=active_page,
            filter_condition=search_condition
        )
        if include_count:
            data['count'] = self.count(model=model, filter_condition=search_condition)
        if json:
            data['list'] = [el.as_json() for el in data['list']]
        return data

    def build_m2m_update_queries(self, model, instance_id, relation, actual_ids, new_ids):
        print('update_m2m_relation')
        model = self.get_model(model)
        foreign_model = self.get_model(relation.foreign_model)
        if isinstance(actual_ids, str):
            actual_ids = extract_ids(actual_ids)
        if isinstance(new_ids, str):
            new_ids = extract_ids(new_ids)
        actual_ids = set(actual_ids)
        new_ids = set(new_ids)
        ids_to_add = new_ids - actual_ids
        ids_to_remove = actual_ids - new_ids

        queries = []

        id_field_name = model.id_field_name()
        foreign_id_field_name = foreign_model.id_field_name()
        table = relation.junction_table
        print('m2m, add:', ids_to_add)
        for id_to_add in ids_to_add:
            queries.append(
                InsertQuery.build(table, inserts={
                    id_field_name: instance_id,
                    foreign_id_field_name: id_to_add
                })
            )
        for ids_to_remove in ids_to_remove:
            condition = And.concat([
                Equals(ColumnReference(id_field_name, table), Parameter(instance_id)),
                Equals(ColumnReference(foreign_id_field_name, table), Parameter(ids_to_remove))
            ])
            queries.append(DeleteQuery(table, condition))

        # todo: delete in one query with 'IN' expression

        return queries

    def update(self, model, filter_condition, data, instance=None, commit=True):
        # todo only update changed data
        # i.e. difference data - instance.data
        # todo: all in transaction!
        model = self.get_model(model)
        updates = dict()
        m2m_update_queries = []

        for column, value in data.items():
            # todo value into sql value
            field = model.get_field(column)
            # todo refactor
            if field is None:
                if not value:
                    continue
                relation = model.get_relation(column)
                if isinstance(relation, ManyToOne):
                    filter_column = relation.update_search_column
                    filter_value = value
                    fk_id = self.retrieve_value_by_value(
                        model=relation.foreign_model,
                        lookup_column=relation.foreign_model.id_field_name(),
                        filter_column=filter_column,
                        filter_value=filter_value
                    )
                    if fk_id is None:
                        raise DidNotFindForeignIdException(f'Did not find {model.name()} with {filter_column} = {filter_value}',
                                                           field=column)
                    updates[relation.foreign_key_field] = fk_id
                elif isinstance(relation, ManyToMany):
                    # compare difference
                    # if instance is None, needs to be loaded first..
                    m2m_update_queries.extend(self.build_m2m_update_queries(
                        model=model,
                        instance_id=instance.id,
                        relation=relation,
                        actual_ids=[entity.id for entity in getattr(instance, column).entities],
                        new_ids=value)
                    )

                elif relation is None:
                    raise Exception(f'Error during update: did not find column {column}')
                else:
                    raise Exception(f'Error during update: Could not handle {relation}')
            else:
                updates[column] = value

        update_query = UpdateQuery.build(
            model, filter_condition=filter_condition, updates=updates)
        print('params of update_query:', update_query.params)

        self.execute_queries_in_transaction(queries=[update_query] + m2m_update_queries)

    def update_by_id(self, model, id, data, instance=None, commit=True):
        model = self.get_model(model)
        filter_condition = Equals.id_as_parameter(model, id)
        return self.update(model=model, filter_condition=filter_condition, data=data,
                            instance=instance, commit=commit)