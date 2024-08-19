import streamlit as st

st.set_page_config(
    page_title='Home',
    page_icon='📚',
    layout='wide'
)

st.title('The Great Library of Alexandria')

"""
Welcome to the Great Library of Alexandria. 
This is a collection of python libraries that I've published which I found to be really helpful on my day-to-day job as data analyst/scientist/machine learning engineer/consultant.

### 1. Lesley
Lesley is a library to show heatmap on calendar data. It is heavily inspired by another package called July, but instead of matplotlib, Lesley used altair, which in turn use vega, as the backend. This enable to add interactivity in the figure, such as tooltip, which is really helpful when doing exploratory analysis.

### 2. Floryn
Floryn is a library to plot text filled in percentage, instead of full. This can be used to highlight the difference or ratio between several values or metrics.

3. Raftel
Raftel is a library to plot s2id into the map. S2ID is a way to perform geospatial analysis by dividing the map into quad tree. More about S2ID and its difference compare to other algorithm such as geohash or H3 can be learned further in this article.

4. Monochromap
Monochromap is a library to plot on top of black and white map, or what we in the industry called Stamen Toner tile style. The black and white, instead of for example default tile style provided by google maps or open street maps, make it easier to highlight certain geographical features like places of point of interest.

"""
