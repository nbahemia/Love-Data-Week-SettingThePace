import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw/NCAA Women's Basketball Data Files 2026")

games = pd.read_parquet(
    DATA_DIR / "games.parquet",
    columns=["game_id", "season"]
)

team_box = pd.read_parquet(
    DATA_DIR / "team_box.parquet",
    columns=["game_id", "season", "team_id"]
)

# Total games by season
game_counts = (
    games.groupby("season")["game_id"]
    .nunique()
    .rename("total_games")
)

# Games represented in team_box
box_game_counts = (
    team_box.groupby("season")["game_id"]
    .nunique()
    .rename("games_with_team_box")
)

# Games with exactly two team rows
rows_per_game = (
    team_box.groupby(["season", "game_id"])
    .size()
    .reset_index(name="team_rows")
)

complete_counts = (
    rows_per_game[rows_per_game["team_rows"] == 2]
    .groupby("season")["game_id"]
    .nunique()
    .rename("complete_team_box_games")
)

coverage = pd.concat(
    [game_counts, box_game_counts, complete_counts],
    axis=1
).fillna(0)

coverage["coverage_pct"] = (
    coverage["complete_team_box_games"]
    / coverage["total_games"]
    * 100
)

coverage["team_box_rows"] = (
    team_box.groupby("season").size()
)

print("\nTEAM BOX COVERAGE BY SEASON\n")
print(coverage.to_string(
    formatters={"coverage_pct": "{:.1f}%".format}
))