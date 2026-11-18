import streamlit as st
from pathlib import Path
import sys
import plotly.graph_objects as go

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import your recommender
from src.recommender import recommend, initialize, explain_similarity, radar_data, get_player_names


# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(
    page_title="NBA Player Similarity Recommender",
    layout="centered"
)

st.title("🏀 NBA Player Similarity Recommender")
st.write(
    "Select an NBA player from the 2024–25 season and discover statistically similar players "
    "based on scoring, efficiency, playmaking, defense, and impact metrics."
)

# ----------------------------
# Load data + model
# ----------------------------
@st.cache_resource
def load_players():
    initialize()
    return get_player_names()

players = load_players()

# ----------------------------
# Sidebar controls
# ----------------------------
st.sidebar.header("Controls")
st.sidebar.caption("2024–25 snapshot · similarity is not a probability or player ranking")

selected_player = st.sidebar.selectbox(
    "Choose a player",
    players,
    index=players.index("Jayson Tatum") if "Jayson Tatum" in players else 0
)

top_n = st.sidebar.slider(
    "Number of similar players",
    min_value=3,
    max_value=10,
    value=5
)

# ----------------------------
# Show recommendations
# ----------------------------
if selected_player:
    st.subheader(f"Players similar to {selected_player}")
    recs = recommend(selected_player, top_n=top_n)
    st.dataframe(recs, width="stretch")

st.divider()

# ----------------------------
# Explanation FIRST
# ----------------------------
st.subheader("🧠 Why are they similar?")

# Default to first recommendation so explanation always shows

compare_player = st.selectbox(
    "Choose a player to explain similarity",
    recs["Player"].tolist(),
    index=0
)

explain = explain_similarity(selected_player, compare_player, top_k=6)
st.dataframe(explain, width="stretch")
st.caption("Closest features in standardized space. Contributions are normalized cosine terms; the six shown need not sum to the full score.")

st.divider()

# ----------------------------
# Radar chart AFTER explanation
# ----------------------------
st.subheader("📊 Stat profile comparison")

rad = radar_data(selected_player, compare_player)

categories = rad["Feature"].tolist()
values1 = rad[selected_player].tolist() + [rad[selected_player].tolist()[0]]
values2 = rad[compare_player].tolist() + [rad[compare_player].tolist()[0]]
categories_loop = categories + [categories[0]]

fig = go.Figure()
fig.add_trace(
    go.Scatterpolar(
        r=values1,
        theta=categories_loop,
        fill="toself",
        name=selected_player
    )
)
fig.add_trace(
    go.Scatterpolar(
        r=values2,
        theta=categories_loop,
        fill="toself",
        name=compare_player
    )
)

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=True,
    title=f"{selected_player} vs {compare_player} — Radar Comparison (0–1 normalized)"
)

st.plotly_chart(fig, width="stretch")
