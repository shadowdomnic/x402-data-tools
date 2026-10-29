"""180+ pay-per-call data tools for AI agents: token, wallet, company and website reports, crypto and EVM data,
SEC filings, FRED and Treasury macro data, weather, web pages as Markdown and more. Paid per call in USDC on
Base over x402 (no account or API key), with a free tier of 20 calls a day."""

from .client import (BASE_URL, DEFAULT_TOOLS, FreeQuotaExceeded, ToolSpec, X402DataTools, X402ToolError,
                     load_catalog)

__all__ = ["BASE_URL", "DEFAULT_TOOLS", "FreeQuotaExceeded", "ToolSpec", "X402DataTools", "X402ToolError",
           "load_catalog"]
__version__ = "0.1.0"
