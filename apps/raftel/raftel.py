import os
import raftel as rt
import streamlit as st

st.set_page_config(layout='wide')

st.title('Raftel')
api_key = os.environ['STADIA_API_KEY']

reset_button = st.button(label='Reset Map')
if reset_button:
    if 'peta' in st.session_state:
        del st.session_state['peta']

cols = st.columns([0.25, 0.75])
with cols[0]:
    with st.form('s2_form'):

        lat = st.number_input('Insert Latitude', value=-6.1944, min_value=-180., max_value=180.)
        lon = st.number_input('Insert Longitude', value=106.8229, min_value=-180., max_value=180.)
        s2id_level = st.number_input('Insert S2ID level', value=9, min_value=0, max_value=30)
        alpha = st.number_input('Select Rectangle Transparency', value=0.5, min_value=0., max_value=1.0)
        color = st.color_picker('Select Rectangle Color', value='#00ff00')

        submit = st.form_submit_button('submit')
        if submit:
            s2id = rt.get_s2id(float(lat), float(lon), s2id_level)
            if 'peta' not in st.session_state:
                st.session_state['peta'] = rt.plot_s2id([s2id], api_key=api_key, color=color, alpha=alpha, auto_render=False)
            else:
                st.session_state['peta'] = rt.plot_s2id([s2id], api_key=api_key, color=color, alpha=alpha, auto_render=False, m=st.session_state['peta'])

            st.write(f'adding S2ID {s2id}')


with cols[1]:
    if 'peta' in st.session_state:
        st.image(st.session_state['peta'].render())
    else:
        st.image('apps/raftel/raftel_placeholder.png')
