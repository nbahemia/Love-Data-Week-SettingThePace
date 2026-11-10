from pathlib import Path

import duckdb


# --------------------------------------------------
# Paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = ROOT / "data" / "raw" / "NCAA Women's Basketball Data Files 2026"
PROCESSED_DIR = ROOT / "data" / "processed"
SQL_DIR = ROOT / "src" / "features"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def sql_path(path: Path) -> str:
    """Convert a Path to a DuckDB-safe SQL string."""
    return path.as_posix().replace("'", "''")


# --------------------------------------------------
# DuckDB connection
# --------------------------------------------------

con = duckdb.connect()


# --------------------------------------------------
# 1. Register raw Parquet files as views
# --------------------------------------------------

team_box_path = sql_path(RAW_DIR / "team_box.parquet")
games_path = sql_path(RAW_DIR / "games.parquet")
play_by_play_path = sql_path(RAW_DIR / "play_by_play.parquet")

con.execute(
    f"""
    CREATE VIEW team_box AS
    SELECT *
    FROM read_parquet('{team_box_path}')
    """
)

con.execute(
    f"""
    CREATE VIEW games AS
    SELECT *
    FROM read_parquet('{games_path}')
    """
)

con.execute(
    f"""
    CREATE VIEW play_by_play AS
    SELECT *
    FROM read_parquet('{play_by_play_path}')
    """
)


# --------------------------------------------------
# 2. Build team-level possession estimates
# --------------------------------------------------

possessions_sql = (SQL_DIR / "possessions.sql").read_text()

team_possessions_output = PROCESSED_DIR / "team_possessions.parquet"
team_possessions_path = sql_path(team_possessions_output)

con.execute(
    f"""
    COPY (
        {possessions_sql.rstrip().rstrip(";")}
    )
    TO '{team_possessions_path}'
    (FORMAT PARQUET)
    """
)


# --------------------------------------------------
# 3. Register team_possessions as a DuckDB view
#
# IMPORTANT:
# game_pace.sql references "team_possessions",
# so this must happen BEFORE game_pace.sql runs.
# --------------------------------------------------

con.execute(
    f"""
    CREATE VIEW team_possessions AS
    SELECT *
    FROM read_parquet('{team_possessions_path}')
    """
)


# --------------------------------------------------
# 4. Build OT-adjusted game pace
# --------------------------------------------------

game_pace_sql = (SQL_DIR / "game_pace.sql").read_text()

game_pace_output = PROCESSED_DIR / "game_pace.parquet"
game_pace_path = sql_path(game_pace_output)

con.execute(
    f"""
    COPY (
        {game_pace_sql.rstrip().rstrip(";")}
    )
    TO '{game_pace_path}'
    (FORMAT PARQUET)
    """
)


# --------------------------------------------------
# 5. Register game_pace as a DuckDB view
# --------------------------------------------------

con.execute(
    f"""
    CREATE VIEW game_pace AS
    SELECT *
    FROM read_parquet('{game_pace_path}')
    """
)


# --------------------------------------------------
# 6. Pipeline summary
# --------------------------------------------------

team_rows = con.execute(
    """
    SELECT COUNT(*)
    FROM team_possessions
    """
).fetchone()[0]

team_games = con.execute(
    """
    SELECT COUNT(DISTINCT game_id)
    FROM team_possessions
    """
).fetchone()[0]

pace_games = con.execute(
    """
    SELECT COUNT(*)
    FROM game_pace
    """
).fetchone()[0]

ot_games = con.execute(
    """
    SELECT COUNT(*)
    FROM game_pace
    WHERE status_period > 4
    """
).fetchone()[0]


print(
    f"Created team_possessions.parquet: "
    f"{team_rows:,} rows across {team_games:,} games"
)

print(
    f"Created game_pace.parquet: "
    f"{pace_games:,} games"
)

print(
    f"Overtime games normalized: "
    f"{ot_games:,}"
)


# --------------------------------------------------
# 7. Close connection
# --------------------------------------------------

con.close()