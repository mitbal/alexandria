import os
import raftel as rt
import streamlit as st

st.set_page_config(layout='wide')

st.image('apps/raftel/raftel_banner.png', width=1000)
st.title('Raftel')

cols = st.columns([0.25, 0.75])

with cols[0]:
    with st.form('s2_form'):

        lat = st.number_input('Insert Latitude', value=-6.1944, min_value=-180., max_value=180.)
        lon = st.number_input('Insert Longitude', value=106.8229, min_value=-180., max_value=180.)
        s2id_level = st.number_input('Insert S2ID level', value=9, min_value=0, max_value=30)
        alpha = st.number_input('Select Rectangle Transparency', value=0.5, min_value=0., max_value=1.0)
        color = st.color_picker('Select Rectangle Color', value='#00ff00')

        submit = st.form_submit_button('submit')


api_key = os.environ['STADIA_API_KEY']

with cols[1]:
    if submit:
        s2id = rt.get_s2id(float(lat), float(lon), s2id_level)
        peta = rt.plot_s2id([s2id], api_key=api_key, color=color, alpha=alpha)

        st.write(f'S2ID {s2id}')
        st.image(peta)
