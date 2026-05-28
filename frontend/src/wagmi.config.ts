import { createConfig, http } from "wagmi";
import { injected } from "wagmi/connectors";
import { defineChain } from "viem";

export const genLayerStudionet = defineChain({
  id: 61999,
  name: "GenLayer Studionet",
  nativeCurrency: { name: "GEN", symbol: "GEN", decimals: 18 },
  rpcUrls: {
    default: { http: [import.meta.env.VITE_GENLAYER_RPC_URL ?? "https://studio.genlayer.com/api"] },
  },
  blockExplorers: {
    default: { name: "GenLayer Explorer", url: "https://explorer-studio.genlayer.com" },
  },
});

export const config = createConfig({
  chains: [genLayerStudionet],
  connectors: [injected()],
  transports: {
    [genLayerStudionet.id]: http(),
  },
});
