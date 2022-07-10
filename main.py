import streamlit as st
import pandas as pd
import numpy as np

from src.data_analysis import principal_component_analysis_plot, get_community_top_sorted, load_data

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

st.plotly_chart(fig)