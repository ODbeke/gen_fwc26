from __future__ import annotations

WEI_PER_GEN = 10**18

COUNTRY_FLAGS = {
    "Argentina": "🇦🇷",
    "Australia": "🇦🇺",
    "Belgium": "🇧🇪",
    "Bosnia-Herzegovina": "🇧🇦",
    "Brazil": "🇧🇷",
    "Canada": "🇨🇦",
    "Cape Verde": "🇨🇻",
    "Colombia": "🇨🇴",
    "Croatia": "🇭🇷",
    "Curaçao": "🇨🇼",
    "England": "🏴",
    "France": "🇫🇷",
    "Germany": "🇩🇪",
    "Ghana": "🇬🇭",
    "Haiti": "🇭🇹",
    "Ivory Coast": "🇨🇮",
    "Japan": "🇯🇵",
    "Mexico": "🇲🇽",
    "Morocco": "🇲🇦",
    "Netherlands": "🇳🇱",
    "New Zealand": "🇳🇿",
    "Norway": "🇳🇴",
    "Portugal": "🇵🇹",
    "Qatar": "🇶🇦",
    "Saudi Arabia": "🇸🇦",
    "Scotland": "🏴",
    "Senegal": "🇸🇳",
    "South Korea": "🇰🇷",
    "Spain": "🇪🇸",
    "Sweden": "🇸🇪",
    "Switzerland": "🇨🇭",
    "United States": "🇺🇸",
    "Uruguay": "🇺🇾",
}

POSITION_COLORS = {
    "GK": "#FFD700",
    "DEF": "#22c55e",
    "MID": "#38bdf8",
    "FWD": "#ef4444",
}


def wei_to_gen(wei: int) -> float:
    """Convert wei to GEN."""
    return wei / WEI_PER_GEN


def gen_to_wei(gen: float) -> int:
    """Convert GEN to wei."""
    return int(gen * WEI_PER_GEN)


def format_price(price_int: int) -> str:
    """Format a contract price integer as an FWC millions label."""
    return f"{price_int / 10:.1f}m"


def position_color(position: str) -> str:
    """Return the UI color for a fantasy position."""
    return POSITION_COLORS.get(position, "#94a3b8")


def flag_emoji(country: str) -> str:
    """Return a flag emoji for a country name."""
    return COUNTRY_FLAGS.get(country, "🏳")
