import abc
import typing as t


class ObjectPoolMixin(abc.ABC):
    """
    nice guide to pattern: https://medium.com/@i.ahmadhassan/mastering-object-pool-design-pattern-in-dart-aecc2c77149d
    """

    __instances: dict[t.Any, "ObjectPoolMixin"] = {}

    def __new__(cls, *args, **kwargs):
        key = (cls, args, tuple(sorted(kwargs.items())))

        if key not in cls.__instances:
            instance = super().__new__(cls)
            instance.__instances[key] = instance

        return cls.__instances[key]
