import streamlit as st
import pandas as pd
import numpy as np

from src.data_analysis import principal_component_analysis_plot, threed_user_persona, genre_ranking_plots, artist_ranking_plots, get_community_top_sorted, load_data

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})
st.latex(r'''
     \textrm{Welcome to (The Sound of)}^2 \textrm{AI Community}
     ''')
st.write("Work in progress! Thank you for participating :)")

user_data, community_top_50 = load_data(timeframe="long")

community_data = get_community_top_sorted(community_top_50)

fig = principal_component_analysis_plot(user_data, community_data)

fig_user_3d = threed_user_persona(user_data, community_top_50)

wc_genre, fig_genre = genre_ranking_plots(community_top_50)

wc_artist, fig_artist = artist_ranking_plots(community_top_50)
st.write('Principal Component Analysis of Community Songs')
st.plotly_chart(fig)
st.write('User Persona Relative to Community')
st.plotly_chart(fig_user_3d)
st.markdown('''<p style="font-size:11">Please note that the features are calculated in the following ways:
            <br> Popularity: popularity of the song
            <br> Loves Dance Music: 0.6 * danceability + 0.3 * loudness + 0.3 * energy - 0.2 * acousticness
            <br> Enjoys Happy Music (Musical Positiveness): 0.8 * valence + 0.2 * mode
            <br> The size of the user is reflected by the number of unique genres they listen to.
            
            
            </p>''', unsafe_allow_html=True)
st.write('Most Listened to Genre')
st.pyplot(wc_genre)
st.plotly_chart(fig_genre)
st.write('Most Listened to Artist')
st.pyplot(wc_artist)
st.plotly_chart(fig_artist)




