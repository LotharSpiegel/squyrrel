from squyrrel.sql.query import Query
from squyrrel.sql.clauses import *
from squyrrel.orm.signals import model_loaded_signal


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
        data = self.db.fetchall()
        return data

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
                raise Exception(f'Orm: did not find model {model}')
        return model

    def get_all(self, model, page_size=None, page_number=None):
        select_fields = []
        model = self.get_model(model)
        for field_name, field in model.fields().items():
            select_fields.append(field_name)
        if page_number is None:
            pagination = None
        else:
            pagination = Pagination(page_number, page_size)

        query = Query(
            select_clause=SelectClause(*select_fields),
            from_clause=FromClause(model.table_name),
            pagination=pagination
        )

        sql = self.builder.build(query)
        # sql = f'select {select_expr} from {model.table_name} {pagination}'

        try:
            res = self.execute_query(sql)
        except Exception:
            raise Exception(f'Error during execution of query: \n{sql}')

        entities = []
        for data in res:
            entities.append(self.build_entity(model, data, select_fields))
        return entities

    def build_entity(self, model, data, select_fields):
        kwargs = {}
        for i, field_name in enumerate(select_fields):
            # print(field_name, data[i])
            kwargs[field_name] = data[i]
        return model(**kwargs)