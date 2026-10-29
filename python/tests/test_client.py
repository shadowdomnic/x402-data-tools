import json

import httpx
import pytest

from x402_data_tools import DEFAULT_TOOLS, FreeQuotaExceeded, X402DataTools
from x402_data_tools.openai import anthropic_tools, openai_tools
from x402_data_tools.schema import args_model


def test_catalog_and_defaults():
    t = X402DataTools(private_key=None)
    assert len(t.catalog) >= 180
    assert [s.name for s in t.tools()] == list(DEFAULT_TOOLS)
    assert all(s.route.startswith("/v1/") and s.price_usd >= 0.002 for s in t.catalog.values())
    assert any(s.name == "token_due_diligence_report" for s in t.tools(tags=["report"]))
    assert t.search("yield curve")


def test_schemas():
    t = X402DataTools()
    spec = t.catalog["token_due_diligence_report"]
    model = args_model(spec)
    assert model(token="0xabc").chain == "base"
    with pytest.raises(Exception):
        model()
    assert openai_tools(["macro_briefing"])[0]["function"]["name"] == "macro_briefing"
    assert anthropic_tools(["macro_briefing"])[0]["input_schema"]["type"] == "object"


def _mock(monkeypatch, text, is_error=False):
    def handler(request):
        body = json.loads(request.content)
        assert body["method"] == "tools/call"
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1,
                                         "result": {"content": [{"type": "text", "text": text}], "isError": is_error}})
    real = httpx.AsyncClient

    def client(*a, **kw):
        kw["transport"] = httpx.MockTransport(handler)
        return real(*a, **kw)
    monkeypatch.setattr(httpx, "AsyncClient", client)


def test_free_call_parses_json(monkeypatch):
    monkeypatch.delenv("X402_PRIVATE_KEY", raising=False)
    _mock(monkeypatch, '{"ok": 1}')
    assert X402DataTools().call("macro_briefing") == {"ok": 1}


def test_free_quota(monkeypatch):
    monkeypatch.delenv("X402_PRIVATE_KEY", raising=False)
    _mock(monkeypatch, "Free limit of 20 calls per day reached. Continue with the paid endpoint ...")
    with pytest.raises(FreeQuotaExceeded):
        X402DataTools().call("macro_briefing")
