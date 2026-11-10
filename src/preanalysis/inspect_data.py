import pandas as pd
from pathlib import Path

p = Path("data/raw/NCAA Women's Basketball Data Files 2026")

files = [
    "games.parquet",
    "team_box.parquet",
    "game_box.parquet",
    "play_by_play.parquet",
    "rankings.parquet",
    "teams.parquet",
]

for filename in files:
    df = pd.read_parquet(p / filename)

    if "season" in df.columns:
        seasons = sorted(df["season"].dropna().unique().tolist())
    elif "season_year" in df.columns:
        seasons = sorted(df["season_year"].dropna().unique().tolist())
    else:
        seasons = "N/A"

    print(
        f"{filename}: "
        f"{len(df):,} rows x {len(df.columns)} cols | "
        f"seasons: {seasons}"
    )