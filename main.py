import streamlit as st

page_home = st.Page('home.py', title='Home', icon='📚')
page_lesley = st.Page('apps/lesley/lesley.py', title='Lesley', icon='📅')
page_floryn = st.Page('apps/floryn/floryn.py', title='Floryn', icon='🌼')
page_raftel = st.Page('apps/raftel/raftel.py', title='Raftel', icon='🟩')
page_monoch = st.Page('apps/monochromap/monochromap.py', title='Monochromap', icon='🗺️')
pages = st.navigation(
    {
        'Home': [page_home],
        'Libraries': [page_lesley, page_floryn, page_raftel, page_monoch]
    }
)

pages.run()
