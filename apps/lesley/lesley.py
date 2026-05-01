import time
import calendar

import lesley
import numpy as np
import pandas as pd
import streamlit as st



st.title('Lesley')

use_random = st.radio('Data Input', ['Use Random Data', 'Upload CSV'], horizontal=True)
if use_random == 'Use Random Data':

    cols = st.columns(2)
    year = cols[0].number_input('Select Year', min_value=1666, max_value=2600, value=2024, step=1)

    dates = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31')
    values = np.random.randint(1, 10, size=len(dates))
else:
    st.write('Provide csv files with at least 2 columns, "date" and "value"')
    file_csv = st.file_uploader('Select File')

    if file_csv:
        df = pd.read_csv(file_csv)
        dates = df['date'].astype('datetime64[ns]')
        values = df['value'].astype('float')
        year = int(dates[0].year)
    else:
        st.stop()

cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'YlGn']
cmap = st.selectbox('Select Color Maps', cmaps, index=5)

st.write('Github-styled Heatmap function')
heatmap_container = st.container(height=310)
with heatmap_container:
    height=270
    chart_heatmap = lesley.cal_heatmap(dates, values, height=height, cmap=cmap)
    st.altair_chart(chart_heatmap, width='content')

st.write('Individual Month Plot')
month_container = st.container(height=400)
with month_container:
    cols = st.columns(2)
    month = cols[0].selectbox('Select month', calendar.month_name[1:])
    show_date = cols[0].checkbox('Show Date', value=True)
    idx = list(calendar.month_name).index(month)
    month_plot = lesley.month_plot(dates, values, month=idx, width=450, cmap=cmap, show_date=show_date)
    cols[1].altair_chart(month_plot, width='content')

st.write('Entire Year Plot')
year_container = st.container(height=850)
with year_container:
    nrows = st.selectbox('Select Layout', ['1x12', '2x6', '3x4', '4x3', '6x2', '12x1'], index=2)
    df = pd.DataFrame({
        'date': dates,
        'value': values,
    })
    year_plot = lesley.plot_calendar(year=year, label_df=df, layout=nrows, color=cmap)
    st.altair_chart(year_plot)
