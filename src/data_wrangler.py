"""
Parses the user json files received from the web app and saves in a clean format. 
The code enriches the data with audio features pulled from the Spotify API based on users top 50 track ids.
Requires a .env file with correctly specified Spotify credentials, i.e. SPOTIPY_CLIENT_ID="" SPOTIPY_CLIENT_SECRET="".
"""
from dotenv import load_dotenv
load_dotenv()
import os  
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Setup credentials with spotify api. Reads secrets from .env
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# Wrangle data
entries = os.listdir("data/raw")
for entry in entries:
    # Parse the user information
    user_info_file_path = "data/raw/" + entry + "/userinfo.json"

    # Read user info
    with open(user_info_file_path) as f:
        user_data = json.load(f)

    # Parse json format to csv friendly format
    user_info = {
        "displayName": user_data["display_name"],
        "id": user_data["id"],
        "imageUrl": user_data["images"][0]["url"] if user_data.get("images") is not None and len(user_data["images"]) > 0 else "",
        "userUrl": user_data["external_urls"]["spotify"]
    }

    # Create directory for clean data
    folder_path = f"data/clean/{user_info['id']}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Write csv file to disk
    with open(folder_path + '/userinfo.json', 'w') as outfile:
        json.dump(user_info, outfile)

    # Read track data
    top_50_file_path = "data/raw/" + entry + "/top50-long.json"
    with open(top_50_file_path) as f:
        top50_data = json.load(f)
    
    # Parse track json object to csv friendly format
    tracks = []
    for track in top50_data["items"]:
        track_data = {
            "id": track["id"],
            "name": track["name"],
            "popularity": track["popularity"],
            "url": track["external_urls"]["spotify"],
            "artist_ids": [artist["id"] for artist in track["artists"]],
            "artist_names": [artist["name"] for artist in track["artists"]],
        }
        tracks.append(track_data)
    tracks_df = pd.DataFrame(tracks)
    
    # Get audio features for each track
    audio_features = sp.audio_features(tracks_df["id"])
    features_df = pd.DataFrame(audio_features).drop(["analysis_url", "type", "track_href", "uri"], axis=1)
    
    # Merge track information and audio features
    merged_df = pd.merge(tracks_df, features_df, left_on='id', right_on='id', how='inner')
    
    # Write csv file to disk
    merged_df.to_csv(folder_path+ "/top50.csv", index=False)