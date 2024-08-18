import os
import streamlit as st
import monochromap as mono

st.title('Monochromap')


reset_button = st.button(label='Reset Map')
if reset_button:
    if 'peta' in st.session_state:
        del st.session_state['peta']

shape = st.selectbox('Select type of object', ['Point', 'Line', 'Image'])
with st.form('canvas'):

    if shape == 'Point':
        lat = st.number_input('Input Latitude', value=-6.1944)
        lon = st.number_input('Input Longitude', value=106.8229)
    elif shape == 'Line':
        cols = st.columns(2)
        with cols[0]:
            lat1 = st.number_input('Input Lat Point 1', value=-6.0686695, min_value=-180., max_value=180.)
            lon1 = st.number_input('Input Lon Point 1', value=105.8847784, min_value=-180., max_value=180.)
        with cols[1]:
            lat2 = st.number_input('Input Lat Point 2', value=-7.693067, min_value=-180., max_value=180.)
            lon2 = st.number_input('Input Lon Point 2', value=113.9266419, min_value=-180., max_value=180.)

    submit = st.form_submit_button('Add to map')
    if submit:

        if 'peta' not in st.session_state:
            st.session_state['peta'] = mono.MonochroMap(api_key=os.environ['STADIA_API_KEY'])

        if shape == 'Point':
            obj = mono.Point((float(lon), float(lat)), '#fb294344', 5)
        elif shape == 'Line':
            obj = mono.Line(coords=[(lon1, lat1), (lon2, lat2)], color='#fb294344', width=5)
        st.session_state['peta'].add_feature(obj)

if 'peta' in st.session_state:
    img = st.session_state['peta'].render()
    st.image(img)
else:
    st.image('pages/monochromap_placeholder.png')