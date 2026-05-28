import { useState } from "react";
import { useAccount } from "wagmi";
import { Navbar, type Page } from "./components/Navbar";
import { WalletConnect } from "./components/WalletConnect";
import { Chips } from "./pages/Chips";
import { Fixtures } from "./pages/Fixtures";
import { Home } from "./pages/Home";
import { Leaderboard } from "./pages/Leaderboard";
import { MatchDetail } from "./pages/MatchDetail";
import { Profile } from "./pages/Profile";
import { Squad } from "./pages/Squad";
import { Transfers } from "./pages/Transfers";
import { useUiStore } from "./store/uiStore";

export default function App() {
  const [page, setPage] = useState<Page>("Home");
  const { address } = useAccount();
  const notification = useUiStore((state) => state.notification);
  const owner = address ?? "";

  return (
    <div className="min-h-screen bg-ink text-slate-50">
      <header className="sticky top-0 z-40 border-b border-line bg-ink">
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
          <Navbar active={page} onChange={setPage} />
          <WalletConnect />
        </div>
      </header>
      {notification && <div className="border-b border-gold/40 bg-gold/10 px-4 py-2 text-sm text-gold">{notification}</div>}
      <main>
        {page === "Home" && <Home address={owner} />}
        {page === "Squad" && <Squad address={owner} />}
        {page === "Transfers" && <Transfers address={owner} />}
        {page === "Chips" && <Chips />}
        {page === "Fixtures" && <Fixtures />}
        {page === "Leaderboard" && <Leaderboard address={owner} />}
        {page === "Profile" && <Profile address={owner} />}
        {page === "Home" ? null : page === "Fixtures" ? <MatchDetail /> : null}
      </main>
      <footer className="border-t border-line px-4 py-4 text-xs text-slate-400">
        GenLayer Studionet · RPC https://studio.genlayer.com/api · Chain 61999 · Currency GEN
      </footer>
    </div>
  );
}
