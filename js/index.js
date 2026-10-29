// Client for the x402 data tools at https://bess-x402.onrender.com.
// Paid: pass an EVM private key (or set X402_PRIVATE_KEY) holding USDC on Base; each call pays its price
// over x402, no account or API key. Free: without a key, calls go through the MCP endpoint (20 calls/day per IP).
import { readFileSync } from "node:fs";

const catalogData = JSON.parse(readFileSync(new URL("./catalog.json", import.meta.url), "utf8"));

export const BASE_URL = "https://bess-x402.onrender.com";
export const DEFAULT_TOOLS = [
  "token_due_diligence_report", "wallet_profile_report", "company_financial_health_report",
  "website_audit_report", "macro_briefing", "read_web_page", "us_company_fundamentals", "crypto_token_prices",
  "evm_gas_fees", "fred_series", "prediction_markets_search", "weather_forecast",
];

export class X402ToolError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "X402ToolError";
    this.status = status;
  }
}

export class FreeQuotaExceeded extends X402ToolError {
  constructor(message) {
    super(message, 402);
    this.name = "FreeQuotaExceeded";
  }
}

export function loadCatalog() {
  return catalogData.tools;
}

export class X402DataTools {
  constructor({ privateKey, baseUrl, network = "eip155:8453" } = {}) {
    this.privateKey = privateKey ?? process.env.X402_PRIVATE_KEY ?? null;
    this.baseUrl = (baseUrl ?? process.env.X402_DATA_TOOLS_URL ?? BASE_URL).replace(/\/$/, "");
    this.network = network;
    this.catalog = new Map(loadCatalog().map((t) => [t.name, t]));
    this._fetch = null;
  }

  get paid() {
    return Boolean(this.privateKey);
  }

  tools({ names, tags, all = false } = {}) {
    if (all) return [...this.catalog.values()];
    if (tags?.length) return [...this.catalog.values()].filter((t) => t.tags.some((x) => tags.includes(x)));
    return (names ?? DEFAULT_TOOLS).map((n) => {
      const t = this.catalog.get(n);
      if (!t) throw new X402ToolError(`unknown tool ${n}`, 400);
      return t;
    });
  }

  search(text, limit = 10) {
    const words = text.toLowerCase().split(/\s+/).filter(Boolean);
    return [...this.catalog.values()]
      .filter((t) => {
        const hay = `${t.name} ${t.title} ${t.tags.join(" ")} ${t.description}`.toLowerCase();
        return words.every((w) => hay.includes(w));
      })
      .slice(0, limit);
  }

  async call(name, args = {}) {
    const spec = this.catalog.get(name);
    if (!spec) throw new X402ToolError(`unknown tool ${name}`, 400);
    const clean = Object.fromEntries(Object.entries(args).filter(([, v]) => v !== undefined && v !== null));
    return this.paid ? this._paidCall(spec, clean) : this._freeCall(spec, clean);
  }

  async _payingFetch() {
    if (!this._fetch) {
      const [{ wrapFetchWithPaymentFromConfig }, { ExactEvmScheme }, { privateKeyToAccount }] = await Promise.all([
        import("@x402/fetch"), import("@x402/evm"), import("viem/accounts"),
      ]);
      const account = privateKeyToAccount(this.privateKey);
      this._fetch = wrapFetchWithPaymentFromConfig(fetch, {
        schemes: [{ network: this.network, client: new ExactEvmScheme(account) }],
      });
    }
    return this._fetch;
  }

  async _paidCall(spec, args) {
    const url = new URL(this.baseUrl + spec.route);
    for (const [k, v] of Object.entries(args)) url.searchParams.set(k, String(v));
    const r = await (await this._payingFetch())(url, { method: "GET" });
    const text = await r.text();
    if (!r.ok) {
      let detail = text;
      try { detail = JSON.parse(text).detail ?? text; } catch {}
      throw new X402ToolError(`${spec.name}: ${typeof detail === "string" ? detail : JSON.stringify(detail)}`, r.status);
    }
    return JSON.parse(text);
  }

  async _freeCall(spec, args) {
    const r = await fetch(this.baseUrl + "/mcp", {
      method: "POST",
      headers: { "content-type": "application/json", accept: "application/json, text/event-stream" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name: spec.name, arguments: args } }),
    });
    if (!r.ok) throw new X402ToolError(`${spec.name}: MCP endpoint answered ${r.status}`, r.status);
    const msg = await r.json();
    if (msg.error) throw new X402ToolError(`${spec.name}: ${msg.error.message}`, 400);
    const text = (msg.result.content ?? []).map((c) => c.text ?? "").join("");
    if (msg.result.isError) throw new X402ToolError(`${spec.name}: ${text}`, 400);
    try {
      return JSON.parse(text);
    } catch {
      if (text.startsWith("Free limit")) {
        throw new FreeQuotaExceeded(`${text} Set X402_PRIVATE_KEY (a wallet with USDC on Base) to keep going.`);
      }
      return text;
    }
  }
}

/** Function-calling definitions for the OpenAI Chat Completions / Responses API. */
export function openaiTools(opts = {}, client = new X402DataTools()) {
  return client.tools(opts).map((s) => ({
    type: "function",
    function: { name: s.name, description: s.description.slice(0, 1024), parameters: s.input_schema },
  }));
}

/** Tool definitions for the Anthropic Messages API. */
export function anthropicTools(opts = {}, client = new X402DataTools()) {
  return client.tools(opts).map((s) => ({ name: s.name, description: s.description, input_schema: s.input_schema }));
}

/** Run one model tool call and return the string content for the tool result message. */
export async function runToolCall(name, args, client = new X402DataTools()) {
  const parsed = typeof args === "string" ? (args ? JSON.parse(args) : {}) : (args ?? {});
  try {
    const v = await client.call(name, parsed);
    return typeof v === "string" ? v : JSON.stringify(v);
  } catch (e) {
    return JSON.stringify({ error: String(e.message ?? e), status: e.status ?? null });
  }
}
