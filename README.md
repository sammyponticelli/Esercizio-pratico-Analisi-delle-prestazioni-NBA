# NBA Impact Analysis

Analysis of how much NBA players contribute to their team's performance, through a synthetic indicator called the **Impact Score**.

The Impact Score is computed with a predefined formula in which every individual statistic carries a specific weight. The analysis produces **two versions** of the indicator, computed in parallel and compared against each other:

- **`impact_score_game`** — average impact *per game* (measures the overall volume of production);
- **`impact_score_40`** — impact normalised *per 40 minutes* of play (measures efficiency per unit of time).

The full write-up of the findings, with all the charts and their reading, is in **[REPORT.md](REPORT.md)**. This file documents the data, the method and the code.

---

## Dataset

`nba_players_25_26_regular_season_wide_data.csv` — individual statistics for the **2025-26 NBA Regular Season** (582 players, 28 variables).

Main variables used in the analysis:

| Variable | Description |
|---|---|
| `player_name` | Player name |
| `age_completed_years` | Age (completed years) |
| `team` | Team |
| `minutes_played` | Minutes played (season totals) |
| `one_point_made`, `two_point_made`, `three_point_made` | Made shots by type |
| `offensive_rebounds`, `defensive_rebounds` | Offensive and defensive rebounds |
| `assists`, `steals`, `blocks`, `turnovers` | Assists, steals, blocks, turnovers |
| `wins`, `losses` | Wins and losses (used to derive games played) |
| `position` | Position (G / F / C and combinations) — not part of the formula, but the grouping variable of phase 8 |

Variables present in the dataset but **not** used in the analysis:

| Variable | Description |
|---|---|
| `height_m`, `weight_kg` | Height and weight |
| `experience` | Years of NBA experience |
| `country` | Nationality |
| `personal_fouls` | Personal fouls |
| `one_point_attempted`, `two_point_attempted`, `three_point_attempted` | Attempted shots by type (from which shooting percentages could be derived) |

The data is seasonal (totals): per-game averages are derived during the analysis.

---

## The Impact Score formula

The statistics are expressed as **per-game averages**. Both versions of the indicator are derived from that base.

**Impact Score per game:**

```
impact_score_game = PTS + 1.2 · REB + 1.5 · AST + 2 · STL + 2 · BLK − TOV
```

**Impact Score normalised per 40 minutes:**

```
impact_score_40 = (PTS + 1.2 · REB + 1.5 · AST + 2 · STL + 2 · BLK − TOV) / MIN · 40
```

where:

- `PTS = one_point_made + 2 · two_point_made + 3 · three_point_made`
- `REB = offensive_rebounds + defensive_rebounds`
- `games_played = wins + losses`
- `MIN` = average minutes per game

The weights reward the plays with the highest added value (assists, steals, blocks) and penalise turnovers.

The two versions answer different questions: `impact_score_game` measures **how much a player produces overall**, and is therefore tied to the minutes the coach gives them; `impact_score_40` makes players with very different playing times comparable, measuring impact **per unit of time**. Comparing the two tells apart the players who produce a lot because they play a lot from those who are efficient regardless of time on court.

### Games played filter

Since normalising by minutes tends to reward players with very little playing time (very small samples), the analysis only considers players who have played at least **1/3 of the games of the most used player** in the dataset. This is a *relative* threshold: it works on a season still in progress, without having to fix a predefined number of games.

---

## Structure of the analysis

### 1. Dataset exploration
Analysis of the structure of the dataset, identification of the available variables, analysis of the data types, check for missing values and duplicates.

### 2. Data cleaning and preparation
Handling of missing values, removal of any duplicates, conversion of the variables into the appropriate formats and preparation of the data the analysis needs.

Choices made:
- missing values in `wins` / `losses` treated as 0 games played;
- players with 0 games played excluded from the averages (`NaN` instead of a division by zero);
- hybrid position labels collapsed onto the primary position (`G-F` → `G`, `F-G` and `F-C` → `F`, `C-F` → `C`), so that every table downstream works on three groups instead of seven.

### 3. Impact Score computation
Application of the predefined formula, accounting for the different weights assigned to the player statistics. The games played filter is applied before the computation. The result is stored in the two new variables `impact_score_game` and `impact_score_40`.

### 4. Top 10 analysis
Players are sorted by Impact Score and the 10 with the highest score are singled out. For the Top 10 the **average Impact Score** and the **average age** are computed. The analysis runs separately on the two versions of the indicator, producing two distinct rankings.

### 5. Analysis by age band
Players are split into the **19–22**, **23–26**, **27–30**, **31–34** and **35+** bands. For each band: number of players, average Impact Score, maximum Impact Score. Here too the table is built for both versions of the indicator.

### 6. Search for significant correlations
Analysis of the relationship between **minutes played** and each of the two versions of the Impact Score: Pearson correlation coefficient, scatter plot and linear regression line drawn on top of the chart.

The phase is completed by a **cluster analysis** (K-Means, 3 clusters, on standardised minutes played and Impact Score) that identifies groups of players with similar profiles of usage and impact. The two cluster analyses are produced in parallel as well, one per version of the indicator.

The comparison between the two correlations is itself a result of the analysis:

| Relationship | Pearson |
|---|---|
| `minutes_played` ↔ `impact_score_game` | **0.76** |
| `minutes_played` ↔ `impact_score_40` | **0.39** |

The strong correlation on the per-game score confirms that overall production depends largely on playing time; normalising per 40 minutes removes most of it, while leaving a residual positive correlation — a sign that coaches do tend to give more minutes to the more efficient players.

### 7. Player comparison
The Top 10 players are compared on the main individual statistics (`PTS`, `REB`, `AST`, `STL`, `BLK`, `TOV`, `MIN` per-game averages), with one comparison table per version of the indicator and two **bar charts** of the respective Top 10.

Tables and charts are built on the dataset **filtered** in phase 3, so the rankings match those of phase 4. The two tables are independent of each other: each works on its own copy of the filtered dataset.

### 8. Impact Score by position
Average Impact Score grouped by position, computed on both versions of the indicator, with a **grouped bar chart** comparing the two averages position by position.

Hybrid labels are collapsed onto the primary position (`G-F` → `G`, `F-G` and `F-C` → `F`, `C-F` → `C`). The dataset spreads players over seven labels, three of which hold fewer than 25 of the 419 eligible players — too few for a stable average, and `F-G` held just 9. The three resulting groups hold 204 guards, 155 forwards and 60 centres.

Results:

| Position | Players | Impact Score per game | Impact Score per 40 minutes |
|---|---|---|---|
| `G` | 204 | 19.88 | 33.84 |
| `F` | 155 | 19.67 | 35.09 |
| `C` | 60 | **22.81** | **40.78** |

Centres lead on both versions. Their margin over the guards widens once playing time is normalised, from about 15% to about 21%, while the margin over the forwards stays around 16%. This follows from the formula, where rebounds are weighted 1.2 and blocks 2 — the two categories where centres accumulate most. Guards and forwards are almost tied per game (19.88 against 19.67) but swap order once normalised (33.84 against 35.09), because guards average about one minute more per game.

### 9. Conclusions
The results of the previous phases come together in a **summary table** that puts the two versions of the indicator side by side, one question of the analysis per row:

| | per game | per 40 minutes |
|---|---|---|
| Highest impact player | Nikola Jokić (59.93) | Nikola Jokić (68.81) |
| Top 10 average Impact Score | 48.67 | 59.07 |
| Top 10 average age | 27.5 | 27.7 |
| Age band with the highest impact | 35+ (26.03) | 35+ (39.09) |
| Correlation with minutes played | 0.76 | 0.39 |
| Position with the highest impact | C (22.81) | C (40.78) |

What comes out of it:

- **Jokić is first in both rankings.** This is the most solid result of the analysis: he stays ahead even once playing time is taken out of the picture, so his edge does not depend on how long he is on the court.
- **The two Top 10 averages are not comparable with each other.** 48.67 and 59.07 live on different scales: nobody averages 40 minutes, so the normalisation rescales every score upwards. Each number has to be read inside its own column.
- **The average age of the best players is the same in both versions**, just above 27: the performance peak does not move depending on how impact is measured.
- **The 35+ band has the highest average in both versions, but this is a selection effect.** It is 20 players out of 419: at that age only those who are still very strong stay on the court, while the younger bands also contain every bench player.
- **The correlation with minutes drops from 0.76 to 0.39.** Per-game production is largely explained by the minutes granted; normalising removes most of that, and what remains suggests coaches do give more room to the more efficient players.
- **Centres have the highest impact on both versions, and normalising widens their lead.** Guards and forwards are separated by 0.21 per game and change order once normalised, so the only stable positional result is the advantage of the interior — which comes straight from the weights the formula puts on rebounds and blocks.

---

## Progress

| Section | Status |
|---|---|
| 1. Dataset exploration | ✅ implemented |
| 2. Data cleaning and preparation | ✅ implemented |
| 3. Impact Score computation | ✅ implemented — both versions (per game and per 40 minutes) |
| 4. Top 10 analysis | ✅ implemented — on both versions |
| 5. Analysis by age band | ✅ implemented — on both versions |
| 6. Search for significant correlations | ✅ implemented — minutes/impact correlation, scatter with regression and cluster analysis, on both versions |
| 7. Player comparison | ✅ implemented — comparison tables and Top 10 bar charts, on both versions |
| 8. Impact Score by position | ✅ implemented — averages by position and bar chart comparing the two versions |
| 9. Conclusions | ✅ implemented — summary table with the two versions side by side |

---

## Project structure

```
nba_analysis_exercise/
├── nba_analysis.py                                   # analysis script
├── nba_players_25_26_regular_season_wide_data.csv    # dataset
├── charts/                                           # the seven figures, saved as PNG
├── REPORT.md                                         # write-up of the findings
├── .gitignore
└── README.md
```

### Main functions (`nba_analysis.py`)

| Function | Description |
|---|---|
| `explore_dataset(raw_data)` | Initial exploration: `head`, data types |
| `build_season_totals(season_stats)` | View of the season totals with `games_played`, `PTS`, `REB` |
| `calculate_per_game_averages(season_stats)` | Per-game averages of every statistic, and the collapse of the hybrid position labels |
| `filter_by_games_played(per_game_stats)` | Keeps the players with at least 1/3 of the games of the most used one |
| `calculate_impact_score_40(qualified_players)` | Formula normalised per 40 minutes (`impact_score_40`), sorted descending |
| `calculate_impact_score_game(qualified_players)` | Formula on the per-game averages (`impact_score_game`), sorted descending |
| `calculate_top10_average_score_40` / `..._game` | Average Impact Score of the Top 10, for each version |
| `calculate_top10_average_age_40` / `..._game` | Average age of the Top 10, for each version |
| `build_age_group_table_40` / `..._game` | Summary table by age band (number of players, average, maximum) |
| `calculate_minutes_correlation_40` / `..._game` | Pearson correlation coefficient between minutes played and Impact Score |
| `collect_correlations(ranking_game, ranking_40)` | Collects the two correlations into a dictionary |
| `plot_minutes_vs_score_40` / `..._game` | Scatter plot minutes/Impact Score with the linear regression line |
| `plot_cluster_analysis_40` / `..._game` | K-Means cluster analysis (3 clusters) on standardised minutes and Impact Score |
| `build_top10_comparison_game` / `..._40` | Comparison table of the Top 10 with the per-game averages |
| `plot_top10_bar_chart_40` / `..._game` | Bar chart of the Top 10 for each version of the indicator |
| `calculate_score_by_position_game` / `..._40` | Average Impact Score by position, sorted descending |
| `plot_position_comparison(scores_game, scores_40)` | Grouped bar chart of the two averages by position, ordered `G`, `F`, `C` |
| `build_conclusions_table(...)` | Final summary table: the six answers of the analysis, per game and per 40 minutes |

Naming convention: functions start with a verb (`calculate_`, `build_`, `plot_`, `filter_`, `explore_`), variables are nouns. Functions that exist in two versions carry the `_game` or `_40` suffix. The DataFrames that flow through the analysis are named `season_stats` (season totals) → `per_game_stats` (per-game averages) → `qualified_players` (after the filter) → `ranking_game` / `ranking_40` (with the Impact Score computed and sorted).

### Implementation notes

Recurring choices in the code, collected here so the comments in the file can stay minimal.

**Defensive copies.** Every analysis function opens with a `.copy()` of the DataFrame it receives and works on the copy: the caller's DataFrame keeps its original columns, so the functions can be called in any order without depending on one another.

**Divisions by zero.** Averages are never computed on a null denominator. Before dividing, the denominator goes through `.where(column > 0)`, which turns zeros into `NaN`: a player with 0 games (or 0 minutes) leaves the analysis as missing data instead of producing an `inf`.

**Missing values in the charts.** `np.polyfit` returns `NaN` coefficients if even a single row is incomplete, and `KMeans` does not accept `NaN` at all: both functions therefore `dropna` on the two columns they use before computing.

**Regression line.** The line is drawn on `np.sort(x.unique())` rather than on the original `x`: without sorting, `plot` retraces the line back and forth following the order of the rows.

**Separate figures.** Every chart function opens its own `plt.figure()` before drawing, otherwise the charts would end up stacked on the same axes.

**Standardisation before K-Means.** Minutes and Impact Score live on different scales: without `StandardScaler` the euclidean distance would be dominated by the minutes. The number of clusters (3) is the one with the best silhouette score on this dataset, and `random_state=42` makes the clusters identical on every run.

**`minutes_played` hidden but present.** The column stays in the DataFrames because correlations, scatter plots and cluster analysis are built on it; it is dropped only at `print` time, to keep the console tables light.

---

## Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- scikit-learn (`StandardScaler`, `KMeans`)

---

## How to run the analysis

```bash
pip install pandas numpy matplotlib scikit-learn
python nba_analysis.py
```

The script has to be run from the project folder, where the CSV file is.

Running it prints the summary tables to the console and opens **seven Matplotlib windows**:

| # | Chart |
|---|---|
| 1 | Scatter plot minutes / `impact_score_40` with the regression line |
| 2 | Scatter plot minutes / `impact_score_game` with the regression line |
| 3 | Cluster analysis on minutes and `impact_score_40` |
| 4 | Cluster analysis on minutes and `impact_score_game` |
| 5 | Bar chart of the Top 10 by `impact_score_40` |
| 6 | Bar chart of the Top 10 by `impact_score_game` |
| 7 | Bar chart comparing the average Impact Score by position |

The main program is split in two blocks: first every table printed to the console, in the order of phases 1 to 9, then every chart grouped by type (the two scatters, the two clusters, the two Top 10, the comparison by position). The windows all open together on `plt.show()`, so keeping them grouped makes the order in which they appear predictable.

---

## Note

The analysis is exploratory: the Impact Score is an indicator built on the formula and the weights defined in this project and **is not necessarily an official measure of impact used by the NBA**.
