import os  
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA

# Ignore pandas deprecated warnings... We are hacking...
import warnings
warnings.filterwarnings('ignore')

def load_data(timeframe="long"):
    user_data = {}
    top_50 = pd.DataFrame()

    entries = os.listdir("data/clean")
    for entry in entries:
        # Load user info
        with open("data/clean/" + entry + "/userinfo.json") as f:
            user_data[entry] = json.load(f)
        
        # Load top 50 data
        df = pd.read_csv("data/clean/" + entry + f"/top50-{timeframe}.csv")
        df["user_id"] = user_data[entry]["id"]
        top_50 = top_50.append(df, ignore_index=True)
    return user_data, top_50


def get_community_top_sorted(top_50):
    # Count track accurences
    song_occurences = top_50.groupby(["id"])["id"].count()
    top_50 = pd.merge(top_50, song_occurences, left_on='id', right_index=True, how='inner')
    top_50.drop(["id_x", "id_y"], axis=1, inplace=True)

    # Community score weighted by user scores
    top_50["community_score"] = top_50["user_score"].groupby(top_50["id"]).transform("sum")
    top_50.drop(["user_score"], axis=1, inplace=True)

    # Sort by community score
    top_50.sort_values("community_score",ascending=False, inplace=True)

    # Drop duplicates
    top_50.drop_duplicates(subset=["id"], inplace=True)

    return top_50


def principal_component_analysis_plot(user_data, community_top_sorted):
    # Sort features
    qualitative = ['artist_names','genres','key','mode','speechiness','liveness','user_id']
    quantative_normalizable = ['avg_artists_popularity', 'popularity', 'danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'mode']
    quantative_not_normalizable = ['tempo', 'duration_ms', "user_id"]
    
    # Normalise features
    quantative_normalized = community_top_sorted[quantative_normalizable].apply(lambda x: (x - x.mean())/x.std(), axis = 0)

    # Reduce dimentions to 3 based on normalized quantative values of audio properties 
    pca = PCA(n_components=3)
    pca.fit(quantative_normalized)

    pca_data = pd.DataFrame(pca.transform(quantative_normalized), columns=["pca1","pca2","pca3"])

    df = pd.concat([pca_data.reset_index(), community_top_sorted.reset_index()], axis=1)

    # Pretty print
    df["pretty_name"] = df["name"] + " - " + df["artist_names"].apply(lambda x: " &".join(x[1:-1].split(',')).replace("'",""))
    df["user_name"] = df["user_id"].map(lambda x: user_data[x]["displayName"])

    # Create plot
    fig = px.scatter_3d(df, x='pca1', y='pca2', z='pca3', color='user_name', size='community_score', size_max=30,
                        opacity=0.7, hover_name="pretty_name", 
                        hover_data={
                            "pca1": False, 
                            "pca2": False, 
                            "pca3": False, 
                            "user_name": True, 
                            "genres": True, 
                            "popularity": True, 
                            "avg_artists_popularity": True, 
                            "tempo": True,
                            "key": True
                        },
                        labels={
                            "user_name": "User Name", 
                            "genres": "Artist Genres", 
                            "popularity": "Popularity", 
                            "avg_artists_popularity":"Average Artists Popularity", 
                            "community_score": "Community Score"
                        })
    
    fig.update_layout(legend_title="User Name")
    return fig

def main():
    user_data, top_50 = load_data("long")

    community_top_sorted = get_community_top_sorted(top_50)
    fig = principal_component_analysis_plot(user_data, community_top_sorted)
    fig.show()

if __name__ == "__main__":
    main()
