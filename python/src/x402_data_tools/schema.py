"""Pydantic argument models built from each tool's JSON schema, for frameworks that want a model class."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, create_model

from .client import ToolSpec

_TYPES = {"string": str, "integer": int, "number": float, "boolean": bool, "array": list, "object": dict}


def args_model(spec: ToolSpec) -> type[BaseModel]:
    props = spec.input_schema.get("properties", {})
    required = set(spec.input_schema.get("required", []))
    fields: dict[str, Any] = {}
    for name, p in props.items():
        typ = _TYPES.get(p.get("type"), Any)
        desc = p.get("description")
        if name in required:
            fields[name] = (typ, Field(..., description=desc))
        else:
            fields[name] = (Optional[typ], Field(p.get("default"), description=desc))
    model_name = "".join(w.capitalize() for w in spec.name.split("_")) + "Args"
    return create_model(model_name, **fields)
