# Setting the Pace
## Should You Play Your Game — or Theirs?

### Project Goal

This project investigates how game pace affects performance in NCAA women's basketball and whether teams should always attempt to impose their preferred tempo or adjust their style based on the opponent.

Rather than treating pace only as a descriptive statistic, the project aims to develop a matchup-specific framework for understanding when playing faster or slower benefits a team.

### Project Development AI Disclaimer

AI has helped contribute to this project by producing code files, documentation, and aiding my lines of reasoning. My workflow with AI is centered around feeding it information, my jumbled blurbs of ideas and reasoning, as well as assisting in coding and debugging. 
---

# Research Questions

## Question 1 — Is There an Optimal Pace?

**Core question:** How is pace associated with team performance?

Questions to investigate:

- Are stronger teams generally playing faster or slower than their opponents?
- Is there a relationship between game pace and point differential?
- Is that relationship linear?
- Is there a pace range associated with the strongest performance?
- Do diminishing returns appear when teams play too quickly?
- Does the relationship remain after accounting for team and opponent quality?

This section establishes the baseline relationship between pace and performance. It should not be interpreted as proof that pace causes winning.

### Potential Outcomes

The analysis may show that:

- faster basketball is associated with stronger performance;
- slower basketball is associated with stronger performance;
- pace has little independent relationship with performance;
- an intermediate pace produces the strongest outcomes; or
- optimal pace depends heavily on team style and opponent.

---

## Question 2 — Does Faster Basketball Create Sloppier Basketball?

**Core question:** How does game pace affect execution?

Potential metrics include:

- turnover rate;
- effective field-goal percentage;
- offensive rebound rate;
- free-throw rate;
- assists;
- fast-break scoring;
- points per possession.

Rate statistics should generally be preferred over raw totals because faster games naturally contain more possessions and therefore more opportunities for events such as turnovers and rebounds.

This section is intended to identify potential mechanisms behind any relationship discovered between pace and performance.

For example, if performance initially improves as pace increases but declines at extremely high tempos, execution metrics may help determine whether the decline corresponds with increased turnover rate, poorer shooting efficiency, reduced offensive rebounding, or another factor.

---

## Question 3 — Should You Play Your Game or Theirs?

**Primary research question:** Given two teams with established playing styles, when should a team impose its preferred pace and when should it adjust its tempo to the opponent?

Each team's preferred or expected pace will be estimated using only information available before the matchup.

Potential concepts include:

**Pregame Team Pace**

An estimate of the tempo at which a team typically plays entering a game.

**Pace Mismatch**

The difference between the preferred paces of the two teams entering a matchup.

**Pace Deviation**

The difference between the actual game's pace and a team's expected/preferred pace.

**Tempo Control**

A measure of which team's established pace the actual game more closely resembled.

The ultimate objective is to estimate how expected performance changes across possible game paces for a particular matchup.

Rather than producing one universal optimal pace, the model could produce a matchup-specific recommendation.

Example:

- Team A preferred pace: 74
- Team B preferred pace: 67
- Estimated optimal matchup pace for Team A: 70

Such a result would suggest that Team A may benefit from adjusting away from its normal style rather than simply maximizing its ability to impose its usual pace.

---

# Data

Primary dataset: NCAA women's basketball.

Primary analysis window:

- 2021–22 through 2025–26 seasons
- Dataset season values: 2022–2026

The window was selected after evaluating team-level box-score coverage.

Team-box coverage was approximately 99.6%–100% throughout this period, producing:

- 28,880 complete games
- 57,760 team-game observations

Earlier seasons contained substantially more missing team-level box-score data and several obvious data-quality issues.

---

# Pace Construction

Initial team possessions are estimated from box-score statistics using field-goal attempts, offensive rebounds, turnovers, and free-throw attempts.

Each game produces two independent possession estimates, one for each team.

Validation across the primary sample showed:

- Mean within-game difference: 1.54 possessions
- Median difference: 1.28
- 90th percentile: 3.16
- 95th percentile: 3.84
- 99th percentile: 5.32

The two team estimates are averaged to create a game-level possession estimate.

---

# Overtime Adjustment

An early question during development was whether overtime games were artificially being classified as high-paced games.

They were.

Raw possession totals naturally increase when games contain additional five-minute overtime periods.

Game pace is therefore normalized to a 40-minute regulation game.

Overtime identification was validated by comparing the final game status period against the maximum period contained in play-by-play data.

Among games represented in both sources, the two measures agreed in all but four cases.

The game-level status period was selected because it provided more complete coverage.

The final primary sample contains:

- 28,880 games
- 1,209 overtime games

After normalization:

- Overall mean pace: 70.16 possessions per 40 minutes
- Median pace: 69.78
- 5th percentile: 61.28
- 95th percentile: 80.54

Overtime games averaged 78.78 raw possessions but only 68.70 possessions when normalized to 40 minutes, demonstrating why the adjustment was necessary.

---

# Modeling Principles

## Prevent Future Leakage

Any estimate of a team's style entering a game must use only games played before that matchup.

Future games cannot contribute to a historical team's pregame pace estimate.

## Preferred Pace Is Not Yet Defined

Potential estimators include:

- season-to-date pace;
- recent rolling pace;
- weighted combinations of long-term and recent pace.

Rather than selecting one arbitrarily, historical data may be used to determine which estimator best predicts future or rest-of-season team tempo.

## Separate Prediction From Explanation

Predictive models may help estimate matchup outcomes and optimal pace, but feature importance alone should not be interpreted as causal evidence.

The project should distinguish between:

- descriptive relationships;
- predictive relationships;
- actionable basketball interpretations.

---

# Development Questions Raised

1. Should possession counts come from box scores or play-by-play?

   Initial decision: use box-score estimates for broad coverage and potentially use play-by-play as an independent validation source.

2. Should the project use a SQL database?

   Decision: use DuckDB over Parquet files, allowing SQL transformations without duplicating the large raw datasets.

3. Which seasons have sufficient data quality?

   Decision: use 2022–2026 dataset seasons as the primary sample after inspecting coverage and box-score quality.

4. Which turnover field should be used?

   Validation showed that `turnovers` and `total_turnovers` were fully populated in the primary period, while `team_turnovers` represented a narrower statistic. `turnovers` was selected for the possession estimate.

5. Do overtime games distort pace?

   Yes. Game pace is now normalized to possessions per 40 minutes.

6. Should preferred pace be season-to-date or recent form?

   Not yet decided. Both should initially be calculated and evaluated without future leakage.

7. Could preferred pace estimation itself become a machine-learning problem?

   Potentially. Historical information available at a given point in the season could be used to estimate future/rest-of-season pace, allowing the weighting of recent and longer-term pace to be determined empirically.

---

# Current Status

Completed:

- Repository structure
- Python environment
- Raw-data inspection
- Team-box coverage analysis
- Primary season selection
- DuckDB transformation pipeline
- Team possession estimation
- Within-game possession validation
- Overtime identification
- 40-minute pace normalization
- Initial research-question framework

Next:

Define and validate each team's pregame preferred pace before beginning the matchup optimization analysis.