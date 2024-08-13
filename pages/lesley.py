import lesley
import streamlit as st

import numpy as np
import pandas as pd

st.set_page_config(layout='wide')
st.title('Lesley')

use_random = st.radio('Select one', ['True', 'False'])

if use_random:
    dates = pd.date_range(start='2024-01-01', end='2024-12-31')
    values = np.random.randint(0, 10, size=len(dates))
else:
    st.stop()

heatmap_container = st.container()
with heatmap_container:
    height=270
    chart_heatmap = lesley.cal_heatmap(dates, values)
    st.altair_chart(chart_heatmap, use_container_width=False)
