"""Regenerate README visuals and example tables from the bundled snapshot."""
from pathlib import Path
import sys,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src import recommender as r

def main():
    r.initialize()
    df,sim=r.build_similarity_model(r.load_data())
    X=StandardScaler().fit_transform(df[r.FEATURES])
    (ROOT/'figures').mkdir(exist_ok=True);(ROOT/'results').mkdir(exist_ok=True)
    recs=r.recommend('Jayson Tatum');recs.to_csv(ROOT/'results/tatum_recommendations.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':'#fbfaf7','axes.facecolor':'#fbfaf7','savefig.facecolor':'#fbfaf7','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'text.color':'#24343d'})
    fig,ax=plt.subplots(figsize=(10,4.7));bars=ax.barh(recs.Player[::-1],recs.Similarity[::-1],color='#557e80',height=.6)
    ax.set(xlim=(0,1.03),xlabel='Cosine similarity of standardized statistical profiles',title='Who profiles most like Jayson Tatum?')
    ax.bar_label(bars,fmt='%.3f',padding=5)
    fig.text(.5,.015,'2024–25 snapshot • 356 complete player profiles • scores are not probabilities',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(ROOT/'figures/tatum_recommendations.png',dpi=160);plt.close(fig)
    pca=PCA(n_components=2);coords=pca.fit_transform(X)
    fig,ax=plt.subplots(figsize=(10,6.3));palette=['#557e80','#c08b57','#7e7397','#7c9658','#bd7475']
    for pos,col in zip(sorted(df.Pos.unique()),palette):
        mask=df.Pos.eq(pos).to_numpy();ax.scatter(coords[mask,0],coords[mask,1],s=22,alpha=.65,label=pos,color=col)
    for player in ['Jayson Tatum','Stephen Curry','Nikola Jokić','Rudy Gobert']:
        matches=df.index[df.Player.eq(player)]
        if len(matches):
            i=matches[0];ax.annotate(player,coords[i],xytext=(6,9),textcoords='offset points',fontsize=9)
    ax.set(title='A two-dimensional view of player profiles',xlabel=f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)',ylabel=f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)');ax.legend(frameon=False,title='Position')
    fig.text(.5,.015,'PCA is a visualization only; recommendations use all 14 standardized features.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(ROOT/'figures/player_map.png',dpi=160);plt.close(fig)
    compare='LeBron James';ids=[df.index[df.Player.eq(n)][0] for n in ['Jayson Tatum',compare]]
    labels=['Points / game','Field goal %','Three-point %','Free throw %','Assists / game','Turnovers / game','Usage %','Steals / game','Blocks / game','Defensive rebounding %','True shooting %','Player efficiency rating','Win shares / 48','Box plus/minus']
    fig,ax=plt.subplots(figsize=(10,6));y=np.arange(len(labels));ax.barh(y-.17,X[ids[0]],height=.33,label='Jayson Tatum',color='#557e80');ax.barh(y+.17,X[ids[1]],height=.33,label=compare,color='#c08b57');ax.invert_yaxis();ax.set_yticks(y,labels);ax.axvline(0,color='#aeb6b8',lw=.7);ax.set(xlabel='Standard deviations from the eligible-player mean',title='Inside the comparison: Tatum and LeBron');ax.legend(frameon=False)
    fig.text(.5,.015,'Higher means more of the statistic, not necessarily better (for example, turnovers).',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(ROOT/'figures/profile_comparison.png',dpi=160);plt.close(fig)
    pd.DataFrame(coords,columns=['PC1','PC2']).assign(Player=df.Player,Pos=df.Pos).to_csv(ROOT/'results/player_map.csv',index=False)
    (ROOT/'results/summary.json').write_text(json.dumps({'snapshot_rows':len(r.load_data()),'eligible_players':len(df),'features':r.FEATURES,'pca_explained_variance_ratio':pca.explained_variance_ratio_.tolist()},indent=2)+'\n')
    print(recs.to_string(index=False));print('Visuals and example outputs regenerated from snapshot.')
if __name__=='__main__':main()
