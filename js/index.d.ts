export declare const BASE_URL: string;
export declare const DEFAULT_TOOLS: string[];

export interface ToolSpec {
  name: string;
  route: string;
  price_usd: number;
  title: string;
  description: string;
  tags: string[];
  input_schema: Record<string, unknown>;
}

export interface ToolSelection {
  names?: string[];
  tags?: string[];
  all?: boolean;
}

export interface ClientOptions {
  /** EVM private key holding USDC on Base; defaults to X402_PRIVATE_KEY. Without one, the free tier is used. */
  privateKey?: `0x${string}` | string | null;
  baseUrl?: string;
  network?: string;
}

export declare class X402ToolError extends Error {
  status?: number;
  constructor(message: string, status?: number);
}

export declare class FreeQuotaExceeded extends X402ToolError {}

export declare function loadCatalog(): ToolSpec[];

export declare class X402DataTools {
  constructor(options?: ClientOptions);
  readonly paid: boolean;
  catalog: Map<string, ToolSpec>;
  tools(selection?: ToolSelection): ToolSpec[];
  search(text: string, limit?: number): ToolSpec[];
  call<T = unknown>(name: string, args?: Record<string, unknown>): Promise<T>;
}

export declare function openaiTools(selection?: ToolSelection, client?: X402DataTools): Array<Record<string, unknown>>;
export declare function anthropicTools(selection?: ToolSelection, client?: X402DataTools): Array<Record<string, unknown>>;
export declare function runToolCall(name: string, args: string | Record<string, unknown> | null,
                                    client?: X402DataTools): Promise<string>;
