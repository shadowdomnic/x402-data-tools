"""CrewAI tools.

    from x402_data_tools.crewai import get_tools
    analyst = Agent(role="Analyst", goal="...", tools=get_tools(tags=["report"]))
"""

from __future__ import annotations

import json
from typing import Any

from .client import ToolSpec, X402DataTools, X402ToolError
from .schema import args_model


def to_crewai(client: X402DataTools, spec: ToolSpec):
    try:
        from crewai.tools import BaseTool
    except ImportError as e:  # pragma: no cover
        raise ImportError("pip install 'x402-data-tools[crewai]'") from e

    from pydantic import BaseModel

    model = args_model(spec)

    class X402Tool(BaseTool):
        name: str = spec.name
        description: str = f"{spec.description} (${spec.price_usd:g} per call)"
        args_schema: type[BaseModel] = model

        def _run(self, **kwargs: Any) -> str:
            try:
                value = client.call(spec.name, **kwargs)
            except X402ToolError as e:
                return f"error: {e}"
            return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)

    return X402Tool()


def get_tools(names: list[str] | None = None, tags: list[str] | None = None, all_tools: bool = False,
              client: X402DataTools | None = None, **client_kwargs: Any) -> list:
    client = client or X402DataTools(**client_kwargs)
    return [to_crewai(client, s) for s in client.tools(names, tags, all_tools)]
