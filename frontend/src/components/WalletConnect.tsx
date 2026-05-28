import { Wallet } from "lucide-react";
import { useAccount, useConnect, useDisconnect } from "wagmi";

const shortAddress = (address: string) => `${address.slice(0, 6)}...${address.slice(-4)}`;

export function WalletConnect() {
  const { address, isConnected, chain } = useAccount();
  const { connect, connectors, isPending } = useConnect();
  const { disconnect } = useDisconnect();
  const injected = connectors[0];

  return (
    <div className="flex min-w-[260px] items-center gap-2 rounded border border-line bg-panel px-3 py-2 text-sm">
      <Wallet className="h-4 w-4 text-gold" aria-hidden="true" />
      {isConnected && address ? (
        <>
          <div className="min-w-0 flex-1">
            <div className="truncate font-semibold">{shortAddress(address)}</div>
            <div className="truncate text-xs text-slate-400">{chain?.name ?? "Connected wallet"}</div>
          </div>
          <button type="button" onClick={() => disconnect()} className="focus-ring rounded bg-ink px-3 py-2 text-xs font-semibold">
            Disconnect
          </button>
        </>
      ) : (
        <button type="button" disabled={!injected || isPending} onClick={() => injected && connect({ connector: injected })} className="focus-ring w-full rounded bg-gold px-3 py-2 font-bold text-ink disabled:bg-slate-700 disabled:text-slate-400">
          {isPending ? "Connecting..." : "Connect wallet"}
        </button>
      )}
    </div>
  );
}
