from squyrrel.core.config.base import IConfig, IConfigRegistry
from squyrrel.core.config.decorators import hook


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

    @hook(IConfig.HOOK_INIT_KWARGS)
    def config_init_kwargs(kwargs):
        kwargs['x'] = X2()
        kwargs['y'] = Y2()
        return kwargs

    @hook(IConfig.HOOK_AFTER_INIT)
    def config(inst, **kwargs):
        inst.test_property = 'config 2'
