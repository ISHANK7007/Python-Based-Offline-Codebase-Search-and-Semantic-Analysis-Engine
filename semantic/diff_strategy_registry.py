from semantic.diff_strategy_base import DiffStrategy

class DiffStrategyRegistry:
    """Registry for available diff strategies."""

    _strategies = {}

    @classmethod
    def register(cls, strategy_class, name=None):
        if not issubclass(strategy_class, DiffStrategy):
            raise TypeError(f"{strategy_class.__name__} is not a DiffStrategy")
        name = name or strategy_class.__name__
        cls._strategies[name] = strategy_class
        return strategy_class

    @classmethod
    def get_strategy(cls, name_or_class, **kwargs):
        if isinstance(name_or_class, str):
            if name_or_class not in cls._strategies:
                raise ValueError(f"No registered strategy named '{name_or_class}'")
            strategy_class = cls._strategies[name_or_class]
            return strategy_class(**kwargs)
        elif issubclass(name_or_class, DiffStrategy):
            return name_or_class(**kwargs)
        raise TypeError(f"Expected strategy name or class, got {type(name_or_class)}")

    @classmethod
    def list_strategies(cls):
        return [
            {"name": name, "description": strategy_class.__doc__}
            for name, strategy_class in cls._strategies.items()
        ]
