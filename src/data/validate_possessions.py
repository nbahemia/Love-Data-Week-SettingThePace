from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "team_possessions.parquet"

path = DATA.as_posix().replace("'", "''")

con = duckdb.connect()

print("\nPOSSESSION DISTRIBUTION\n")

print(
    con.execute(
        f"""
        SELECT
            COUNT(*) AS observations,
            ROUND(AVG(estimated_team_possessions), 2) AS mean,
            ROUND(MEDIAN(estimated_team_possessions), 2) AS median,
            ROUND(STDDEV(estimated_team_possessions), 2) AS std_dev,
            ROUND(MIN(estimated_team_possessions), 2) AS minimum,
            ROUND(QUANTILE_CONT(estimated_team_possessions, 0.01), 2) AS p01,
            ROUND(QUANTILE_CONT(estimated_team_possessions, 0.05), 2) AS p05,
            ROUND(QUANTILE_CONT(estimated_team_possessions, 0.95), 2) AS p95,
            ROUND(QUANTILE_CONT(estimated_team_possessions, 0.99), 2) AS p99,
            ROUND(MAX(estimated_team_possessions), 2) AS maximum
        FROM read_parquet('{path}')
        """
    ).df().to_string(index=False)
)

print("\nBY SEASON\n")

print(
    con.execute(
        f"""
        SELECT
            season,
            COUNT(*) / 2 AS games,
            ROUND(AVG(estimated_team_possessions), 2) AS avg_possessions,
            ROUND(MEDIAN(estimated_team_possessions), 2) AS median_possessions
        FROM read_parquet('{path}')
        GROUP BY season
        ORDER BY season
        """
    ).df().to_string(index=False)
)

print("\nEXTREME LOW VALUES\n")

print(
    con.execute(
        f"""
        SELECT
            game_date,
            team_location,
            opponent_team_location,
            team_score,
            opponent_team_score,
            ROUND(estimated_team_possessions, 2) AS possessions
        FROM read_parquet('{path}')
        ORDER BY estimated_team_possessions
        LIMIT 10
        """
    ).df().to_string(index=False)
)

print("\nEXTREME HIGH VALUES\n")

print(
    con.execute(
        f"""
        SELECT
            game_date,
            team_location,
            opponent_team_location,
            team_score,
            opponent_team_score,
            ROUND(estimated_team_possessions, 2) AS possessions
        FROM read_parquet('{path}')
        ORDER BY estimated_team_possessions DESC
        LIMIT 10
        """
    ).df().to_string(index=False)
)

print("\nWITHIN-GAME POSSESSION DIFFERENCE\n")

print(
    con.execute(
        f"""
        WITH game_differences AS (
            SELECT
                game_id,
                season,
                MAX(estimated_team_possessions)
                    - MIN(estimated_team_possessions)
                    AS possession_difference
            FROM read_parquet('{path}')
            GROUP BY game_id, season
            HAVING COUNT(*) = 2
        )

        SELECT
            COUNT(*) AS games,
            ROUND(AVG(possession_difference), 2) AS mean_difference,
            ROUND(MEDIAN(possession_difference), 2) AS median_difference,
            ROUND(QUANTILE_CONT(possession_difference, 0.90), 2) AS p90,
            ROUND(QUANTILE_CONT(possession_difference, 0.95), 2) AS p95,
            ROUND(QUANTILE_CONT(possession_difference, 0.99), 2) AS p99,
            ROUND(MAX(possession_difference), 2) AS maximum
        FROM game_differences
        """
    ).df().to_string(index=False)
)

print("\nLARGEST WITHIN-GAME DIFFERENCES\n")

print(
    con.execute(
        f"""
        WITH ranked_games AS (
            SELECT
                game_id,
                game_date,
                MAX(team_location) AS team_1,
                MIN(team_location) AS team_2,
                MIN(estimated_team_possessions) AS low_estimate,
                MAX(estimated_team_possessions) AS high_estimate,
                MAX(estimated_team_possessions)
                    - MIN(estimated_team_possessions)
                    AS possession_difference
            FROM read_parquet('{path}')
            GROUP BY game_id, game_date
            HAVING COUNT(*) = 2
        )

        SELECT
            game_id,
            game_date,
            team_1,
            team_2,
            ROUND(low_estimate, 2) AS low_estimate,
            ROUND(high_estimate, 2) AS high_estimate,
            ROUND(possession_difference, 2) AS difference
        FROM ranked_games
        ORDER BY possession_difference DESC
        LIMIT 15
        """
    ).df().to_string(index=False)
)

con.close()