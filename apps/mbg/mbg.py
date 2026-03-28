import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(
    page_title='MBG Plot',
    page_icon='',
    layout='wide'
)

st.title('MBG Plot')

df = pd.read_csv('apps/mbg/mbg.csv')

st.data_editor(df, hide_index=True, num_rows='dynamic')
 
import base64
import re
from pathlib import Path
 
import altair as alt
import pandas as pd
 
 
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
 
def _svg_to_data_uri(svg_path: str | Path) -> str:
    """Read an SVG file and return a data-URI string usable in <img src=...>."""
    svg_text = Path(svg_path).read_text(encoding="utf-8")
 
    # Ensure the SVG has an explicit width/height so Altair scales it
    # (add them only if missing)
    if 'width=' not in svg_text:
        svg_text = svg_text.replace('<svg', '<svg width="100"', 1)
    if 'height=' not in svg_text:
        svg_text = svg_text.replace('<svg', '<svg height="100"', 1)
 
    encoded = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
 
 
def _expand_to_icon_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand the input dataframe so there is one row per icon to draw.
 
    Input columns : [category (str), value (int/float)]
    Output columns: [category, value, icon_index]
        where icon_index ∈ [0, value)
    """
    cat_col, val_col = df.columns[0], df.columns[1]
    rows = []
    for _, row in df.iterrows():
        n = int(round(row[val_col]))
        for i in range(n):
            rows.append({
                "category":   row[cat_col],
                "value":      n,
                "icon_index": i,   # column position (0-based)
            })
    return pd.DataFrame(rows)
 
 
# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------
 
def plot_pictograph(
    df: pd.DataFrame,
    svg_path: str | Path,
    *,
    icon_size: int = 40,
    icon_spacing: int = 6,
    title: str = "Pictograph Chart",
    color: str = "#4C78A8",
    background: str = "white",
    label_font_size: int = 13,
    value_label: bool = True,
) -> alt.Chart:
    """
    Build an isotype / pictograph Altair chart.
 
    Parameters
    ----------
    df : pd.DataFrame
        Two-column dataframe.  Column 0 = category (str),
        Column 1 = numeric value (non-negative integer).
    svg_path : str or Path
        Path to the SVG icon file.  The icon is repeated `value` times
        per category row.
    icon_size : int
        Rendered width *and* height of each icon in pixels.
    icon_spacing : int
        Extra horizontal gap (px) between icons beyond their natural width.
    title : str
        Chart title.
    color : str
        Tint colour applied to every icon via CSS filter trick where possible.
        (Altair mark_image does not support fill, so tinting is best-effort.)
    background : str
        Chart background colour.
    label_font_size : int
        Font size for category axis labels.
    value_label : bool
        Whether to show the numeric total at the end of each row.
 
    Returns
    -------
    alt.LayerChart
        An Altair chart object.  Call .show() or .save("out.html").
    """
    # --- validation ---------------------------------------------------------
    if df.shape[1] < 2:
        raise ValueError("df must have at least 2 columns.")
 
    cat_col, val_col = df.columns[0], df.columns[1]
 
    if not pd.api.types.is_numeric_dtype(df[val_col]):
        raise TypeError(f"Column '{val_col}' must be numeric.")
 
    if (df[val_col] < 0).any():
        raise ValueError("All values must be >= 0.")
 
    max_val = int(df[val_col].max())
    if max_val > 200:
        raise ValueError(
            f"Maximum value is {max_val}. Pictograph charts work best "
            "with values ≤ 200 to keep the chart readable."
        )
 
    # --- build data ---------------------------------------------------------
    data = _expand_to_icon_rows(df[[cat_col, val_col]])
    data_uri = _svg_to_data_uri(svg_path)
 
    step = icon_size + icon_spacing          # px per icon column
    row_height = icon_size + icon_spacing    # px per category row
 
    # Total chart width: enough to fit the widest row
    chart_width = max_val * step + 80        # 80px buffer for labels
    chart_height = df.shape[0] * row_height + 60
 
    # --- icon layer ---------------------------------------------------------
    icon_layer = (
        alt.Chart(data)
        .mark_image(
            width=icon_size,
            height=icon_size,
        )
        .encode(
            x=alt.X(
                "icon_index:Q",
                scale=alt.Scale(domain=[-0.5, max_val - 0.5]),
                axis=alt.Axis(
                    title=None,
                    labels=False,
                    ticks=False,
                    grid=False,
                    domain=False,
                ),
            ),
            y=alt.Y(
                "category:N",
                sort=alt.EncodingSortField(
                    field=val_col, op="max", order="descending"
                ),
                axis=alt.Axis(
                    title=None,
                    labelFontSize=label_font_size,
                    ticks=False,
                    domain=False,
                    grid=False,
                    labelPadding=8,
                ),
            ),
            url=alt.value(data_uri),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("value:Q",    title="Value"),
            ],
        )
    )
 
    # --- optional value-label layer ----------------------------------------
    if value_label:
        label_data = df[[cat_col, val_col]].copy()
        label_data.columns = ["category", "value"]
 
        label_layer = (
            alt.Chart(label_data)
            .mark_text(
                align="left",
                baseline="middle",
                dx=8,
                fontSize=label_font_size,
                fontWeight="bold",
                color="#555555",
            )
            .encode(
                x=alt.X(
                    "value:Q",
                    scale=alt.Scale(domain=[-0.5, max_val - 0.5]),
                    axis=None,
                ),
                y=alt.Y(
                    "category:N",
                    sort=alt.EncodingSortField(
                        field="value", op="max", order="descending"
                    ),
                ),
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


sample_df = pd.DataFrame({
    "Fruit":    ["Apples", "Bananas", "Cherries", "Dates", "Elderberry"],
    "Quantity": [7, 4, 10, 2, 6],
})

chart = plot_pictograph(
    # df=sample_df,
    df=df,
    # svg_path=tmp_svg,
    svg_path='apps/mbg/mbg.svg',
    icon_size=36,
    icon_spacing=4,
    title="Biaya dengan unit Hari MBG (1.2T/hari)",
    value_label=True,
)

st.altair_chart(chart)
