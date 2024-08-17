import os
import raftel as rt
import streamlit as st

st.image('pages/raftel_banner.png', width=1000)
st.title('Raftel')

cols = st.columns([0.2, 0.8])

with cols[0]:
    with st.form('s2_form'):

        lat = st.text_input('Insert Latitude', '-6.1944')
        lon = st.text_input('Insert Longitude', '106.8229')
        s2id_level = st.number_input('Insert S2ID level', value=9)

        submit = st.form_submit_button('submit')


api_key = os.environ['STADIA_API_KEY']

with cols[1]:
    if submit:
        s2id = rt.get_s2id(float(lat), float(lon), s2id_level)
        peta = rt.plot_s2id([s2id], api_key=api_key)

        st.image(peta)
