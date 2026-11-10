from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[2]
PACE_PATH = ROOT / "data" / "processed" / "game_pace.parquet"


def sql_path(path: Path) -> str:
    return path.as_posix().replace("'", "''")


path = sql_path(PACE_PATH)

con = duckdb.connect()


print("\nGAME PACE DISTRIBUTION\n")

print(
    con.execute(
        f"""
        SELECT
            COUNT(*) AS games,
            ROUND(AVG(game_pace), 2) AS mean,
            ROUND(MEDIAN(game_pace), 2) AS median,
            ROUND(STDDEV(game_pace), 2) AS std_dev,
            ROUND(MIN(game_pace), 2) AS minimum,
            ROUND(QUANTILE_CONT(game_pace, 0.01), 2) AS p01,
            ROUND(QUANTILE_CONT(game_pace, 0.05), 2) AS p05,
            ROUND(QUANTILE_CONT(game_pace, 0.95), 2) AS p95,
            ROUND(QUANTILE_CONT(game_pace, 0.99), 2) AS p99,
            ROUND(MAX(game_pace), 2) AS maximum
        FROM read_parquet('{path}')
        """
    ).df().to_string(index=False)
)


print("\nOVERTIME EFFECT\n")

print(
    con.execute(
        f"""
        SELECT
            CASE
                WHEN status_period = 4 THEN 'Regulation'
                ELSE 'Overtime'
            END AS game_type,

            COUNT(*) AS games,

            ROUND(AVG(raw_game_possessions), 2)
                AS avg_raw_possessions,

            ROUND(AVG(game_pace), 2)
                AS avg_pace_40

        FROM read_parquet('{path}')

        GROUP BY game_type
        ORDER BY game_type
        """
    ).df().to_string(index=False)
)


print("\nFASTEST GAMES AFTER OT ADJUSTMENT\n")

print(
    con.execute(
        f"""
        SELECT
            game_id,
            game_date,
            status_period,
            game_minutes,

            ROUND(raw_game_possessions, 2)
                AS raw_possessions,

            ROUND(game_pace, 2)
                AS pace_40

        FROM read_parquet('{path}')

        ORDER BY game_pace DESC
        LIMIT 15
        """
    ).df().to_string(index=False)
)


print("\nSLOWEST GAMES AFTER OT ADJUSTMENT\n")

print(
    con.execute(
        f"""
        SELECT
            game_id,
            game_date,
            status_period,
            game_minutes,

            ROUND(raw_game_possessions, 2)
                AS raw_possessions,

            ROUND(game_pace, 2)
                AS pace_40

        FROM read_parquet('{path}')

        ORDER BY game_pace
        LIMIT 15
        """
    ).df().to_string(index=False)
)


con.close()