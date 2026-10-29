import assert from "node:assert/strict";
import test from "node:test";

import { DEFAULT_TOOLS, FreeQuotaExceeded, X402DataTools, anthropicTools, openaiTools } from "../index.js";

test("catalog and defaults", () => {
  const t = new X402DataTools({ privateKey: null });
  assert.ok(t.catalog.size >= 180);
  assert.deepEqual(t.tools().map((s) => s.name), DEFAULT_TOOLS);
  assert.ok(t.tools({ tags: ["report"] }).some((s) => s.name === "macro_briefing"));
  assert.ok(t.search("yield curve").length > 0);
  assert.equal(openaiTools({ names: ["macro_briefing"] })[0].function.name, "macro_briefing");
  assert.equal(anthropicTools({ names: ["macro_briefing"] })[0].input_schema.type, "object");
});

test("free call and quota", async () => {
  const real = globalThis.fetch;
  let text = '{"ok":1}';
  globalThis.fetch = async () => new Response(JSON.stringify({ jsonrpc: "2.0", id: 1,
    result: { content: [{ type: "text", text }], isError: false } }));
  try {
    const t = new X402DataTools({ privateKey: null });
    assert.deepEqual(await t.call("macro_briefing"), { ok: 1 });
    text = "Free limit of 20 calls per day reached.";
    await assert.rejects(t.call("macro_briefing"), FreeQuotaExceeded);
  } finally {
    globalThis.fetch = real;
  }
});
