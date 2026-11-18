import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------
# Config
# ----------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "nba_2025_clean.csv"

FEATURES = [
    # Scoring / Shooting
    "PTS_pg", "FG%_pg", "3P%_pg", "FT%_pg",
    # Playmaking / Turnovers
    "AST_pg", "TOV_pg", "USG%_adv",
    # Defense
    "STL_pg", "BLK_pg", "DRB%_adv",
    # Efficiency / Impact
    "TS%_adv", "PER_adv", "WS/48_adv", "BPM_adv",
]

# These will be built at runtime
_df_model = None
_sim_matrix = None


# ----------------------------
# Core functions
# ----------------------------
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the cleaned NBA dataset from CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run src/data_prep.py first to generate nba_2025_clean.csv."
        )
    df = pd.read_csv(path)
    return df


def build_similarity_model(df: pd.DataFrame, features=FEATURES):
    """
    Build scaled feature matrix + cosine similarity.
    Returns:
      df_model: filtered df after dropna
      sim_matrix: cosine similarity matrix (n_players x n_players)
    """
    # Keep only rows with complete feature data
    required = ["Player", *features]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df_model = df.dropna(subset=required).reset_index(drop=True)
    if len(df_model) < 2:
        raise ValueError("At least two complete player profiles are required.")
    if df_model["Player"].duplicated().any():
        raise ValueError("Expected one row per player; resolve duplicate players first.")
    if not np.isfinite(df_model[features].to_numpy(dtype=float)).all():
        raise ValueError("Model features must be finite numeric values.")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[features])

    sim_matrix = cosine_similarity(X_scaled)
    return df_model, sim_matrix


def initialize():
    """Build the global model objects (df_model and sim_matrix)."""
    global _df_model, _sim_matrix
    df = load_data()
    _df_model, _sim_matrix = build_similarity_model(df)


def get_player_names():
    """Return only players eligible for the fitted model."""
    if _df_model is None:
        initialize()
    return sorted(_df_model["Player"].tolist())


def _player_index(name):
    if _df_model is None:
        initialize()
    matches = _df_model.index[_df_model["Player"] == name]
    if len(matches) == 0:
        raise ValueError(f"{name} not found in the eligible player dataset.")
    return int(matches[0])


def recommend(player_name: str, top_n: int = 5) -> pd.DataFrame:
    """
    Return the top-N most similar players to player_name.
    """
    global _df_model, _sim_matrix
    if _df_model is None or _sim_matrix is None:
        initialize()
    if isinstance(top_n, bool) or not isinstance(top_n, int) or top_n < 1:
        raise ValueError("top_n must be a positive integer.")

    if player_name not in _df_model["Player"].values:
        raise ValueError(f"{player_name} not found in dataset.")

    idx = _df_model.index[_df_model["Player"] == player_name][0]
    sims = list(enumerate(_sim_matrix[idx]))
    sims = sorted(sims, key=lambda x: x[1], reverse=True)

    out = []
    for j, score in sims:
        if j == idx:
            continue
        row = _df_model.iloc[j]
        out.append(
            {
                "Player": row["Player"],
                "Team": row.get("Tm", "—"),
                "Pos": row.get("Pos", "—"),
                "Similarity": round(float(score), 3),
            }
        )
        if len(out) >= top_n:
            break

    return pd.DataFrame(out)

def get_player_row(player_name: str) -> pd.Series:
    global _df_model
    if _df_model is None:
        initialize()
    if player_name not in _df_model["Player"].values:
        raise ValueError(f"{player_name} not found in dataset.")
    return _df_model[_df_model["Player"] == player_name].iloc[0]


def explain_similarity(player1: str, player2: str, top_k: int = 6) -> pd.DataFrame:
    """
    Explain similarity using scaled-feature closeness and cosine contributions.
    Returns the top features where players are closest (in scaled space),
    along with each feature's contribution to the cosine similarity.
    """
    global _df_model
    if _df_model is None:
        initialize()

    # Work on the same modeling df used for similarity
    df_model = _df_model.copy()

    # Fit scaler on df_model features to match model space
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[FEATURES])
    X_scaled = pd.DataFrame(X_scaled, columns=FEATURES)

    # Locate indices in df_model
    idx1 = _player_index(player1)
    idx2 = _player_index(player2)

    v1 = X_scaled.iloc[idx1]
    v2 = X_scaled.iloc[idx2]

    # Difference in scaled space (smaller = more similar)
    abs_diff = (v1 - v2).abs()

    # Normalized feature contributions sum to the full cosine similarity.
    denominator = np.linalg.norm(v1) * np.linalg.norm(v2)
    contribution = v1 * v2 / denominator if denominator else v1 * 0.0

    out = pd.DataFrame({
        "Feature": FEATURES,
        "Player1 (scaled)": v1.values,
        "Player2 (scaled)": v2.values,
        "Abs Diff (scaled)": abs_diff.values,
        "Cosine Contribution": contribution.values,
    })

    # Pick top-k "closest" features, but keep contribution visible too
    out = out.sort_values("Abs Diff (scaled)", ascending=True).head(top_k).reset_index(drop=True)

    # Make it prettier: round numbers
    for c in ["Player1 (scaled)", "Player2 (scaled)", "Abs Diff (scaled)", "Cosine Contribution"]:
        out[c] = out[c].astype(float).round(3)

    return out

def radar_data(player1: str, player2: str) -> pd.DataFrame:
    """
    Returns a 0–1 normalized table for FEATURES for two players,
    based on min/max across the modeling dataframe.
    """
    global _df_model
    if _df_model is None:
        initialize()

    df_model = _df_model.copy()
    stats = df_model.set_index("Player")[FEATURES]

    p1 = stats.loc[player1]
    p2 = stats.loc[player2]

    mins = stats.min()
    maxs = stats.max()
    denom = (maxs - mins).replace(0, 1)  # avoid divide-by-zero

    p1_scaled = (p1 - mins) / denom
    p2_scaled = (p2 - mins) / denom

    radar_df = pd.DataFrame({
        "Feature": FEATURES,
        player1: p1_scaled.values,
        player2: p2_scaled.values,
    })

    return radar_df

# ----------------------------
# Quick test (optional)
# ----------------------------
if __name__ == "__main__":
    initialize()
    print(recommend("Jayson Tatum", top_n=5))
