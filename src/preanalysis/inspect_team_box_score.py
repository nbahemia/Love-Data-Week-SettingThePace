import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw/NCAA Women's Basketball Data Files 2026")

cols = [
    "season",
    "game_id",
    "game_date",
    "team_id",
    "team_location",
    "team_score",
    "field_goals_attempted",
    "free_throws_attempted",
    "offensive_rebounds",
    "team_turnovers",
    "total_turnovers",
    "turnovers",
]

df = pd.read_parquet(
    DATA_DIR / "team_box.parquet",
    columns=cols
)

df = df[df["season"].between(2022, 2026)]

print("\nSAMPLE\n")
print(df.head(10).to_string(index=False))

print("\nNON-NULL PERCENTAGE\n")
print(
    (df.notna().mean() * 100)
    .round(2)
    .to_string()
)

print("\nNON-ZERO PERCENTAGE\n")
for col in [
    "field_goals_attempted",
    "free_throws_attempted",
    "offensive_rebounds",
    "team_turnovers",
    "total_turnovers",
    "turnovers",
]:
    numeric = pd.to_numeric(df[col], errors="coerce")
    print(f"{col:25} {(numeric.fillna(0) != 0).mean() * 100:.2f}%")