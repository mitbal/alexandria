import os
import streamlit as st
import monochromap as mono

st.title('Monochromap')

with st.form('canvas'):

    st.selectbox('Select type of object', ['Point'])

    lat = st.text_input('Input Latitude')
    lon = st.text_input('Input Longitude')

    submit = st.form_submit_button('Add to map')
    if submit:

        if 'peta' not in st.session_state:
            st.session_state['peta'] = mono.MonochroMap(api_key=os.environ['STADIA_API_KEY'])

        p = mono.Point((float(lon), float(lat)), '#fb294344', 5)
        st.session_state['peta'].add_feature(p)

if 'peta' in st.session_state:
    img = st.session_state['peta'].render()
    st.image(img)
else:
    st.image('pages/monochromap_placeholder.png')