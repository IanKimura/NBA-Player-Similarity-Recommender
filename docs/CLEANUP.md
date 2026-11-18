# Cleanup and verification

The public repository contained a README and placeholder directory files.
The working app, notebook, source modules and CSV were located in the local
`Personal_Projects/nba-player-similarity` project.

## Changes in this package

- Added a working source/data package, dependency list, visual README, example
  outputs and a snapshot-based notebook.
- Replaced the notebook workflow that shadowed scikit-learn's pairwise cosine
  function with a two-vector function, producing an argument error.
- Exclude the selected player by row index, rather than assuming it is always
  first in the similarity sort. This handles tied and zero-vector profiles.
- Validate required columns, unique player names, finite values and positive
  recommendation counts.
- Normalize feature-wise cosine contributions by both vector norms. Before
  rounding, their sum now matches the cosine similarity. The table still orders
  by smallest absolute standardized difference, not by largest contribution.
- Limit the app selector to complete eligible profiles, cache initialization,
  and explain the score and visualization scales.
- Recognize aggregate traded-player rows in the optional data pipeline and fix
  the fallback season-minute calculation. The bundled CSV remains unchanged.
- Replaced placeholder clone/setup instructions with actual runnable commands.

The original local project outside this prepared folder was not modified.
No live data refresh or new model features are required for the examples.

## Checks

- Rankings for all 356 eligible players are sorted and exclude the query player.
- A tied constant-profile example does not return the query itself.
- Summed rounded explanation contributions approximate the cosine score within
  the expected rounding tolerance.
- Invalid requests and missing feature columns produce useful errors.
- Synthetic `2TM` rows are preferred over individual stints.
- Streamlit AppTest exercises the initial render and a player-selection change.
- All notebook code cells execute against the bundled data.
- README image paths and local links are checked; all PNGs decode successfully.

Application checks use Streamlit's test interface, not a browser screenshot.
The optional network refresh is unverified against the live source site.
