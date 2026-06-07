from __future__ import annotations

import copy
import json
from typing import Any, Callable


try:
    from pydantic import BaseModel as PydanticBaseModel
    from pydantic import Field as PydanticField

    BaseModel = PydanticBaseModel
    Field = PydanticField
except Exception:  # pragma: no cover - used only when dependencies are not installed

    def Field(default: Any = None, default_factory: Callable[[], Any] | None = None, **_: Any) -> Any:
        return default_factory() if default_factory else default

    class BaseModel:
        """Small compatibility shim so mock mode can run before dependencies are installed."""

        def __init__(self, **kwargs: Any) -> None:
            annotations = getattr(self.__class__, "__annotations__", {})
            for name in annotations:
                if name in kwargs:
                    value = kwargs[name]
                else:
                    value = copy.deepcopy(getattr(self.__class__, name, None))
                setattr(self, name, value)
            for name, value in kwargs.items():
                if name not in annotations:
                    setattr(self, name, value)

        def model_dump(self, **_: Any) -> dict[str, Any]:
            return copy.deepcopy(self.__dict__)

        def dict(self, **_: Any) -> dict[str, Any]:
            return self.model_dump()

        def model_dump_json(self, **_: Any) -> str:
            return json.dumps(self.model_dump(), default=str)

