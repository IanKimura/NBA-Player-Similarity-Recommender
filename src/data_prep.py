
import pandas as pd
from pathlib import Path

SEASON = 2025  # NBA_2025_* pages = 2024-25 season
URLS = {
    "per_game": f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_per_game.html",
    "per100":   f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_per_poss.html",
    "advanced": f"https://www.basketball-reference.com/leagues/NBA_{SEASON}_advanced.html",
}

def load_bbr_table(url: str) -> pd.DataFrame:
    df = pd.read_html(url)[0]
    # Drop repeated header rows inside the table
    df = df[df['Player'] != 'Player'].copy()
    # Remove * markers in names
    df['Player'] = df['Player'].str.replace(r'\*', '', regex=True)
    return df

def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    keep_str = {'Player','Pos','Tm','Team','Rk'}
    for c in df.columns:
        if c in keep_str:
            continue
        df[c] = pd.to_numeric(df[c].astype(str).str.replace('%','', regex=False), errors='coerce')
    return df

def keep_tot_row(df: pd.DataFrame) -> pd.DataFrame:
    team_col = 'Tm' if 'Tm' in df.columns else ('Team' if 'Team' in df.columns else None)

    def pick_row(g: pd.DataFrame) -> pd.DataFrame:
        if team_col:
            total = g[team_col].astype(str).str.match(r"^(TOT|\d+TM)$")
            if total.any():
                return g[total].head(1)
        for cand in ['MP', 'MP_per_g', 'G']:
            if cand in g.columns:
                return g.sort_values(cand, ascending=False).head(1)
        return g.head(1)

    chunks = [pick_row(g) for _, g in df.groupby('Player', sort=False)]
    return pd.concat(chunks, ignore_index=True)

def fetch_merge_2025() -> pd.DataFrame:
    per_game = coerce_numeric(load_bbr_table(URLS['per_game']))
    per100   = coerce_numeric(load_bbr_table(URLS['per100']))
    adv      = coerce_numeric(load_bbr_table(URLS['advanced']))

    per_game = keep_tot_row(per_game)
    per100   = keep_tot_row(per100)
    adv      = keep_tot_row(adv)

    # Choose ids + feature subsets
    id_cols = ['Player','Pos']

    per_game_feats = ['G','MP','FG','FGA','FG%','3P','3PA','3P%','2P','2PA','2P%','FT','FTA','FT%',
                      'ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS']
    per100_feats   = ['G','MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%',
                      'ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS']
    adv_feats      = ['G','MP','PER','TS%','3PAr','FTr','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%','USG%',
                      'OWS','DWS','WS','WS/48','OBPM','DBPM','BPM','VORP']

    def keep(df, feats, suffix):
        cols = id_cols + [c for c in feats if c in df.columns]
        out = df[cols].copy()
        out = out.rename(columns={c: f"{c}{suffix}" for c in feats if c in out.columns})
        return out

    pg  = keep(per_game, per_game_feats, '_pg')
    p100= keep(per100,   per100_feats,   '_p100')
    adv = keep(adv,      adv_feats,      '_adv')

    on_keys = ['Player','Pos']
    merged = pg.merge(p100, on=on_keys, how='inner').merge(adv, on=on_keys, how='inner')

    # Minutes-qualified filter (stable comps)
    mp_col = 'MP_pg' if 'MP_pg' in merged.columns else ('MP_adv' if 'MP_adv' in merged.columns else None)
    if mp_col:
        if 'G_pg' in merged.columns and mp_col == 'MP_pg':
            merged['MP_total_est'] = merged['G_pg'] * merged['MP_pg']
        elif mp_col == 'MP_adv':
            merged['MP_total_est'] = merged['MP_adv']
        else:
            merged['MP_total_est'] = merged[mp_col]
        merged = merged[merged['MP_total_est'] >= 500].copy()

    return merged.sort_values('Player').reset_index(drop=True)


def main():
    """
    Run the data pipeline and save the cleaned NBA dataset to CSV.
    """
    # Run your existing pipeline
    df = fetch_merge_2025()

    # Figure out repo root (one level above /src)
    repo_root = Path(__file__).resolve().parents[1]

    # Create data/ folder if it doesn't exist
    data_dir = repo_root / "data"
    data_dir.mkdir(exist_ok=True)

    # Save CSV
    output_path = data_dir / "nba_2025_clean.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved dataset with {len(df)} players to {output_path}")

    
if __name__ == "__main__":
    main()

