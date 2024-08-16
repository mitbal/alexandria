import streamlit as st

import raftel as rt

st.title('Raftel')

option = st.radio('Select Input Type', ['Coordinate', 'S2ID'])

if option == 'Coordinate':

    lat = st.text_input('Insert Latitude', '-6.1944')
    lon = st.text_input('Insert Longitude', '106.8229')

    s2id_level = st.number_input('Insert S2ID level', value=7)

import os

api_key = os.environ['STADIA_API_KEY']

s2id = rt.get_s2id(float(lat), float(lon), s2id_level)
peta = rt.plot_s2id([s2id], api_key=api_key)

st.image(peta)
