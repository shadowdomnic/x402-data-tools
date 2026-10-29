"""LangChain tools (also usable from LangGraph and any framework that accepts LangChain tools).

    from x402_data_tools.langchain import get_tools
    tools = get_tools()                      # free tier; get_tools(private_key="0x...") to pay per call
    agent = create_react_agent(llm, tools)
"""

from __future__ import annotations

import json
from typing import Any

from .client import ToolSpec, X402DataTools, X402ToolError
from .schema import args_model


def _result(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def to_langchain(client: X402DataTools, spec: ToolSpec):
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as e:  # pragma: no cover
        raise ImportError("pip install 'x402-data-tools[langchain]'") from e

    def run(**kwargs: Any) -> str:
        try:
            return _result(client.call(spec.name, **kwargs))
        except X402ToolError as e:
            return f"error: {e}"

    async def arun(**kwargs: Any) -> str:
        try:
            return _result(await client.acall(spec.name, **kwargs))
        except X402ToolError as e:
            return f"error: {e}"

    return StructuredTool.from_function(func=run, coroutine=arun, name=spec.name,
                                        description=f"{spec.description} (${spec.price_usd:g} per call)",
                                        args_schema=args_model(spec))


def get_tools(names: list[str] | None = None, tags: list[str] | None = None, all_tools: bool = False,
              client: X402DataTools | None = None, **client_kwargs: Any) -> list:
    """LangChain StructuredTools; pass names=, tags= or all_tools=True to choose (default: a dozen)."""
    client = client or X402DataTools(**client_kwargs)
    return [to_langchain(client, s) for s in client.tools(names, tags, all_tools)]
