from squyrrel.management.base import BaseCommand
from squyrrel.sql.expressions import Equals, NumericalLiteral
from squyrrel.sql.references import ColumnReference


class OrmCommand(BaseCommand):
    prefix = 'orm'

    __inject__ = {
        '_wizz': 'QueryWizzard',
    }


class GetModels(OrmCommand):
    name = 'models'

    def handle(self, *args, **kwargs):
        for key, value in self._wizz.models.items():
            print(key)


class GetAllCommand(OrmCommand):
    name = 'getall'

    def add_arguments(self, parser):
        parser.add_argument('model', type=str, help='Model for which to get all objects (db table rows)')
        parser.add_argument('-p', '--page_size', type=int, help='Page size', default=20)

    def handle(self, *args, **kwargs):
        model = kwargs['model']
        page_size = kwargs.get('page_size', 20)
        active_page = kwargs.get('active_page', None)
        # todo: adjust get_all call
        res = self._wizz.get_all(model, page_size=page_size, active_page=active_page)
        print(res)


class GetCommand(OrmCommand):
    name = 'get'

    def add_arguments(self, parser):
        parser.add_argument('model', type=str, help='Model for which to get object (db table rows)')

    def handle(self, *args, **kwargs):
        model = kwargs.pop('model')
        # todo: build/parse filter_condition
        res = self._wizz.get(model, filter_condition=None)
        print(res)


class GetByIdCommand(OrmCommand):
    name = 'get_by_id'

    def add_arguments(self, parser):
        parser.add_argument('model', type=str, help='Model for which to get object by id (db table rows)')
        parser.add_argument('id', type=str)

    def handle(self, *args, **kwargs):
        model = kwargs.pop('model')
        id_ = kwargs.pop('id')
        model = self._wizz.get_model(model)
        filter_condition = Equals(ColumnReference(model.id_field_name()), NumericalLiteral(id_))
        res = self._wizz.get(model, filter_condition=filter_condition)
        print(res)
