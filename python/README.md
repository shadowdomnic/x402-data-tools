# x402-data-tools

184 data tools for AI agents, each paid per call in USDC on Base over [x402](https://x402.org).
You don't need an account or an API key, and there is a free tier of 20 calls a day.

```bash
pip install x402-data-tools              # core client
pip install "x402-data-tools[langchain]" # + LangChain / LangGraph tools
pip install "x402-data-tools[crewai]"    # + CrewAI tools
```

## What's inside

| Kind | Examples | Price |
|---|---|---|
| **Reports** (one call, scored verdict) | token due diligence, wallet profile, company financial health, website audit, macro briefing | $0.02-0.05 |
| Crypto & EVM | token prices, DEX pools, Uniswap price, gas, balances, ERC-20 transfers, token risk, Aave health, funding rates, options | $0.003 |
| Stocks & macro | SEC fundamentals, filings, insider trades, screener, FRED series, Treasury curve, FX, central-bank rates, Eurostat | $0.003-0.005 |
| Web | page to Markdown, metadata, DNS, WHOIS, SSL, headers, tech stack, email security | $0.003-0.005 |
| Everything else | weather, US alerts, VIN decode, FDA drug labels, clinical trials, prediction markets, arXiv, CVEs, calculators | $0.003 |

Call `X402DataTools().catalog` to list all of them, or `search("yield curve")` to find one.

## Quick start

```python
from x402_data_tools import X402DataTools

tools = X402DataTools()                        # free tier: 20 calls/day per IP
print(tools.call("macro_briefing")["signals"])

paid = X402DataTools(private_key="0x...")      # or set X402_PRIVATE_KEY; pays per call
report = paid.call("token_due_diligence_report",
                   token="0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed", chain="base")
print(report["grade"], report["verdict"])
```

For paid calls, use a dedicated wallet that holds a few dollars of USDC on Base. It needs no ETH, because payments are gasless signatures.

## LangChain / LangGraph

```python
from langgraph.prebuilt import create_react_agent
from x402_data_tools.langchain import get_tools

agent = create_react_agent(llm, get_tools())             # a default dozen tools
agent = create_react_agent(llm, get_tools(tags=["report"]))
```

## CrewAI

```python
from crewai import Agent
from x402_data_tools.crewai import get_tools

analyst = Agent(role="Crypto analyst", goal="Vet tokens before we list them",
                backstory="...", tools=get_tools(["token_due_diligence_report", "wallet_profile_report"]))
```

## OpenAI / Anthropic function calling

```python
from x402_data_tools.openai import openai_tools, anthropic_tools, run_tool_call

tools = openai_tools()            # or anthropic_tools()
# when the model asks for a tool:
content = run_tool_call(call.function.name, call.function.arguments)
```

## MCP (Claude, Cursor, etc.)

You don't need this package for MCP. Add the remote server
`https://bess-x402.onrender.com/mcp`. It gives 20 free calls a day, then answers with the paid x402 URL.

## Notes

- Data comes from public and openly licensed sources: SEC EDGAR, FRED public series, US Treasury, OFAC, NWS, openFDA, DefiLlama, public RPC and others.
- Reports are automated heuristics. They are not financial, legal or security advice.
- Errors come back as `X402ToolError`, with `.status` set to 400 for bad input and 5xx when an upstream source is down. `FreeQuotaExceeded` means you should set a key.

MIT licensed.
