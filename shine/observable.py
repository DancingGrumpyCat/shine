class Observable:
    def __init__(self, value):
        if isinstance(value, Observable):
            raise Exception('Cannot nest observables')
        self.value = value
        self.listeners = []

    def set(self, value):
        if isinstance(value, Observable):
            raise Exception('Cannot nest observables')
        self.value = value
        for listener in self.listeners:
            listener(self.value)

    def get(self):
        return self.value

    def add_listener(self, listener):
        self.listeners.append(listener)

    @classmethod
    def dict(cls, **kwargs):
        obj = cls({name: value.get() for name, value in kwargs.items()})

        def listener(_value):
            obj.set({name: value.get() for name, value in kwargs.items()})

        for kwarg in kwargs.values():
            kwarg.add_listener(listener)

        return obj

    @classmethod
    def list(cls, *args):
        obj = cls([arg.get() for arg in args])

        def listener(_value):
            obj.set([arg.get() for arg in args])

        for arg in args:
            arg.add_listener(listener)

        return obj

    def map(self, fn):
        obj = Observable(fn(self.value))

        def listener(value):
            obj.set(fn(value))

        self.add_listener(listener)

        return obj
