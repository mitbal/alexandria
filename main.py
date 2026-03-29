import streamlit as st

st.set_page_config(
    page_title='Home',
    page_icon='📚',
    layout='wide'
)

page_home = st.Page('home.py', title='Home', icon='📚')
page_lesley = st.Page('apps/lesley/lesley.py', title='Lesley', icon='📅')
page_floryn = st.Page('apps/floryn/floryn.py', title='Floryn', icon='🌼')
page_raftel = st.Page('apps/raftel/raftel.py', title='Raftel', icon='🟩')
page_monoch = st.Page('apps/monochromap/monochromap.py', title='Monochromap', icon='🗺️')
page_mbg = st.Page('apps/mbg/mbg.py', title='MBG Plot', icon='🍱')

pages = st.navigation(
    {
        'Home': [page_home],
        'Libraries': [page_lesley, page_floryn, page_raftel, page_monoch, page_mbg]
    }
)

st.sidebar.html('Other project<br/><a href=https://panendividen.com>Panen Dividen</a>')

pages.run()
