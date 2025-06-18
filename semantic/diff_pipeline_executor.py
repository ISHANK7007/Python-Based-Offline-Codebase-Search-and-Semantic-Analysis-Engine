from semantic.diff_logic_core import DiffStrategy  # Ensure this matches actual path

class DiffStrategyRegistry:
    """Registry for available diff strategies."""

    _strategies = {}

    @classmethod
    def register(cls, strategy_class, name=None):
        """Register a strategy class.

        Can be used directly or as a decorator:
            @DiffStrategyRegistry.register
            class MyStrategy(DiffStrategy): ...
        """
        if not issubclass(strategy_class, DiffStrategy):
            raise TypeError(f"{strategy_class.__name__} is not a subclass of DiffStrategy")

        strategy_name = name or strategy_class.__name__
        cls._strategies[strategy_name] = strategy_class
        return strategy_class  # Allows decorator usage

    @classmethod
    def get_strategy(cls, name_or_class, **kwargs):
        """Retrieve a strategy instance by name or class reference.

        Args:
            name_or_class (str or Type[DiffStrategy]): The strategy name or class itself.
            **kwargs: Additional parameters passed to strategy constructor.

        Returns:
            An instance of the requested DiffStrategy.
        """
        if isinstance(name_or_class, str):
            if name_or_class not in cls._strategies:
                raise ValueError(f"No registered strategy named '{name_or_class}'")
            strategy_class = cls._strategies[name_or_class]
            return strategy_class(**kwargs)

        if isinstance(name_or_class, type) and issubclass(name_or_class, DiffStrategy):
            return name_or_class(**kwargs)

        raise TypeError(f"Expected strategy name or class, got {type(name_or_class).__name__}")

    @classmethod
    def list_strategies(cls):
        """List all registered strategy classes with their docstrings."""
        return [
            {
                "name": name,
                "description": (strategy_class.__doc__ or "").strip()
            }
            for name, strategy_class in cls._strategies.items()
        ]
