import { PointsBreakdown } from "../components/PointsBreakdown";

export function MatchDetail() {
  return (
    <div className="space-y-4 p-4">
      <div className="rounded border border-line bg-panel p-6 text-center">
        <div className="text-sm text-slate-400">Validators reached strict equality</div>
        <div className="mt-2 text-4xl font-black text-gold">England 2-0 Spain</div>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <PointsBreakdown rows={[{ label: "Goals", points: 5 }, { label: "Assist", points: 3 }, { label: "Bonus", points: 3 }]} />
        <PointsBreakdown rows={[{ label: "Clean sheet", points: 4 }, { label: "Saves", points: 2 }]} />
        <PointsBreakdown rows={[{ label: "Yellow card", points: -1 }, { label: "Penalty miss", points: -2 }]} />
      </div>
    </div>
  );
}
