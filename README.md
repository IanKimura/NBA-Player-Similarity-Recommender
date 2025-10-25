# 🏀 NBA Player Similarity Recommender (2024–25 Season)

A **content-based recommender system** that suggests NBA players similar in statistical performance to a selected player for the 2024–25 season.

---

## 🎯 Project Overview
This project builds a **player similarity model** using advanced basketball metrics to recommend players with comparable styles and production. Users can select any player and instantly view the most statistically similar players, complete with similarity scores and visual comparisons.

---

## ⚙️ Tech Stack
- **Python** (pandas, scikit-learn, plotly)
- **Streamlit** (interactive web dashboard)
- **NBA API / Basketball Reference** (data source)
- **Cosine Similarity** (similarity metric)
- **PCA** (optional dimensionality reduction)

---

## 🚀 Features
- Input a player name and get top-N similar players.
- Scaled and normalized statistical comparison.
- Interactive Streamlit dashboard.
- PCA scatter visualization for player clusters.
- Easy to expand with radar charts or filters.

---

## 🧠 How It Works
1. Collects 2024–25 season data.
2. Standardizes numeric features for fair comparison.
3. Computes **cosine similarity** between all player vectors.
4. Displays top similar players with similarity scores.

---

## 📦 Setup
```bash
git clone https://github.com/yourusername/nba-player-recommender.git
cd nba-player-recommender
pip install -r requirements.txt
streamlit run app/app.py
