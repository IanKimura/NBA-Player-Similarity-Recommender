# Historical data snapshot

`nba_2025_clean.csv` is the original local project's cleaned 2024–25 snapshot,
copied without changing its rows. Its source workflow uses Basketball Reference's
2025 per-game, per-possession, and advanced tables. Retrieval date and original
raw HTML were not saved, so exact recreation from the live site is not guaranteed.

The snapshot has 364 unique player rows and 68 columns. The recommender drops
eight rows with incomplete values among its 14 features, leaving 356 profiles.
Team identifiers are absent in this snapshot; any team field displays a dash.

The original pipeline uses a 500 estimated-minutes filter, combining games
played and per-game minutes. Traded-player aggregation may reflect an older
fallback to a stint row rather than an aggregate row when source markers differ.
The CSV is preserved as the basis for the documented examples.

The revised optional pipeline recognizes `TOT` and markers such as `2TM` as
aggregate rows, and avoids multiplying an advanced-table season-minute total
by games played. Those changes do not rewrite the bundled snapshot.

Optional refresh:

```bash
python -m pip install lxml
python src/data_prep.py
```

Refreshing overwrites the snapshot. Live site access policies and table schemas
can change; this network refresh was not exercised during cleanup. Inspect
source tables and row counts before using refreshed data, then regenerate the
figures and example outputs.

Source URLs used by the pipeline:

- https://www.basketball-reference.com/leagues/NBA_2025_per_game.html
- https://www.basketball-reference.com/leagues/NBA_2025_per_poss.html
- https://www.basketball-reference.com/leagues/NBA_2025_advanced.html

Source data remains the property of its respective owners. This repository does
not assign an upstream data license.
