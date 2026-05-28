import { formatPrice, STARTING_BUDGET } from "../lib/constants";

interface BudgetBarProps {
  spent: number;
  remaining: number;
}

export function BudgetBar({ spent, remaining }: BudgetBarProps) {
  const percent = Math.min(100, (spent / STARTING_BUDGET) * 100);
  return (
    <div className="rounded border border-line bg-panel p-4">
      <div className="mb-2 flex items-center justify-between text-sm">
        <span>Budget</span>
        <span className="font-semibold text-gold">{formatPrice(remaining)} left</span>
      </div>
      <div className="h-3 rounded bg-slate-950">
        <div className="h-3 rounded bg-gold" style={{ width: `${percent}%` }} />
      </div>
      <div className="mt-2 flex justify-between text-xs text-slate-400">
        <span>Spent {formatPrice(spent)}</span>
        <span>Savings {formatPrice(remaining)}</span>
      </div>
    </div>
  );
}
