import streamlit as st
# import streamlit_analytics2 as streamlit_analytics

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
page_vortree = st.Page('apps/vortree/vortree.py', title='Voronoi Treemap', icon='🌀')
# page_csv_explorer = st.Page('apps/csv_explorer/csv_explorer.py', title='CSV Explorer', icon='📊')
page_finplot = st.Page('apps/finplot/finplot.py', title='FinPlot', icon='💹')
page_reddit = st.Page('apps/reddit_stats/reddit_stats.py', title='Reddit Stats', icon='🤖')
page_report_montage = st.Page('apps/report_montage/report_montage.py', title='Annual Report Montage', icon='🖼️')

pages = st.navigation(
    {
        'Home': [page_home],
        'Libraries': [page_lesley, page_floryn, page_raftel, page_monoch, page_mbg, page_vortree],
        'Utilities': [page_finplot, page_reddit, page_report_montage],
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

image_html = get_img_with_href('panen_dividen.svg', 'https://panendividen.com?utm_source=alexandria')
st.sidebar.markdown(image_html, unsafe_allow_html=True)

# with streamlit_analytics.track():
#     pages.run()

pages.run()
