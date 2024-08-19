import floryn
import streamlit as st

st.title('Floryn')

cols = st.columns(3)

text = cols[0].text_input('Input Text Here', value='FY2024 Revenue: 100.19B IDR')
percentage = cols[1].number_input('Insert Percentage Here', value=0.9544)
orientation = cols[2].selectbox('Select Orientation', ['horizontal', 'vertical'])

img = floryn.pp(text=text, percentage=percentage, orientation=orientation)

st.image(img)
