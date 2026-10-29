// Vercel AI SDK tools: generateText({ model, tools: aiSdkTools(), ... })
import { jsonSchema, tool } from "ai";
import { X402DataTools, X402ToolError } from "./index.js";

export function aiSdkTools(opts = {}, client = new X402DataTools(opts)) {
  const out = {};
  for (const s of client.tools(opts)) {
    out[s.name] = tool({
      description: `${s.description} ($${s.price_usd} per call)`,
      inputSchema: jsonSchema(s.input_schema),
      execute: async (args) => {
        try {
          return await client.call(s.name, args);
        } catch (e) {
          if (e instanceof X402ToolError) return { error: e.message, status: e.status };
          throw e;
        }
      },
    });
  }
  return out;
}
