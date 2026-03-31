import math
import base64
from pathlib import Path

import pandas as pd
import altair as alt
import streamlit as st


try:
    st.set_page_config(
        page_title='MBG Plot',
        page_icon='🍱',
        layout='wide'
)
except:
    print('Config has been set before. Big whoops')


st.title('MBG Plot')

uploaded_file = st.file_uploader('Upload CSV file', type='csv')
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv('apps/mbg/mbg.csv')

# df = pd.read_csv('apps/mbg/mbg.csv')

st.data_editor(df, hide_index=True, num_rows='dynamic')
 
 
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
 
def _svg_to_data_uri(svg_path: str | Path) -> str:
    """Read an SVG file and return a base64 data-URI usable as an image src."""
    svg_text = Path(svg_path).read_text(encoding="utf-8")
    if 'width=' not in svg_text:
        svg_text = svg_text.replace('<svg', '<svg width="100"', 1)
    if 'height=' not in svg_text:
        svg_text = svg_text.replace('<svg', '<svg height="100"', 1)
    encoded = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
 
 
def _expand_to_icon_rows(
    df: pd.DataFrame,
    max_per_row: int,
) -> pd.DataFrame:
    """
    Expand the dataframe so each icon gets its own row, with wrapping.
 
    Output columns
    --------------
    category   : original category label
    value      : original numeric value
    col        : x position within a wrapped row  (0 .. max_per_row-1)
    y_key      : composite string used as Altair's Y ordinal field,
                 e.g. "Apples||0", "Apples||1" for wrap rows 0 and 1
    y_sort_key : integer used to keep wrap-rows in the correct order
    """
    cat_col, val_col = df.columns[0], df.columns[1]
    rows = []
    sort_counter = 0
 
    for _, row in df.iterrows():
        n = int(round(row[val_col]))
        n_wrap_rows = max(1, math.ceil(n / max_per_row))
 
        for i in range(n):
            wrap_row = i // max_per_row
            col_pos  = i %  max_per_row
            rows.append({
                "category":   str(row[cat_col]),
                "value":      n,
                "col":        col_pos,
                "wrap_row":   wrap_row,
                "y_key":      f"{row[cat_col]}||{wrap_row}",
                "y_sort_key": sort_counter + wrap_row,
            })
 
        sort_counter += n_wrap_rows
 
    return pd.DataFrame(rows)
 
 
def _build_y_sort_order(expanded: pd.DataFrame) -> list[str]:
    """Return y_key values sorted by y_sort_key (ascending = top-to-bottom)."""
    order_df = (
        expanded[["y_key", "y_sort_key"]]
        .drop_duplicates()
        .sort_values("y_sort_key")
    )
    return order_df["y_key"].tolist()
 
 
# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------
 
def plot_pictograph(
    df: pd.DataFrame,
    svg_path: str | Path,
    *,
    icon_size: int = 36,
    icon_spacing: int = 2,
    max_per_row: int = 20,
    title: str = "Pictograph Chart",
    background: str = "transparent",
    label_font_size: int = 13,
    value_label: bool = False,
) -> alt.Chart:
    """
    Build an isotype / pictograph Altair chart with row-wrapping support.
 
    Parameters
    ----------
    df : pd.DataFrame
        Two-column dataframe. Column 0 = category (str),
        column 1 = numeric value (non-negative number).
    svg_path : str or Path
        Path to the SVG icon file.
    icon_size : int
        Rendered width & height of each icon in pixels (default 36).
    icon_spacing : int
        Extra horizontal gap in px between icons (default 2).
    max_per_row : int
        Maximum icons per line before wrapping to a new sub-row (default 20).
        Set higher to allow longer rows, lower to force earlier wrapping.
    title : str
        Chart title.
    background : str
        Chart background colour.
    label_font_size : int
        Font size for category axis labels.
    value_label : bool
        Show the numeric total to the right of the last icon (default False).
 
    Returns
    -------
    alt.Chart
        Altair chart. Call .show() or .save("out.html").
    """
    # --- validation ---------------------------------------------------------
    if df.shape[1] < 2:
        raise ValueError("df must have at least 2 columns.")
 
    cat_col, val_col = df.columns[0], df.columns[1]
 
    if not pd.api.types.is_numeric_dtype(df[val_col]):
        raise TypeError(f"Column '{val_col}' must be numeric.")
    if (df[val_col] < 0).any():
        raise ValueError("All values must be >= 0.")
 
    # --- expand data --------------------------------------------------------
    data = _expand_to_icon_rows(df[[cat_col, val_col]], max_per_row)
    data_uri = _svg_to_data_uri(svg_path)
 
    y_order = _build_y_sort_order(data)
 
    step       = icon_size + icon_spacing
    row_height = icon_size + max(icon_spacing, 4)
 
    # Total wrap-rows across all categories
    total_wrap_rows = data[["category", "wrap_row"]].drop_duplicates().shape[0]
 
    chart_width  = max_per_row * step + 60
    chart_height = total_wrap_rows * row_height + 40
 
    # --- icon layer ---------------------------------------------------------
    icon_layer = (
        alt.Chart(data)
        .mark_image(width=icon_size, height=icon_size)
        .encode(
            x=alt.X(
                "col:Q",
                scale=alt.Scale(domain=[-0.5, max_per_row - 0.5]),
                axis=alt.Axis(
                    title=None, labels=False, ticks=False,
                    grid=False, domain=False,
                ),
            ),
            y=alt.Y(
                "y_key:N",
                sort=y_order,
                axis=alt.Axis(
                    title=None,
                    labelFontSize=label_font_size,
                    ticks=False,
                    domain=False,
                    grid=False,
                    labelPadding=8,
                    # Show label only for the first wrap-row of each category
                    labelExpr=(
                        "indexof(datum.value, '||') >= 0 ? "
                        "(split(datum.value, '||')[1] == '0' ? "
                        "split(datum.value, '||')[0] : '') "
                        ": datum.value"
                    ),
                ),
            ),
            url=alt.value(data_uri),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("value:Q",    title="Value"),
            ],
        )
    )
 
    # --- optional value label -----------------------------------------------
    if value_label:
        # Place the label at the end of the last wrap-row for each category
        label_data = (
            data.sort_values(["category", "wrap_row", "col"])
            .groupby("category", as_index=False)
            .last()
            [["category", "value", "col", "y_key"]]
            .copy()
        )
        label_data["col"] = label_data["col"] + 1  # one step right of last icon
 
        label_layer = (
            alt.Chart(label_data)
            .mark_text(
                align="left", baseline="middle",
                dx=4, fontSize=label_font_size,
                fontWeight="bold", color="#555555",
            )
            .encode(
                x=alt.X(
                    "col:Q",
                    scale=alt.Scale(domain=[-0.5, max_per_row - 0.5]),
                    axis=None,
                ),
                y=alt.Y("y_key:N", sort=y_order),
                text=alt.Text("value:Q"),
            )
        )
        chart = alt.layer(icon_layer, label_layer)
    else:
        chart = icon_layer
 
    return (
        chart
        .properties(
            title=alt.TitleParams(
                text=title,
                fontSize=16,
                fontWeight="bold",
                anchor="start",
                offset=10,
            ),
            width=chart_width,
            height=chart_height,
            background=background,
            padding={"left": 10, "right": 30, "top": 10, "bottom": 10},
        )
        .configure_view(stroke=None)
    )


temp_df = df[[df.columns[0]]]
temp_df['value'] = (df[df.columns[1]] / 1.2).astype(int).to_list()

chart = plot_pictograph(
    df=temp_df,
    svg_path='apps/mbg/mbg.svg',
    icon_size=36,
    icon_spacing=4,
    title="Biaya dengan unit Hari MBG (1.2T/hari)",
    value_label=False,
)

st.altair_chart(chart)
