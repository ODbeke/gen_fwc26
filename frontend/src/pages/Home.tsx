import { BrainCircuit, Trophy, Users } from "lucide-react";
import { Squad } from "./Squad";

interface HomeProps {
  address: string;
}

export function Home({ address }: HomeProps) {
  return (
    <div>
      <section className="relative min-h-[440px] overflow-hidden border-b border-line bg-ink md:min-h-[620px] xl:min-h-[min(56vw,920px)]">
        <img src="/world-cup-mascots.jpeg" alt="World Cup 2026 mascots celebrating on a stadium pitch" className="absolute inset-0 h-full w-full object-cover object-top" />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(5,9,17,0.82)_0%,rgba(5,9,17,0.5)_42%,rgba(5,9,17,0.14)_74%),linear-gradient(0deg,rgba(13,17,23,0.82)_0%,rgba(13,17,23,0.05)_36%)]" />
        <div className="relative z-10 flex min-h-[440px] max-w-7xl flex-col justify-end px-4 pb-8 pt-16 md:min-h-[620px] md:pb-10 xl:min-h-[min(56vw,920px)]">
          <div className="flex flex-wrap items-center gap-3 text-sm font-semibold text-gold">
            <span className="inline-flex items-center gap-2"><Trophy className="h-4 w-4" /> Fantasy World Cup 2026</span>
            <span>Free entry on GenLayer Studionet</span>
          </div>
          <h1 className="mt-3 max-w-3xl text-4xl font-black leading-tight text-white md:text-6xl">Fantasy World Cup</h1>
          <p className="mt-3 max-w-2xl text-base font-medium text-slate-100 md:text-lg">Build your squad, chase the golden awards, and let GenLayer validators settle the football drama.</p>
        </div>
      </section>
      <section className="border-b border-line bg-ink px-4 py-4">
        <div className="grid max-w-7xl gap-3 md:grid-cols-3">
          <div className="rounded border border-line bg-panel p-4"><Users className="mb-2 h-5 w-5 text-gold" />15-player squads, FPL-grade rules.</div>
          <div className="rounded border border-line bg-panel p-4"><BrainCircuit className="mb-2 h-5 w-5 text-gold" />AI validators settle live match data.</div>
          <div className="rounded border border-line bg-panel p-4"><Trophy className="mb-2 h-5 w-5 text-gold" />Golden awards power the Hero chip.</div>
        </div>
      </section>
      <Squad address={address} />
    </div>
  );
}
