import { Sparkles } from "lucide-react";

interface ChipCardProps {
  name: string;
  description: string;
  used?: boolean;
  onActivate?: () => void;
}

export function ChipCard({ name, description, used = false, onActivate }: ChipCardProps) {
  return (
    <div className={`rounded border p-3 ${used ? "border-slate-700 bg-slate-900 text-slate-500" : "border-line bg-panel"}`}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Sparkles className="h-4 w-4 text-gold" aria-hidden="true" />
          {name}
        </div>
        <button
          type="button"
          disabled={used}
          onClick={onActivate}
          className="focus-ring rounded bg-gold px-2 py-1 text-xs font-bold text-ink disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {used ? "Used" : "Activate"}
        </button>
      </div>
      <p className="mt-2 text-xs leading-5 text-slate-400">{description}</p>
    </div>
  );
}
