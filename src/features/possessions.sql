SELECT
    game_id,
    season,
    game_date,
    game_date_time,

    team_id,
    team_location,
    team_name,
    team_abbreviation,
    team_home_away,

    opponent_team_id,
    opponent_team_location,
    opponent_team_name,
    opponent_team_abbreviation,

    team_score,
    opponent_team_score,
    team_winner,

    field_goals_attempted,
    offensive_rebounds,
    turnovers,
    free_throws_attempted,

    field_goals_attempted
        - offensive_rebounds
        + turnovers
        + (0.44 * free_throws_attempted)
        AS estimated_team_possessions

FROM team_box

WHERE season BETWEEN 2022 AND 2026;