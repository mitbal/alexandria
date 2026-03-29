import streamlit as st

st.title('The Great Library of Alexandria')

with open('README.md', 'r') as f:
    readme = f.read()
st.markdown(readme)
