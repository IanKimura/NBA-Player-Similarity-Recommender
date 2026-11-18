"""Regression checks for ranking, explanations, and snapshot handling."""
import unittest
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src import recommender as r
from src.data_prep import keep_tot_row

class RecommenderTests(unittest.TestCase):
    def setUp(self):r.initialize()

    def test_snapshot_rankings_exclude_self_and_are_sorted(self):
        for player in r.get_player_names():
            recs=r.recommend(player,5)
            self.assertEqual(len(recs),5)
            self.assertNotIn(player,recs.Player.tolist())
            self.assertTrue(recs.Similarity.is_monotonic_decreasing)
        self.assertEqual(r.recommend('Jayson Tatum').Player.iloc[0],'LeBron James')

    def test_tied_profile_does_not_recommend_self(self):
        # Force an exact-vector tie where the query is not first in stable order.
        df=r.load_data().iloc[:2].copy()
        for feature in r.FEATURES:df[feature]=1.0
        r._df_model,r._sim_matrix=r.build_similarity_model(df)
        query=df.Player.iloc[1]
        self.assertEqual(r.recommend(query,1).Player.tolist(),[df.Player.iloc[0]])

    def test_explanation_contributions_match_cosine(self):
        rows=r.explain_similarity('Stephen Curry','Damian Lillard',len(r.FEATURES))
        i=r._player_index('Stephen Curry');j=r._player_index('Damian Lillard')
        self.assertAlmostEqual(rows['Cosine Contribution'].sum(),r._sim_matrix[i,j],delta=.008)

    def test_invalid_requests_and_missing_features(self):
        for n in [0,-1,True,1.5]:
            with self.assertRaises(ValueError):r.recommend('Jayson Tatum',n)
        with self.assertRaises(ValueError):r.explain_similarity('Unknown','Jayson Tatum')
        with self.assertRaises(ValueError):r.build_similarity_model(pd.DataFrame({'Player':['A','B']}))

    def test_multi_team_total_row_is_preferred(self):
        df=pd.DataFrame({'Player':['A','A','A'],'Team':['BOS','LAL','2TM'],'MP':[32,35,30]})
        self.assertEqual(keep_tot_row(df).Team.iloc[0],'2TM')

if __name__=='__main__':unittest.main()
