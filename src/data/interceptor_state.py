from typing import Any, Callable


class InterceptorState:
    
    _values: dict[str, Any] = dict()
    enable: bool = False
    
    def __init__(self, validator: Callable[[Any], bool]) -> None:
        self._validator = validator
    
    @staticmethod
    def builder(validator: Callable[[Any], bool]):
        return InterceptorState(validator=validator)
    
    def validate(self) -> bool:
        return self._validator(self._values)
    
    def set(self, values: dict[str, Any]):
        self._values = values
    
    def get(self, key: str) -> Any:
        return self._values.get(key)
    
    def clear(self):
        self._values = dict()