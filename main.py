import streamlit as st
import pandas as pd
import numpy as np

from src.data_analysis import principal_component_analysis_plot, get_mixed_songs, get_stats, threed_user_persona, get_community_top_sorted, load_data

st.latex(r'''
     \textrm{Welcome to (The Sound of)}^2 \textrm{AI Community}
     ''')

user_data, community_top_50 = load_data(timeframe="long")

community_data_sorted = get_community_top_sorted(community_top_50)

fig = principal_component_analysis_plot(user_data, community_data_sorted)

fig_user_3d = threed_user_persona(user_data, community_top_50)

stats = get_stats(user_data, community_data_sorted, community_top_50)
col1, col2, col3 = st.columns(3)
col1.metric("Number of participants", stats["number_of_participants"])
col2.metric("Number of unique tracks", stats["number_of_unique_tracks"])
col3.metric("Number of shared tracks", stats["number_of_shared_tracks"])


st.write('Principal Component Analysis of Community Songs')
st.plotly_chart(fig)

st.write('User Persona Relative to Community')
st.plotly_chart(fig_user_3d)
st.markdown('''<p style="font-size:11"> Please note that the features are calculated in the following ways:
            <br> Popularity: popularity of the song
            <br> Loves Dance Music: 0.6 * danceability + 0.3 * loudness + 0.3 * energy - 0.2 * acousticness
            <br> Enjoys Happy Music (Musical Positiveness): 0.8 * valence + 0.2 * mode
            <br> The size of the user is reflected by the number of unique genres they listen to.
            </p>
            ''', unsafe_allow_html=True)

st.write('Most Listened to Genre')
st.image("./images/genre.png")
st.image("./images/genre-bar.png")

st.write('Most Listened to Artist')
st.image("./images/artist.png")
st.image("./images/artist-bar.png")
st.write('These are the song used in the mix:')
songs = get_mixed_songs(user_data, community_data_sorted)
st.dataframe(songs)

audio_file = open('thesoundofsoundofai.wav', 'rb')
audio_bytes = audio_file.read()

st.write('Generated theme song for the first The Sound of AI Hackathon!')
st.audio(audio_bytes, format="audio/wav", start_time=0)