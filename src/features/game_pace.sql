WITH possession_summary AS (
    SELECT
        game_id,
        season,
        game_date,

        AVG(estimated_team_possessions) AS raw_game_possessions,

        MAX(estimated_team_possessions)
            - MIN(estimated_team_possessions)
            AS possession_estimate_difference,

        COUNT(*) AS team_count

    FROM team_possessions

    GROUP BY
        game_id,
        season,
        game_date
),

game_length AS (
    SELECT
        game_id,
        status_period,

        CASE
            WHEN status_period = 4 THEN 40
            WHEN status_period > 4 THEN 40 + ((status_period - 4) * 5)
            ELSE NULL
        END AS game_minutes

    FROM games

    WHERE season BETWEEN 2022 AND 2026
      AND status_type_completed = TRUE
)

SELECT
    p.game_id,
    p.season,
    p.game_date,

    g.status_period,
    g.game_minutes,

    p.raw_game_possessions,

    p.raw_game_possessions
        * (40.0 / g.game_minutes)
        AS game_pace,

    p.possession_estimate_difference

FROM possession_summary p

INNER JOIN game_length g
    ON p.game_id = g.game_id

WHERE p.team_count = 2
  AND g.game_minutes IS NOT NULL;