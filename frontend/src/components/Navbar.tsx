import { Trophy } from "lucide-react";

const tabs = ["Home", "Squad", "Transfers", "Chips", "Fixtures", "Leaderboard", "Profile"] as const;
export type Page = (typeof tabs)[number];

interface NavbarProps {
  active: Page;
  onChange: (page: Page) => void;
}

export function Navbar({ active, onChange }: NavbarProps) {
  return (
    <nav className="flex flex-wrap items-center gap-2 border-b border-line bg-ink/95 px-4 py-3">
      <div className="mr-4 flex items-center gap-2 font-semibold">
        <Trophy className="h-5 w-5 text-gold" aria-hidden="true" />
        <span>FWC 2026</span>
      </div>
      {tabs.map((tab) => (
        <button
          key={tab}
          type="button"
          onClick={() => onChange(tab)}
          className={`focus-ring rounded px-3 py-2 text-sm ${active === tab ? "bg-gold text-ink" : "text-slate-300 hover:bg-panel"}`}
          aria-current={active === tab ? "page" : undefined}
        >
          {tab}
        </button>
      ))}
    </nav>
  );
}
