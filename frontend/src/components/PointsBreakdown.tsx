interface PointsBreakdownProps {
  rows: Array<{ label: string; points: number }>;
}

export function PointsBreakdown({ rows }: PointsBreakdownProps) {
  return (
    <div className="rounded border border-line bg-panel p-4">
      <h3 className="text-sm font-semibold">Points Breakdown</h3>
      <div className="mt-3 space-y-2 text-sm">
        {rows.map((row) => (
          <div key={row.label} className="flex justify-between border-b border-line pb-2">
            <span>{row.label}</span>
            <span className={row.points >= 0 ? "text-emerald-300" : "text-red-300"}>{row.points}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
