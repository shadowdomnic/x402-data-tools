# x402-data-tools

**184 data tools for AI agents, each paid per call with no account or API key.**
Agents pay in USDC on Base over [x402](https://x402.org), usually $0.003 for a lookup and $0.02-0.05 for a
finished report. Without a wallet, you get 20 free calls a day.

| Package | Install | Frameworks |
|---|---|---|
| [Python](python/) | `pip install x402-data-tools` | LangChain, LangGraph, CrewAI, OpenAI and Anthropic function calling |
| [JavaScript](js/) | `npm i x402-data-tools` | Vercel AI SDK, OpenAI and Anthropic function calling |
| MCP | `https://bess-x402.onrender.com/mcp` | Claude, Cursor, any MCP client (remote, streamable HTTP) |

## Reports: one call, one verdict

| Tool | Price | Returns |
|---|---|---|
| `token_due_diligence_report` | $0.02 | ERC-20 safety score: owner powers in bytecode, proxy, Sourcify verification, deepest Uniswap pool in USD |
| `wallet_profile_report` | $0.02 | EVM address across 5 chains: holdings, activity profile, EIP-7702, ENS, OFAC sanctions check |
| `company_financial_health_report` | $0.05 | US-listed company from SEC filings: health score with reasons, 5-year growth, margins, insiders, filings |
| `website_audit_report` | $0.02 | Security headers, TLS, SPF/DKIM/DMARC, SEO basics, with a list of fixes |
| `macro_briefing` | $0.02 | Yield curve, recession and rate-path signals, Fed funds, inflation expectations, dollar, oil, policy rates |

## And 179 single lookups

Crypto prices and history, DEX pools, Uniswap prices, gas, balances, ERC-20 transfers, token risk, Aave health,
funding rates, options, Polymarket, Kalshi and Manifold, SEC fundamentals, filings, insider trades, FRED, Treasury,
FX, Eurostat, web pages as Markdown, DNS, WHOIS, SSL, weather and US alerts, VIN decoding, FDA labels and recalls,
clinical trials, arXiv, CVEs, and loan, option and unit calculators. See [catalog.json](catalog.json) for the
full list with prices and input schemas.

## Paying

Each paid call is an HTTP GET that answers `402 Payment Required`. The client signs a USDC transfer
authorization (EIP-3009) and retries. Settlement goes through the Coinbase facilitator, so your wallet needs
USDC on Base but no ETH. Use a dedicated wallet holding a few dollars. You are charged only for successful
answers.

## Data and disclaimers

Data comes from public-domain or openly licensed sources: SEC EDGAR, FRED public series, US Treasury, OFAC,
NWS, openFDA, NHTSA, Eurostat, DefiLlama, Sourcify and public blockchain RPC. Reports are automated heuristics,
not financial, legal or security advice.

MIT licensed.
