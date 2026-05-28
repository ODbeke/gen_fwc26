import { POINTS, type Position } from "./constants";

export interface PlayerMatchStats {
  minutes: number;
  goals: number;
  assists: number;
  cleanSheet: boolean;
  saves: number;
  goalsConceded: number;
  yellowCards: number;
  redCards: number;
  ownGoals: number;
  penaltyMisses: number;
  penaltySaves: number;
  defensiveContributions: number;
  bonusRank?: 1 | 2 | 3;
  shootoutScored: number;
  shootoutMissed: number;
}

export interface PointsBreakdown {
  breakdown: Record<string, number>;
  total: number;
}

export function computePlayerPoints(
  stats: PlayerMatchStats,
  position: Position,
  isCaptain: boolean,
  isTripleCaptain: boolean,
  isKnockout: boolean,
  isFinal: boolean,
): PointsBreakdown {
  const breakdown: Record<string, number> = {};
  const add = (key: string, value: number) => {
    if (value !== 0) breakdown[key] = (breakdown[key] ?? 0) + value;
  };

  add("minutes", stats.minutes >= 60 ? POINTS.played_ge60 : stats.minutes > 0 ? POINTS.played_lt60 : 0);
  const goalKey = position === "GK" ? "goal_gk" : position === "DEF" ? "goal_def" : position === "MID" ? "goal_mid" : "goal_fwd";
  add("goals", stats.goals * POINTS[goalKey]);
  add("assists", stats.assists * POINTS.assist);
  const actionExtra = isFinal ? POINTS.final_extra : isKnockout ? POINTS.knockout_extra : 0;
  add("knockoutFinalExtra", (stats.goals + stats.assists) * actionExtra);
  if (stats.cleanSheet && (position === "GK" || position === "DEF")) add("cleanSheet", POINTS.clean_sheet_gk_def);
  if (stats.cleanSheet && position === "MID") add("cleanSheet", POINTS.clean_sheet_mid);
  if (position === "GK") add("saves", Math.floor(stats.saves / 3) * POINTS.save_3);
  if (position === "GK" || position === "DEF") add("goalsConceded", Math.floor(stats.goalsConceded / 2) * POINTS.goals_conceded_2);
  add("yellowCards", stats.yellowCards * POINTS.yellow_card);
  add("redCards", stats.redCards * POINTS.red_card);
  add("ownGoals", stats.ownGoals * POINTS.own_goal);
  add("penaltyMisses", stats.penaltyMisses * POINTS.penalty_miss);
  add("penaltySaves", stats.penaltySaves * POINTS.penalty_save);
  if (position === "DEF" && stats.defensiveContributions >= 10) add("defensiveContributions", POINTS.defensive_contrib_def);
  if ((position === "MID" || position === "FWD") && stats.defensiveContributions >= 12) add("defensiveContributions", POINTS.defensive_contrib_mid_fwd);
  if (stats.bonusRank === 1) add("bonus", POINTS.bonus_1st);
  if (stats.bonusRank === 2) add("bonus", POINTS.bonus_2nd);
  if (stats.bonusRank === 3) add("bonus", POINTS.bonus_3rd);
  add("shootoutScored", stats.shootoutScored * POINTS.penalty_shootout_scored);
  add("shootoutMissed", stats.shootoutMissed * POINTS.penalty_shootout_missed);

  const rawTotal = Object.values(breakdown).reduce((sum, value) => sum + value, 0);
  const multiplier = isCaptain ? (isTripleCaptain ? 3 : 2) : 1;
  if (multiplier > 1) breakdown.captainMultiplier = rawTotal * (multiplier - 1);
  return { breakdown, total: rawTotal * multiplier };
}
