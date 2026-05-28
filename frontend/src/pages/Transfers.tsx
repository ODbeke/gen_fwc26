import { Squad } from "./Squad";

interface TransfersProps {
  address: string;
}

export function Transfers({ address }: TransfersProps) {
  return <Squad address={address} />;
}
