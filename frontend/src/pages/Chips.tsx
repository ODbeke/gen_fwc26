import { ChipCard } from "../components/ChipCard";

export function Chips() {
  return (
    <div className="grid gap-4 p-4 md:grid-cols-2 xl:grid-cols-3">
      <ChipCard name="Wildcard" description="Unlimited transfers in the selected gameweek and three free transfers banked." />
      <ChipCard name="Bench Boost" description="Bench players count toward your score when the gameweek is settled." />
      <ChipCard name="Triple Captain" description="Your captain scores 3x instead of 2x." />
      <ChipCard name="Free Hit" description="Off-chain v1 squad restore support for one-week tactical swings." />
      <ChipCard name="World Cup Hero" description="Choose one player. If they win Boot, Glove, or Ball, gain +10." />
    </div>
  );
}
