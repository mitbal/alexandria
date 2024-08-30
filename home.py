import streamlit as st

st.set_page_config(
    page_title='Home',
    page_icon='📚',
    layout='wide'
)

st.title('The Great Library of Alexandria')

with open('README.md', 'r') as f:
    readme = f.read()
st.markdown(readme)
