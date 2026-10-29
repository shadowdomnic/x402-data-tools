"""Client for the x402 data tools at https://bess-x402.onrender.com.

Two ways to call a tool:

* paid: give an EVM private key (or set X402_PRIVATE_KEY) holding a little USDC on Base. Each call is an HTTP
  GET that pays its price over x402, usually $0.003-0.05, with no account or API key.
* free: without a key, calls go through the service's MCP endpoint, which allows 20 successful calls per IP
  per day. Use it to try the tools; switch to a key for volume.
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
from dataclasses import dataclass, field
from importlib import resources
from typing import Any

import httpx

BASE_URL = "https://bess-x402.onrender.com"
BASE_NETWORK = "eip155:8453"

# A small set that fits in an agent's context; pass names= or tags= to pick others, or all_tools=True.
DEFAULT_TOOLS = (
    "token_due_diligence_report", "wallet_profile_report", "company_financial_health_report",
    "website_audit_report", "macro_briefing", "read_web_page", "us_company_fundamentals", "crypto_token_prices",
    "evm_gas_fees", "fred_series", "prediction_markets_search", "weather_forecast",
)


class X402ToolError(Exception):
    """A tool call failed: bad input (status 4xx), an upstream outage (5xx) or a used-up free quota."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class FreeQuotaExceeded(X402ToolError):
    """The 20 free calls a day are used; set a private key to pay per call."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    route: str
    price_usd: float
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    input_schema: dict = field(default_factory=dict)


def load_catalog() -> list[ToolSpec]:
    data = json.loads(resources.files(__package__).joinpath("catalog.json").read_text(encoding="utf-8"))
    return [ToolSpec(**t) for t in data["tools"]]


def _run(coro):
    """Run a coroutine from sync code, also when an event loop is already running (notebooks, servers)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    out: dict = {}

    def target():
        try:
            out["value"] = asyncio.run(coro)
        except BaseException as e:  # noqa: BLE001 - re-raised in the caller's thread
            out["error"] = e

    t = threading.Thread(target=target)
    t.start()
    t.join()
    if "error" in out:
        raise out["error"]
    return out["value"]


class X402DataTools:
    """Catalog and caller for 180+ pay-per-call data tools.

    >>> tools = X402DataTools()                     # free tier, 20 calls a day
    >>> tools.call("macro_briefing")["signals"][0]
    >>> paid = X402DataTools(private_key="0x...")   # pays USDC on Base per call
    """

    def __init__(self, private_key: str | None = None, base_url: str | None = None,
                 network: str = BASE_NETWORK, timeout: float = 120):
        self.private_key = private_key or os.environ.get("X402_PRIVATE_KEY")
        self.base_url = (base_url or os.environ.get("X402_DATA_TOOLS_URL") or BASE_URL).rstrip("/")
        self.network = network
        self.timeout = timeout
        self.catalog = {t.name: t for t in load_catalog()}

    @property
    def paid(self) -> bool:
        return bool(self.private_key)

    def tools(self, names: list[str] | tuple[str, ...] | None = None, tags: list[str] | None = None,
              all_tools: bool = False) -> list[ToolSpec]:
        """Tool specs by name, by tag, every tool, or the default dozen."""
        if all_tools:
            return list(self.catalog.values())
        if tags:
            want = set(tags)
            return [t for t in self.catalog.values() if want & set(t.tags)]
        picked = []
        for n in names or DEFAULT_TOOLS:
            if n not in self.catalog:
                raise KeyError(f"unknown tool {n!r}; see X402DataTools().catalog")
            picked.append(self.catalog[n])
        return picked

    def search(self, text: str, limit: int = 10) -> list[ToolSpec]:
        """Tools whose name, title, tags or description mention every word of the text."""
        words = text.lower().split()
        hits = [t for t in self.catalog.values()
                if all(w in f"{t.name} {t.title} {' '.join(t.tags)} {t.description}".lower() for w in words)]
        return hits[:limit]

    def call(self, name: str, **arguments: Any) -> Any:
        return _run(self.acall(name, **arguments))

    async def acall(self, name: str, **arguments: Any) -> Any:
        spec = self.catalog.get(name)
        if spec is None:
            raise X402ToolError(f"unknown tool {name!r}", 400)
        args = {k: v for k, v in arguments.items() if v is not None}
        return await (self._paid_call(spec, args) if self.paid else self._free_call(spec, args))

    async def _paid_call(self, spec: ToolSpec, args: dict) -> Any:
        try:
            from eth_account import Account
            from x402 import x402Client
            from x402.http.clients import x402HttpxClient
            from x402.mechanisms.evm.exact import register_exact_evm_client
        except ImportError as e:  # pragma: no cover - dependency problem on the user's side
            raise X402ToolError("paid calls need the x402 SDK: pip install 'x402[evm,httpx]'") from e
        client = x402Client()
        register_exact_evm_client(client, Account.from_key(self.private_key), networks=self.network)
        params = {k: str(v).lower() if isinstance(v, bool) else v for k, v in args.items()}
        async with x402HttpxClient(client, timeout=self.timeout) as http:
            r = await http.get(self.base_url + spec.route, params=params)
        if r.status_code >= 400:
            try:
                detail = r.json().get("detail", r.text)
            except ValueError:
                detail = r.text
            raise X402ToolError(f"{spec.name}: {detail}", r.status_code)
        return r.json()

    async def _free_call(self, spec: ToolSpec, args: dict) -> Any:
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": spec.name, "arguments": args}}
        async with httpx.AsyncClient(timeout=self.timeout) as http:
            r = await http.post(self.base_url + "/mcp", json=body,
                                headers={"accept": "application/json, text/event-stream"})
        if r.status_code >= 400:
            raise X402ToolError(f"{spec.name}: MCP endpoint answered {r.status_code}", r.status_code)
        msg = r.json()
        if "error" in msg:
            raise X402ToolError(f"{spec.name}: {msg['error'].get('message')}", 400)
        result = msg["result"]
        text = "".join(c.get("text", "") for c in result.get("content", []))
        if result.get("isError"):
            raise X402ToolError(f"{spec.name}: {text}", 400)
        try:
            return json.loads(text)
        except ValueError:
            if text.startswith("Free limit"):
                raise FreeQuotaExceeded(f"{text} Set X402_PRIVATE_KEY (a wallet with USDC on Base) to keep going.",
                                        402) from None
            return text
