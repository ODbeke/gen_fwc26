import { logger } from "./logger";

const RPC_URL = import.meta.env.VITE_GENLAYER_RPC_URL ?? "https://studio.genlayer.com/api";
const CONTRACT_ADDRESS = import.meta.env.VITE_FWC_CONTRACT_ADDRESS ?? "";

interface RpcResponse<T> {
  result?: T;
  error?: { message?: string };
}

async function rpc<T>(method: string, params: unknown[]): Promise<T> {
  const response = await fetch(RPC_URL, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: Date.now(), method, params }),
  });
  const body = (await response.json()) as RpcResponse<T>;
  if (body.error) throw new Error(body.error.message ?? "GenLayer RPC error");
  if (body.result === undefined) throw new Error("GenLayer RPC returned no result");
  return body.result;
}

export async function callView<T = unknown>(method: string, args: unknown[] = []): Promise<T> {
  try {
    return await rpc<T>("gen_call", [{ to: CONTRACT_ADDRESS, method, args }]);
  } catch (error) {
    logger.error(`view ${method} failed`, error);
    throw error;
  }
}

export async function callWrite(method: string, args: unknown[] = [], valueWei?: bigint): Promise<string> {
  try {
    return await rpc<string>("gen_sendTransaction", [{ to: CONTRACT_ADDRESS, method, args, value: valueWei?.toString() ?? "0" }]);
  } catch (error) {
    logger.error(`write ${method} failed`, error);
    throw error;
  }
}
