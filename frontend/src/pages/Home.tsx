import { BrainCircuit, Trophy, Users } from "lucide-react";
import { Squad } from "./Squad";

interface HomeProps {
  address: string;
}

export function Home({ address }: HomeProps) {
  return (
    <div>
      <section className="border-b border-line bg-[url('/hero-world-cup.svg')] bg-cover bg-center px-4 py-6">
        <div className="max-w-7xl">
          <div className="flex flex-wrap items-center gap-3 text-sm text-gold">
            <span className="inline-flex items-center gap-2"><Trophy className="h-4 w-4" /> Fantasy World Cup 2026</span>
            <span>Free entry on GenLayer Studionet</span>
          </div>
          <h1 className="mt-3 max-w-3xl text-4xl font-black leading-tight md:text-6xl">Fantasy World Cup</h1>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <div className="rounded border border-line bg-ink/80 p-4"><Users className="mb-2 h-5 w-5 text-gold" />15-player squads, FPL-grade rules.</div>
            <div className="rounded border border-line bg-ink/80 p-4"><BrainCircuit className="mb-2 h-5 w-5 text-gold" />AI validators settle live match data.</div>
            <div className="rounded border border-line bg-ink/80 p-4"><Trophy className="mb-2 h-5 w-5 text-gold" />Golden awards power the Hero chip.</div>
          </div>
        </div>
      </section>
      <Squad address={address} />
    </div>
  );
}
