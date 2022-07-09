import os  
import json
import pandas as pd
import umap
import seaborn as sns
import matplotlib.pyplot as plt

def load_data():
    user_data = {}
    top_50 = pd.DataFrame()

    entries = os.listdir("data/clean")
    for entry in entries:
        # Load user info
        with open("data/clean/" + entry + "/userinfo.json") as f:
            user_data[entry] = json.load(f)
        
        # Load top 50 data
        df = pd.read_csv("data/clean/" + entry + "/top50.csv")
        df["user_id"] = user_data[entry]["id"]
        top_50 = top_50.append(df, ignore_index=True)
    return user_data, top_50


def main():
    user_data, top_50 = load_data()

    exit()
    data = top_50[['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                    'duration_ms', 'time_signature']]
    n_neighbors=15 
    min_dist=0.4 
    n_components=2 
    metric='braycurtis'

    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist,
                        n_components=n_components, metric=metric, random_state=42)
    embedding = reducer.fit_transform(data)
    df_embedding = pd.DataFrame(data=embedding, columns=["dim" + str(x) for x in range(1, n_components+1)], index=data.index)
    df_embedding["hue"] = top_50["user_id"]

    sns.scatterplot(x='dim1', y='dim2', hue="hue", data=df_embedding)
    plt.savefig("image", bbox_inches="tight")
    # return reducer, df_embedding

if __name__ == "__main__":
    main()
