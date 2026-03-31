import streamlit as st
import pandas as pd
import random
from st_vortree import st_vortree

st.title("Voronoi Treemap")

# Generate some mock data
def get_mock_data():
    categories = ["Tech", "Finance", "Healthcare", "Energy"]
    companies = {
        "Tech": ["Apple", "Microsoft", "Google", "Amazon", "Meta"],
        "Finance": ["JPMorgan", "Visa", "Mastercard", "Bank of America"],
        "Healthcare": ["J&J", "UnitedHealth", "Pfizer", "AbbVie"],
        "Energy": ["ExxonMobil", "Chevron", "NextEra", "ConocoPhillips"]
    }
    
    data = []
    for cat in categories:
        for comp in companies[cat]:
            data.append({
                "Company": comp,
                "MarketCap": random.randint(50, 1000),
                "Sector": cat
            })
    return pd.DataFrame(data)

st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        df = get_mock_data()
else:
    df = get_mock_data()

st.sidebar.header("Configuration")

if uploaded_file is not None:
    columns = df.columns.tolist()
    name_col = st.sidebar.selectbox("Name Column", columns, index=0 if len(columns) > 0 else None)
    value_col = st.sidebar.selectbox("Value Column", columns, index=1 if len(columns) > 1 else None)
    
    group_options = ["None"] + columns
    group_col_selection = st.sidebar.selectbox("Group Column", group_options, index=0)
    group_col = group_col_selection if group_col_selection != "None" else None
else:
    name_col = "Company"
    value_col = "MarketCap"
    group_col = "Sector"

color_scheme = st.sidebar.selectbox(
    "Color Scheme", 
    ["tableau10", "category10", "pastel1", "dark", "cool", "warm"]
)
show_values = st.sidebar.checkbox("Show Values", value=True)
show_pct_only = st.sidebar.checkbox("Show Percentages Only", value=False)
label_scale = st.sidebar.slider("Label Scale", 0.5, 2.0, 1.0)
border_color = st.sidebar.color_picker("Border Color", "#ffffff")
border_width = st.sidebar.slider("Border Width", 0, 5, 2)
show_legend = st.sidebar.checkbox("Show Legend", value=True)
height = st.sidebar.slider("Treemap Height", 200, 1000, 400)

if uploaded_file is not None:
    st.write("### Data Preview")
    st.dataframe(df.head())

st.write("### Grouped Treemap")
if group_col:
    st_vortree(
        df,
        name_col=name_col,
        value_col=value_col,
        group_col=group_col,
        color_scheme=color_scheme,
        show_values=show_values,
        show_pct_only=show_pct_only,
        label_scale=label_scale,
        border_color=border_color,
        border_width=border_width,
        show_legend=show_legend,
        height=height,
        key="grouped_treemap"
    )
else:
    st.info("No group column selected. Grouped Treemap is disabled.")

st.write("### Ungrouped Treemap")
st_vortree(
    df,
    name_col=name_col,
    value_col=value_col,
    color_scheme=color_scheme,
    show_values=show_values,
    show_pct_only=show_pct_only,
    label_scale=label_scale,
    border_color=border_color,
    border_width=border_width,
    show_legend=show_legend,
    height=height,
    key="ungrouped_treemap"
)
