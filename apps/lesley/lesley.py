import lesley
import streamlit as st

import numpy as np
import pandas as pd

import calendar

st.title('Lesley')

cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'YlGn']

use_random = st.radio('Use Random Data?', ['True', 'False'])
if use_random == 'True':
    dates = pd.date_range(start='2024-01-01', end='2024-12-31')
    values = np.random.randint(0, 10, size=len(dates))
else:
    st.write('Provide csv files with at least 2 columns, dates and values')
    file_csv = st.file_uploader('Select File')

    if file_csv:
        df = pd.read_csv(file_csv)
        dates = df['dates'].astype('datetime64[ns]')
        values = df['values'].astype('float')
    else:
        st.stop()

cmap = st.selectbox('Select Color Maps', cmaps, index=5)

st.write('Calendar Heatmap function')
heatmap_container = st.container(height=310)
with heatmap_container:
    height=270
    chart_heatmap = lesley.cal_heatmap(dates, values, height=height, cmap=cmap)
    st.altair_chart(chart_heatmap, use_container_width=True)

st.write('Individual Month Plot')
month_container = st.container(height=400)
with month_container:
    month = st.selectbox('Select month', calendar.month_name[1:])
    idx = list(calendar.month_name).index(month)
    month_plot = lesley.month_plot(dates, values, month=idx, height=250, cmap=cmap)
    st.altair_chart(month_plot, use_container_width=False)

st.write('Entire Year Plot')
year_container = st.container(height=850)
with year_container:
    nrows = st.selectbox('Insert Number of Rows', [1, 2, 3, 4, 6, 12], index=2)
    year_plot = lesley.calendar_plot(dates, values, nrows=nrows, cmap=cmap)
    st.altair_chart(year_plot)
