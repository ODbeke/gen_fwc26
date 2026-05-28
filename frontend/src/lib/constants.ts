export const MAX_PLAYERS = 15;
export const STARTING_BUDGET = 1000;
export const MAX_PER_COUNTRY = 3;
export const TRANSFER_COST_PTS = 4;

export const POSITION_COLORS = {
  GK: "#FFD700",
  DEF: "#22c55e",
  MID: "#38bdf8",
  FWD: "#ef4444",
} as const;

export const FLAGS: Record<string, string> = {
  Argentina: "🇦🇷",
  Australia: "🇦🇺",
  Belgium: "🇧🇪",
  "Bosnia-Herzegovina": "🇧🇦",
  Brazil: "🇧🇷",
  Canada: "🇨🇦",
  "Cape Verde": "🇨🇻",
  Colombia: "🇨🇴",
  Croatia: "🇭🇷",
  Curaçao: "🇨🇼",
  England: "🏴",
  France: "🇫🇷",
  Germany: "🇩🇪",
  Ghana: "🇬🇭",
  Haiti: "🇭🇹",
  "Ivory Coast": "🇨🇮",
  Japan: "🇯🇵",
  Mexico: "🇲🇽",
  Morocco: "🇲🇦",
  Netherlands: "🇳🇱",
  "New Zealand": "🇳🇿",
  Norway: "🇳🇴",
  Portugal: "🇵🇹",
  Qatar: "🇶🇦",
  "Saudi Arabia": "🇸🇦",
  Scotland: "🏴",
  Senegal: "🇸🇳",
  "South Korea": "🇰🇷",
  Spain: "🇪🇸",
  Sweden: "🇸🇪",
  Switzerland: "🇨🇭",
  "United States": "🇺🇸",
  Uruguay: "🇺🇾",
};

export const POINTS = {
  played_lt60: 1,
  played_ge60: 2,
  goal_gk: 10,
  goal_def: 6,
  goal_mid: 5,
  goal_fwd: 4,
  assist: 3,
  clean_sheet_gk_def: 4,
  clean_sheet_mid: 1,
  save_3: 1,
  penalty_save: 5,
  goals_conceded_2: -1,
  yellow_card: -1,
  red_card: -3,
  own_goal: -2,
  penalty_miss: -2,
  bonus_1st: 3,
  bonus_2nd: 2,
  bonus_3rd: 1,
  knockout_extra: 1,
  final_extra: 2,
  defensive_contrib_def: 2,
  defensive_contrib_mid_fwd: 2,
  penalty_shootout_scored: 2,
  penalty_shootout_missed: -2,
};

export type Position = keyof typeof POSITION_COLORS;

export interface Player {
  player_id: string;
  name: string;
  country: string;
  position: Position;
  price: number;
  pending?: boolean;
}

export interface Team {
  owner: string;
  username?: string;
  team_name: string;
  budget_remaining: number;
  player_ids: string[];
  captain_id: string;
  vice_captain_id: string;
  total_points: number;
  transfers_available: number;
  chips: {
    wildcard_gw: number;
    bench_boost_gw: number;
    triple_captain_gw: number;
    free_hit_gw: number;
    hero_player_id: string;
    hero_bonus_awarded: boolean;
  };
}

export interface LeaderboardEntry {
  owner: string;
  username?: string;
  team_name: string;
  total_points: number;
  gameweek_points?: number;
}

export const formatPrice = (price: number) => `${(price / 10).toFixed(1)}m`;
export const flagFor = (country: string) => FLAGS[country] ?? "🏳";
