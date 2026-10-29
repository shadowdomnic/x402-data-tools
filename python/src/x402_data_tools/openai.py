"""Function-calling schemas for the OpenAI, Anthropic and other chat APIs, and a dispatcher for tool calls.

    from x402_data_tools.openai import openai_tools, run_tool_call
    tools = openai_tools()
    ... model returns tool_call ...
    content = run_tool_call(tool_call.function.name, tool_call.function.arguments)
"""

from __future__ import annotations

import json
from typing import Any

from .client import X402DataTools, X402ToolError


def openai_tools(names: list[str] | None = None, tags: list[str] | None = None, all_tools: bool = False,
                 client: X402DataTools | None = None) -> list[dict]:
    client = client or X402DataTools()
    return [{"type": "function", "function": {"name": s.name, "description": s.description[:1024],
                                              "parameters": s.input_schema}}
            for s in client.tools(names, tags, all_tools)]


def anthropic_tools(names: list[str] | None = None, tags: list[str] | None = None, all_tools: bool = False,
                    client: X402DataTools | None = None) -> list[dict]:
    client = client or X402DataTools()
    return [{"name": s.name, "description": s.description, "input_schema": s.input_schema}
            for s in client.tools(names, tags, all_tools)]


def run_tool_call(name: str, arguments: str | dict | None, client: X402DataTools | None = None) -> str:
    """Run one tool call from a model and return the content string for the tool message."""
    client = client or X402DataTools()
    args: dict[str, Any] = json.loads(arguments) if isinstance(arguments, str) and arguments else (arguments or {})
    try:
        value = client.call(name, **args)
    except X402ToolError as e:
        return json.dumps({"error": str(e), "status": e.status})
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
