# x402-data-tools (JavaScript)

184 data tools for AI agents, each paid per call in USDC on Base over [x402](https://x402.org).
You don't need an account or an API key, and there is a free tier of 20 calls a day.

```bash
npm i x402-data-tools        # add `ai` too for Vercel AI SDK tools
```

```js
import { X402DataTools } from "x402-data-tools";

const tools = new X402DataTools();                          // free tier: 20 calls/day per IP
console.log((await tools.call("macro_briefing")).signals);

const paid = new X402DataTools({ privateKey: "0x..." });    // or set X402_PRIVATE_KEY
const report = await paid.call("company_financial_health_report", { company: "NVDA" });
console.log(report.grade, report.verdict);
```

## Vercel AI SDK

```js
import { generateText } from "ai";
import { aiSdkTools } from "x402-data-tools/ai-sdk";

const { text } = await generateText({
  model,
  tools: aiSdkTools({ tags: ["report"] }),   // or { names: [...] }, { all: true }; default: a dozen tools
  prompt: "Is 0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed on Base safe to list?",
});
```

## OpenAI / Anthropic function calling

```js
import { openaiTools, anthropicTools, runToolCall } from "x402-data-tools";
const tools = openaiTools();   // pass to chat.completions.create({ tools })
const content = await runToolCall(call.function.name, call.function.arguments);
```

For the full tool list, notes on wallets and the MCP endpoint, see the [repository README](https://github.com/shadowdomnic/x402-data-tools).

MIT licensed.
