import { Clock } from "lucide-react";

export function CountdownTimer() {
  return (
    <div className="inline-flex items-center gap-2 rounded border border-line bg-panel px-3 py-2 text-sm">
      <Clock className="h-4 w-4 text-gold" aria-hidden="true" />
      <span>Next GW deadline: 17d 04h 12m</span>
    </div>
  );
}
