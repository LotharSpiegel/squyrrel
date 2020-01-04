from squyrrel.core.registry.config_registry import IConfig, IConfigRegistry


class A:

    x_class = None # class instance attribute
    y_class = None

    def __init__(self, x=None, y=None):
        self.x = x or X1() # instance attribute
        self.y = y or Y1()
        self.test_property = 'config 1'

    def quack(self):
        return 'x = {}, y = {}'.format(self.x.quack(), self.y.quack())


class X1:

    def quack(self):
        return 'X1'

class Y1:

    def quack(self):
        return 'Y1'

class X2:

    def quack(self):
        return 'X2'

class Y2:

    def quack(self):
        return 'Y2'


class AConfig2(IConfig):

    class_reference = A

    @staticmethod
    def config_init_kwargs(kwargs): # hook for hooking into __init__, replacing kwargs
        kwargs['x'] = X2()
        kwargs['y'] = Y2()
        return kwargs

    @staticmethod # hook for hooking in exactly after __init__ (squyrrel.config_instance)
    def config(inst):
        inst.test_property = 'config 2'
