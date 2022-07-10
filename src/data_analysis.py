import os  
import json
from turtle import onclick
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from ast import literal_eval
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image

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
                            "key": True,
                            "url": True
                        },
                        labels={
                            "user_name": "Username", 
                            "genres": "Artist Genres", 
                            "popularity": "Popularity", 
                            "avg_artists_popularity":"Average Artists Popularity", 
                            "community_score": "Community Score",
                            "url": "Spotify URL"
                        })
    
    fig.update_layout(legend_title="Username")
    return fig

def get_stats(user_data, community_top_sorted, top_50):

    number_of_participants = len(user_data)
    number_of_unique_tracks = community_top_sorted['id'].nunique()
    number_of_shared_tracks = len(community_top_sorted) - number_of_unique_tracks

    stats = {
        "number_of_participants": number_of_participants,
        "number_of_unique_tracks": number_of_unique_tracks,
        "number_of_shared_tracks": number_of_shared_tracks
    }
    return stats

def threed_user_persona(user_data, top_50):
    qualitative = ['artist_names','genres','key','mode','speechiness','liveness','user_id']
    quantative_normalizable = ['popularity', 'danceability', 'energy', 'loudness','speechiness',
        'acousticness', 'instrumentalness', 'valence', 'mode']
    quantative_not_normalizable = ['tempo', 'duration_ms','user_id']
    # relative way of normalizing - more distinctive result / shows more persona
    quantative_normalized = top_50[quantative_normalizable].apply(lambda x: (x - x.mean())/x.std(), axis = 0)
    # absolute way of normalizing - range is [0,1], less distinctive result / a couple of features are similar among users: energy, loudness, valence, etc. 
    # quantative_normalized = (top_50[quantative_normalizable] - top_50[quantative_normalizable].min())/(top_50[quantative_normalizable].max()-top_50[quantative_normalizable].min())
    quantative_top50 = pd.concat([top_50[quantative_not_normalizable],quantative_normalized], axis = 1 )

    ##### Averaging each feature for each user
    user_average_data = quantative_top50.groupby(["user_id"]).mean()
    user_average_data = user_average_data.join(top_50[["user_id", "artist_names","genres"]].groupby(["user_id"]).nunique(), on = 'user_id')
    # using 3 criteria: 
    # 1. popularity
    # 2. dance music lover: 0.6 * danceability + 0.3 * loudness + 0.3 * energy - 0.2 * acousticness
    # 3. musical positiveness: 0.8 * valence + 0.2 * mode
    # mode -> 1: major key, mode -> 0: minor key
    user_average_data["dance_music_lover"] = user_average_data["danceability"] * 0.6 + user_average_data["loudness"] * 0.3 + user_average_data["energy"] * 0.3 - user_average_data["acousticness"] * 0.2
    user_average_data["musical_positiveness"] = user_average_data["valence"] * 0.8 + user_average_data["mode"] * 0.2
    user_average_data["user_name"] = user_average_data.index.map(lambda x: user_data[x]["displayName"])

    ##### Plotting

    fig = px.scatter_3d(user_average_data, x = 'dance_music_lover', y = 'musical_positiveness', z = 'popularity', color = 'user_name', size = 'genres', size_max = 30,
                        opacity = 0.7, labels = {'user_name': 'Username', 'dance_music_lover': 'Loves Dance Music', 'musical_positiveness': 'Enjoys Happy Music', 'popularity': 'Listens to Popular Songs',
                                                 'genres': 'Unique Numbers of Genres'} )
    
    

    fig.update_layout(margin = dict(l=0, r=0, b=0, t=0), coloraxis_colorbar=dict(yanchor="top", y=1, x=0, ticks="outside"))

    return fig

def clean_artist_genre (top_50):
    ###### Dataframe Cleanup
    artist_genre_song = top_50[["artist_names", "genres", "name"]]
    artist_genre_song["artist_names"] = artist_genre_song["artist_names"].apply(literal_eval)
    artist_genre_song["genres"] = artist_genre_song["genres"].apply(literal_eval)
    artist_genre_song = artist_genre_song.explode('artist_names')
    artist_genre_song = artist_genre_song.explode('genres')
    artist_genre_song = artist_genre_song.explode('genres')
    
    return artist_genre_song


def genre_ranking_plots(top_50):
    
    artist_genre_song = clean_artist_genre(top_50)
    ###### Creating Ranking for Genres & Artists respectively
    genre_rank = artist_genre_song[["genres", "name"]].groupby(["genres"]).nunique().sort_values(by = 'name', ascending=False)
    genre_rank = genre_rank[genre_rank["name"] > 5]
    
    d = genre_rank.to_dict()["name"]

    wordcloud = WordCloud(width = 1200, height = 800, background_color = 'white', colormap = 'Dark2')
    wordcloud.generate_from_frequencies(d)
    wc_genre = plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    font = {'family': 'numans',
        'color':  'darkred',
        'weight': 'bold',
        'size': 16,
        }
    
    plt.title("Most Listened to Genre", fontdict = font)
    plt.show()
    genre_rank_bar = genre_rank[genre_rank["name"] > 40]
    fig_genre = px.bar(genre_rank_bar, x = genre_rank_bar.index, y = 'name', labels = {'genres': 'Genre Name', 'name': "Count of Songs"})

    return wc_genre, fig_genre

def artist_ranking_plots(top_50):
    
    artist_genre_song = clean_artist_genre(top_50)
    artist_rank = artist_genre_song[["artist_names", "name"]].groupby(["artist_names"]).nunique().sort_values(by = 'name', ascending=False)
    artist_rank = artist_rank[artist_rank["name"] != 1]
    
    d = artist_rank.to_dict()["name"]

    wordcloud = WordCloud(width = 1200, height = 800, background_color = 'white', colormap = 'Dark2')
    wordcloud.generate_from_frequencies(d)
    wc_artist = plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    font = {'family': 'numans',
        'color':  'darkred',
        'weight': 'bold',
        'size': 16,
        }
    
    plt.title("Most Listened to Artist", fontdict = font)
    plt.show()

    artist_rank_bar = artist_rank[artist_rank["name"] > 5]
    fig_artist = px.bar(artist_rank_bar, x = artist_rank_bar.index, y = 'name', labels = {'artist_names': 'Artist Name', 'name': "Count of Songs"})


    return wc_artist, fig_artist








def get_mixed_songs(user_data, community_top_sorted):
    used_snippets = ["https://p.scdn.co/mp3-preview/0a51a10b22c93ee8b214fe4a87a0b37fe98687f6?cid=8304b92fe9f542b888f57fe23d484b58",
        "https://p.scdn.co/mp3-preview/0c20b9097a095cebe2ee188d97b571488f6f7a11?cid=8304b92fe9f542b888f57fe23d484b58",
        "https://p.scdn.co/mp3-preview/00d78202ee105462335f330434fcfd65c6b4337f?cid=8304b92fe9f542b888f57fe23d484b58",
        "https://p.scdn.co/mp3-preview/1c8d9a2538a002378ed49014cd83ad0c3cabdcea?cid=8304b92fe9f542b888f57fe23d484b58",
        "https://p.scdn.co/mp3-preview/4e10a7370fa085954f4f7031ef7f8507ecd16aea?cid=8304b92fe9f542b888f57fe23d484b58",
        "https://p.scdn.co/mp3-preview/44f70421ee6350765738688558dfe6c931ea14b5?cid=8304b92fe9f542b888f57fe23d484b58",
        "https://p.scdn.co/mp3-preview/1c8d9a2538a002378ed49014cd83ad0c3cabdcea?cid=8304b92fe9f542b888f57fe23d484b58"
    ]

    mixed_tracks = community_top_sorted.loc[community_top_sorted["preview_url"].isin(used_snippets)]
    mixed_tracks["pretty_name"] = mixed_tracks["name"] + " - " + mixed_tracks["artist_names"].apply(lambda x: " &".join(x[1:-1].split(',')).replace("'",""))
    mixed_tracks["user_name"] = mixed_tracks["user_id"].map(lambda x: user_data[x]["displayName"])
    return mixed_tracks
    
def main():
    user_data, top_50 = load_data("long")
    community_top_sorted = get_community_top_sorted(top_50)
    get_stats(user_data, community_top_sorted, top_50)

    fig = principal_component_analysis_plot(user_data, community_top_sorted)
    fig.show()
    
    fig_user_3d = threed_user_persona(top_50)
    fig_user_3d.show()
    
    fig_genre = genre_ranking_plots(top_50)
    fig_genre.show()
    
    fig_artist = artist_ranking_plots(top_50)
    fig_artist.show()
    

if __name__ == "__main__":
    main()
