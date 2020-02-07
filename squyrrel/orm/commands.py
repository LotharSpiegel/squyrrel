from squyrrel.management.base import BaseCommand


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
        page_number = kwargs.get('page_number', None)
        res = self._wizz.get_all(model, page_size=page_size, page_number=page_number)
        print(res)