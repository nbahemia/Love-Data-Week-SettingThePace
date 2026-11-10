from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "NCAA Women's Basketball Data Files 2026"


def sql_path(path: Path) -> str:
    return path.as_posix().replace("'", "''")


games_path = sql_path(RAW_DIR / "games.parquet")
pbp_path = sql_path(RAW_DIR / "play_by_play.parquet")

con = duckdb.connect()

# --------------------------------------------------
# Check potentially useful columns in games.parquet
# --------------------------------------------------

print("\nGAMES COLUMNS RELATED TO PERIOD / STATUS / OT\n")

columns = con.execute(
    f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{games_path}')
    """
).df()

mask = columns["column_name"].str.lower().str.contains(
    "period|status|detail|overtime|clock|format"
)

print(columns.loc[mask].to_string(index=False))


# --------------------------------------------------
# Distribution of maximum PBP period
# Only analyze our 2022-2026 seasons
# --------------------------------------------------

print("\nMAXIMUM PBP PERIOD BY GAME\n")

period_distribution = con.execute(
    f"""
    WITH game_periods AS (
        SELECT
            game_id,
            season,
            MAX(period_number) AS max_period
        FROM read_parquet('{pbp_path}')
        WHERE season BETWEEN 2022 AND 2026
        GROUP BY game_id, season
    )

    SELECT
        max_period,
        COUNT(*) AS games
    FROM game_periods
    GROUP BY max_period
    ORDER BY max_period
    """
).df()

print(period_distribution.to_string(index=False))


# --------------------------------------------------
# Sample overtime games
# --------------------------------------------------

print("\nSAMPLE GAMES WITH PERIOD > 4\n")

ot_games = con.execute(
    f"""
    WITH game_periods AS (
        SELECT
            game_id,
            season,
            MAX(period_number) AS max_period
        FROM read_parquet('{pbp_path}')
        WHERE season BETWEEN 2022 AND 2026
        GROUP BY game_id, season
    )

    SELECT *
    FROM game_periods
    WHERE max_period > 4
    ORDER BY max_period DESC, game_id
    LIMIT 20
    """
).df()

print(ot_games.to_string(index=False))

print("\nGAMES.STATUS_PERIOD VS PBP MAX PERIOD\n")

comparison = con.execute(
    f"""
    WITH pbp_periods AS (
        SELECT
            game_id,
            MAX(period_number) AS pbp_max_period
        FROM read_parquet('{pbp_path}')
        WHERE season BETWEEN 2022 AND 2026
        GROUP BY game_id
    ),

    game_status AS (
        SELECT
            game_id,
            season,
            status_period
        FROM read_parquet('{games_path}')
        WHERE season BETWEEN 2022 AND 2026
    )

    SELECT
        g.status_period,
        p.pbp_max_period,
        COUNT(*) AS games
    FROM game_status g
    JOIN pbp_periods p
        ON g.game_id = p.game_id
    GROUP BY
        g.status_period,
        p.pbp_max_period
    ORDER BY
        g.status_period,
        p.pbp_max_period
    """
).df()

print(comparison.to_string(index=False))

con.close()