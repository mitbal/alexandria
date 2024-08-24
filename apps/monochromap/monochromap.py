import os
import streamlit as st
import monochromap as mono

st.title('Monochromap')


reset_button = st.button(label='Reset Map')
if reset_button:
    if 'peta' in st.session_state:
        del st.session_state['peta']

cols = st.columns([0.3, 0.7])
with cols[0]:
    
    shape = st.selectbox('Select type of object', ['Point', 'Line', 'Image'])
    with st.form('canvas'):

        if shape == 'Point':
            lat = st.number_input('Input Latitude', value=-6.1944)
            lon = st.number_input('Input Longitude', value=106.8229)
            rad = st.number_input('Input Radius', value=5, min_value=0, max_value=100)
            alpha = st.number_input('Input Transparency', value=.95, min_value=.0, max_value=1.00)
            color = st.color_picker('Select Color', value='#ff0000')

        elif shape == 'Line':
            cols_form = st.columns(2)
            with cols_form[0]:
                lat1 = st.number_input('Input Lat Point 1', value=-6.0686695, min_value=-180., max_value=180.)
                lon1 = st.number_input('Input Lon Point 1', value=105.8847784, min_value=-180., max_value=180.)
                rad = st.number_input('Input Line Width', value=5, min_value=0, max_value=100)
                color = st.color_picker('Input Line Color', value='#ff0000')

            with cols_form[1]:
                lat2 = st.number_input('Input Lat Point 2', value=-7.693067, min_value=-180., max_value=180.)
                lon2 = st.number_input('Input Lon Point 2', value=113.9266419, min_value=-180., max_value=180.)
                alpha = st.number_input('Input Line Transparency', value=.95, min_value=.0, max_value=1.00)

        elif shape == 'Image':
            icon = st.file_uploader('Select Image File', type=['png', 'jpg'])
            lat = st.number_input('Input Latitude', value=-6.1944, min_value=-180., max_value=180.)
            lon = st.number_input('Input Longitude', value=106.8229, min_value=-180., max_value=180.)

        submit = st.form_submit_button('Add to map')
        if submit:
            error = False
            if shape == 'Point':
                obj = mono.Point((float(lon), float(lat)), f'{color}{int(alpha*256):02x}', rad)
            elif shape == 'Line':
                obj = mono.Line(coords=[(lon1, lat1), (lon2, lat2)], color=f'{color}{int(alpha*256):02x}', width=rad)
            elif shape == 'Image':
                if icon is not None:
                    obj = mono.IconMarker(coord=(float(lon), float(lat)), file_path=icon, offset_x=0, offset_y=0)
                else:
                    st.error('Please select an image first before adding to the map')
                    error = True
            
            if not error:
                if 'peta' not in st.session_state:
                    st.session_state['peta'] = mono.MonochroMap(api_key=os.environ['STADIA_API_KEY'])
                st.session_state['peta'].add_feature(obj)

with cols[1]:
    if 'peta' in st.session_state:
        img = st.session_state['peta'].render()
        st.image(img)
    else:
        st.image('apps/monochromap/monochromap_placeholder.png')
