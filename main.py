import streamlit as st
import pandas as pd
import numpy as np

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df= pd.DataFrame(
    np.random.randn(10, 2),
    columns=['x', 'y'])
st.bar_chart(df)

st.latex(r'''
     The Sound of^2 AI
     ''')

st.write("(The Sound of)^2 AI Community")
st.write("WORK IN PROGRESS!")
st.write("Here we will show the final analysis when we are ready.")
st.write("Thank you for participation! :D")
