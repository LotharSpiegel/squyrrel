from collections import deque

from squyrrel.core.logging.utils import arguments_tostring


NO_NAME_SIGNAL = 'NO_NAME_SIGNAL'

class Signal:

    def __init__(self, name=None, caching=True, before_emit_hook=None, apply_filter=None):
        self._slots = []
        self.name = name or NO_NAME_SIGNAL
        self.cache = SignalCache()
        self.caching = caching
        self.apply_filter = apply_filter or self.apply_filter
        self.children = []
        self.before_emit_hook = before_emit_hook

    def connect(self, slot):
        """Connect slot to signal"""

        # raise exc if slot not callable
        if not self.is_connected(slot):
            self._slots.append(slot)

    def disconnect(self, slot):
        """Removes slot from signal (in case it is connected)"""

        try:
            index = self._slots.index(slot)
        except ValueError:
            pass
        else:
            self._slots.pop(index)

    def emit(self, *args, **kwargs):
        """Calls all slots (connected to this signal)"""

        if not self.apply_filter(*args, **kwargs):
            return

        if self.before_emit_hook is not None:
            self.before_emit_hook(*args, **kwargs)

        for slot in self._slots:
            try:
                slot(*args, **kwargs)
            except TypeError:
                print('Warning: TypeError...')

        for child in self.children:
            # args, kwargs = self.deform_child_args(*args, **kwargs)
            child.emit(*args, **kwargs)

        if self.caching:
            self.cache.append(args, kwargs)

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def apply_filter(self, *args, **kwargs):
        return True

    def is_connected(self, slot):
        return slot in self._slots

    def clear_cache(self):
        _cache = list(self.cache.cache)
        self.cache.cache.clear()
        return _cache

    def filtered(self, apply_filter, **kwargs):
        kwargs['apply_filter'] = apply_filter
        new_signal = Signal(**kwargs)
        self.add_child(new_signal)
        return new_signal


class SignalFreeze:

    # replace by namedtuple

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


class SignalCache:

    def __init__(self):
        self.cache = deque()

    def append(self, args, kwargs):
        self.cache.append(SignalFreeze(args, kwargs))

    def popfirst(self):
        try:
            return self.cache.popleft()
        except IndexError:
            return None