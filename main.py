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

import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_href(local_img_path, target_url):
    img_format = 'svg+xml'
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'Visit Other Project:<br/><a href="{target_url}"><img src="data:image/{img_format};base64,{bin_str}" width="200"></a>'
    return html_code

image_html = get_img_with_href('panen_dividen.svg', 'https://panendividen.com')
st.sidebar.html(image_html)

pages.run()
