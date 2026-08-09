import csv
import pandas as pd
import altair as alt
import streamlit as st

def detect_delimiter(file_obj):
    chunk = file_obj.read(8192)
    file_obj.seek(0)
    try:
        dialect = csv.Sniffer().sniff(chunk.decode('utf-8'), delimiters=';,|\t')
        return dialect.delimiter
    except csv.Error:
        return ','

# --------------------------------------------------------------------------- #
# Theme: editorial / data-journalism aesthetic
# --------------------------------------------------------------------------- #
PALETTE = {
    'prior': '#C9A66B',
    'current': '#1F3A5F',
    'positive': '#2E7D6B',
    'negative': '#B5483C',
    'neutral': '#5A6B7B',
    'ink': '#16202A',
    'muted': '#6B7785',
    'grid': '#E6E2D9',
}

@alt.theme.register('editorial', enable=True)
def editorial_theme():
    return alt.theme.ThemeConfig({
        'config': {
            'background': 'transparent',
            'view': {'stroke': None},
            'font': 'Helvetica Neue, Arial, sans-serif',
            'title': {
                'fontSize': 15,
                'fontWeight': 700,
                'color': PALETTE['ink'],
                'anchor': 'start',
                'offset': 8,
                'subtitleFontSize': 12,
                'subtitleColor': PALETTE['muted'],
                'subtitleFontWeight': 400,
            },
            'axis': {
                'labelFontSize': 12,
                'labelColor': PALETTE['ink'],
                'titleColor': PALETTE['muted'],
                'titleFontSize': 11,
                'titleFontWeight': 500,
                'gridColor': PALETTE['grid'],
                'gridWidth': 1,
                'domainColor': PALETTE['grid'],
                'tickColor': PALETTE['grid'],
                'labelPadding': 6,
            },
            'legend': {
                'labelFontSize': 12,
                'labelColor': PALETTE['ink'],
                'titleColor': PALETTE['muted'],
                'offset': 8,
                'symbolType': 'square',
                'symbolSize': 120,
            },
            'bar': {'cornerRadiusEnd': 3},
        }
    })

st.set_page_config(page_title='CSV Explorer', layout='wide')

st.markdown(
    """
    <style>
        .block-container { padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1180px; }
        h1, h2, h3 { letter-spacing: -0.01em; }
        .eyebrow {
            font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase;
            color: #6B7785; font-weight: 600; margin-bottom: 0.25rem;
        }
        .lede { color: #5A6B7B; font-size: 1.05rem; line-height: 1.6; margin-bottom: 1.75rem; }
        .kpi-label { font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
            color: #6B7785; font-weight: 600; }
        .kpi-value { font-size: 2.1rem; font-weight: 700; letter-spacing: -0.02em; color: #16202A;
            line-height: 1.1; margin-top: 0.2rem; }
        .kpi-delta { font-size: 0.85rem; font-weight: 600; margin-top: 0.15rem; color: #5A6B7B; }
        .up   { color: #2E7D6B; }
        .down { color: #B5483C; }
        .rule { height: 1px; background: #E6E2D9; margin: 2.25rem 0; border: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">CSV Explorer</div>', unsafe_allow_html=True)
st.title('Explore any CSV')
st.markdown(
    '<p class="lede">Upload a CSV to explore its shape and structure. '
    'Demo data loads from <code>sample.csv</code>.</p>',
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Load data
# --------------------------------------------------------------------------- #
uploaded_file = st.file_uploader('Upload a CSV file', type='csv')
if uploaded_file is not None:
    delim = detect_delimiter(uploaded_file)
    df = pd.read_csv(uploaded_file, sep=delim)
else:
    with open('apps/csv_explorer/sample.csv', 'rb') as f:
        delim = detect_delimiter(f)
    df = pd.read_csv('apps/csv_explorer/sample.csv', sep=delim)

with st.expander('Data Preview', expanded=False):
    st.dataframe(df, width='stretch')

# --------------------------------------------------------------------------- #
# Column-type detection (no domain assumptions)
# --------------------------------------------------------------------------- #
num_cols = df.select_dtypes(include='number').columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()

# Detect paired-period numeric columns sharing a stem with a trailing 4-digit
# value, plus an optional "Net Change" and "Growth (%)" column. If found, render
# the tailored comparison dashboard using only the actual column names.
import re
YEAR_RE = re.compile(r'\s*(\d{4})\s*$')
stem_groups = {}
for col in num_cols:
    m = YEAR_RE.search(col)
    if m:
        stem = YEAR_RE.sub('', col).strip() or col
        stem_groups.setdefault(stem, []).append((m.group(1), col))
paired_periods = []
for stem, members in stem_groups.items():
    if len(members) >= 2:
        members.sort()
        paired_periods.append((stem, [c for _, c in members[:2]]))

NET_CANDIDATES = [c for c in num_cols if 'net' in c.lower() and 'change' in c.lower()]
GROWTH_CANDIDATES = [c for c in num_cols if 'growth' in c.lower()]
NET_COL = NET_CANDIDATES[0] if NET_CANDIDATES else None
GROWTH_COL = GROWTH_CANDIDATES[0] if GROWTH_CANDIDATES else None


def fmt(n):
    return f'{n:,.0f}'


if paired_periods:
    stem, PERIOD_COLS = paired_periods[0]
    col_a, col_b = PERIOD_COLS

    # Pick a label column, selectable by the user. Default to a column literally
    # containing "english"/"name", else the last categorical column.
    default_idx = len(cat_cols) - 1 if cat_cols else 0
    for i, c in enumerate(cat_cols):
        if 'english' in c.lower() or 'name' in c.lower():
            default_idx = i
            break

    label_options = cat_cols if cat_cols else ['—']
    LABEL_COL = st.selectbox(
        'Category column', label_options, index=default_idx, key='comp_label',
    )

    if cat_cols and LABEL_COL != '—':
        # ---- Headline KPIs (use the aggregate row if present, else totals) --- #
        agg_mask = df[cat_cols].apply(
            lambda s: s.astype(str).str.lower().isin(['total', 'jumlah', 'sum'])
        ).any(axis=1)
        if agg_mask.any():
            total_row = df.loc[agg_mask].iloc[0]
            v_a = float(total_row[col_a])
            v_b = float(total_row[col_b])
            net = float(total_row[NET_COL]) if NET_COL else v_b - v_a
            growth = float(total_row[GROWTH_COL]) if GROWTH_COL else (
                (v_b - v_a) / v_a * 100 if v_a else 0.0
            )
        else:
            v_a = float(df[col_a].sum())
            v_b = float(df[col_b].sum())
            net = v_b - v_a
            growth = (net / v_a * 100) if v_a else 0.0

        net_sign = '+' if net >= 0 else '−'
        growth_sign = '+' if growth >= 0 else '−'

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(
            f'<div class="kpi-label">{col_a}</div>'
            f'<div class="kpi-value">{fmt(v_a)}</div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="kpi-label">{col_b}</div>'
            f'<div class="kpi-value">{fmt(v_b)}</div>',
            unsafe_allow_html=True,
        )
        if NET_COL:
            c3.markdown(
                f'<div class="kpi-label">{NET_COL}</div>'
                f'<div class="kpi-value">{net_sign}{fmt(abs(net))}</div>'
                f'<div class="kpi-delta {"down" if net < 0 else "up"}">'
                f'{"−" if net < 0 else "+"}</div>',
                unsafe_allow_html=True,
            )
        if GROWTH_COL:
            c4.markdown(
                f'<div class="kpi-label">{GROWTH_COL}</div>'
                f'<div class="kpi-value">{growth_sign}{abs(growth):.2f}%</div>'
                f'<div class="kpi-delta {"down" if growth < 0 else "up"}">'
                f'{"−" if growth < 0 else "+"}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="rule" />', unsafe_allow_html=True)

        # Per-category table: drop aggregate rows, then group by the chosen
        # label column and sum duplicate categories into a single row each.
        rows_df = df.loc[~agg_mask].copy()
        rows_df = rows_df.groupby(LABEL_COL, as_index=False)[PERIOD_COLS].sum()
        if NET_COL:
            rows_df[NET_COL] = rows_df[col_b] - rows_df[col_a]
        if GROWTH_COL:
            rows_df[GROWTH_COL] = rows_df.apply(
                lambda r: (r[col_b] - r[col_a]) / r[col_a] * 100
                if r[col_a] else 0.0,
                axis=1,
            )

        # ---- Pie chart: only when few categories ------------------------- #
        n_categories = rows_df[LABEL_COL].nunique() if not rows_df.empty else 0
        if 1 < n_categories < 3:
            pie_cols = st.columns(len(PERIOD_COLS))
            for i, pcol in enumerate(PERIOD_COLS):
                pie_df = rows_df[[LABEL_COL, pcol]].copy()
                pie_chart = (
                    alt.Chart(pie_df)
                    .mark_arc(innerRadius=60, stroke='white', strokeWidth=2)
                    .encode(
                        theta=alt.Theta(f'{pcol}:Q', title=None),
                        color=alt.Color(
                            f'{LABEL_COL}:N',
                            legend=alt.Legend(title=LABEL_COL, orient='right',
                                             labelLimit=160),
                            scale=alt.Scale(scheme='category10'),
                        ),
                        tooltip=[
                            alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                            alt.Tooltip(f'{pcol}:Q', format=',', title=pcol),
                        ],
                    )
                    .properties(
                        height=300,
                        title=alt.Title(f'{pcol}', anchor='middle'),
                    )
                )
                pie_cols[i].altair_chart(pie_chart, width='stretch')
            st.markdown('<hr class="rule" />', unsafe_allow_html=True)

        # ---- 1. Slope / dumbbell chart per label ------------------------ #
        slope_df = rows_df.melt(
            id_vars=[LABEL_COL], value_vars=PERIOD_COLS,
            var_name='Column', value_name='Value',
        )
        slope_order = rows_df.sort_values(col_b, ascending=True)[LABEL_COL].tolist()

        slope = alt.Chart(slope_df).mark_line(opacity=0.55).encode(
            x=alt.X('Column:N', sort=PERIOD_COLS, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Value:Q', scale=alt.Scale(zero=False), title=None),
            color=alt.Color(
                f'{LABEL_COL}:N',
                legend=alt.Legend(title=LABEL_COL, orient='right', labelLimit=140),
                scale=alt.Scale(scheme='category10'),
                sort=slope_order,
            ),
            detail=f'{LABEL_COL}:N',
        )
        dots = alt.Chart(slope_df).mark_circle(size=90, opacity=0.95).encode(
            x=alt.X('Column:N', sort=PERIOD_COLS),
            y=alt.Y('Value:Q', scale=alt.Scale(zero=False)),
            color=alt.Color(f'{LABEL_COL}:N', legend=None, sort=slope_order),
            tooltip=[
                alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                alt.Tooltip('Column:N'),
                alt.Tooltip('Value:Q', format=','),
            ],
        )
        slope_chart = (slope + dots).properties(
            height=420,
            title=alt.Title(
                f'{col_a} → {col_b} by {LABEL_COL}',
                subtitle='Steeper lines mark larger moves.',
            ),
        ).resolve_scale(color='independent')

        st.altair_chart(slope_chart, width='stretch')

        st.markdown('<hr class="rule" />', unsafe_allow_html=True)

        left, right = st.columns([1, 1])

        # ---- 2. Diverging lollipop: net change -------------------------- #
        if NET_COL:
            net_df = rows_df[[LABEL_COL, NET_COL]].sort_values(NET_COL)
            net_df['Direction'] = net_df[NET_COL].map(
                lambda x: 'Positive' if x >= 0 else 'Negative'
            )

            loll_base = alt.Chart(net_df).encode(
                y=alt.Y(f'{LABEL_COL}:N', sort=None, title=None,
                        axis=alt.Axis(labelLimit=160)),
            )
            loll_stem = loll_base.mark_rule(strokeWidth=2).encode(
                x=alt.X(f'{NET_COL}:Q', title=NET_COL, scale=alt.Scale(zero=True)),
                color=alt.Color('Direction:N',
                                scale=alt.Scale(domain=['Negative', 'Positive'],
                                               range=[PALETTE['negative'], PALETTE['positive']]),
                                legend=None),
            )
            loll_dot = loll_base.mark_circle(size=180, opacity=0.95).encode(
                x=alt.X(f'{NET_COL}:Q', scale=alt.Scale(zero=True)),
                color=alt.Color('Direction:N',
                                scale=alt.Scale(domain=['Negative', 'Positive'],
                                               range=[PALETTE['negative'], PALETTE['positive']]),
                                legend=None),
                tooltip=[
                    alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                    alt.Tooltip(f'{NET_COL}:Q', format='+,', title=NET_COL),
                ],
            )
            net_chart = (loll_stem + loll_dot).properties(
                height=320,
                title=alt.Title(
                    f'{NET_COL} by {LABEL_COL}',
                    subtitle='Positive in teal, negative in clay.',
                ),
            )
            left.altair_chart(net_chart, width='stretch')

        # ---- 3. Diverging bar: growth (%) ------------------------------- #
        if GROWTH_COL:
            growth_df = rows_df[[LABEL_COL, GROWTH_COL]].sort_values(GROWTH_COL)
            growth_df['Direction'] = growth_df[GROWTH_COL].map(
                lambda x: 'Positive' if x >= 0 else 'Negative'
            )

            growth_chart = alt.Chart(growth_df).mark_bar().encode(
                x=alt.X(f'{GROWTH_COL}:Q', title=GROWTH_COL, scale=alt.Scale(zero=True)),
                y=alt.Y(f'{LABEL_COL}:N', sort=None, title=None,
                        axis=alt.Axis(labelLimit=160)),
                color=alt.Color('Direction:N',
                                scale=alt.Scale(domain=['Negative', 'Positive'],
                                               range=[PALETTE['negative'], PALETTE['positive']]),
                                legend=None),
                tooltip=[
                    alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                    alt.Tooltip(f'{GROWTH_COL}:Q', format='+.2f', title=GROWTH_COL),
                ],
            ).properties(
                height=320,
                title=alt.Title(
                    f'{GROWTH_COL} by {LABEL_COL}',
                    subtitle='Positive in teal, negative in clay.',
                ),
            )
            right.altair_chart(growth_chart, width='stretch')

        st.markdown('<hr class="rule" />', unsafe_allow_html=True)

        # ---- 4. Grouped bar: side-by-side volumes per label ------------- #
        grouped_df = rows_df.melt(
            id_vars=[LABEL_COL], value_vars=PERIOD_COLS,
            var_name='Column', value_name='Value',
        )
        grouped_chart = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X(f'{LABEL_COL}:N', title=None,
                    axis=alt.Axis(labelAngle=-25, labelLimit=160)),
            y=alt.Y('Value:Q', title='Value', scale=alt.Scale(zero=True)),
            xOffset='Column:N',
            color=alt.Color('Column:N',
                            scale=alt.Scale(domain=PERIOD_COLS,
                                           range=[PALETTE['prior'], PALETTE['current']]),
                            legend=alt.Legend(title=None, orient='top')),
            tooltip=[
                alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                alt.Tooltip('Column:N'),
                alt.Tooltip('Value:Q', format=','),
            ],
        ).properties(
            height=280,
            title=alt.Title(
                f'{col_a} and {col_b} by {LABEL_COL}',
                subtitle=f'Sand bars are {col_a}; indigo bars are {col_b}.',
            ),
        )

        st.altair_chart(grouped_chart, width='stretch')

        st.stop()

# --------------------------------------------------------------------------- #
# Generic exploration fallback
# --------------------------------------------------------------------------- #
date_cols = []
for col in df.columns:
    if col in num_cols or col in cat_cols:
        continue
    try:
        pd.to_datetime(df[col], errors='raise')
        date_cols.append(col)
    except (ValueError, TypeError):
        pass

st.header('Summary Statistics')
st.dataframe(df.describe(include='all').T, width='stretch')

if num_cols:
    st.header('Numeric Distributions')
    dist_chart_type = st.radio('Chart type', ['Histogram', 'Box Plot'], horizontal=True)

    if dist_chart_type == 'Histogram':
        for col in num_cols:
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    alt.X(f'{col}:Q', bin=True, title=col),
                    y='count()',
                    tooltip=['count()'],
                    color=alt.value(PALETTE['current']),
                )
                .properties(height=300, title=f'Distribution of {col}')
            )
            st.altair_chart(chart, width='stretch')
    else:
        df_melted = df[num_cols].melt(var_name='column', value_name='value')
        chart = (
            alt.Chart(df_melted)
            .mark_boxplot()
            .encode(
                x=alt.X('column:N', title=''),
                y=alt.Y('value:Q', title='Value'),
                color=alt.Color('column:N', legend=None, scale=alt.Scale(scheme='tableau10')),
            )
            .properties(height=400, title='Box Plots')
        )
        st.altair_chart(chart, width='stretch')

if cat_cols:
    st.header('Categorical Overview')
    top_n = st.slider('Top N categories', 5, 30, 10)
    for col in cat_cols:
        counts = df[col].value_counts().head(top_n).reset_index()
        counts.columns = [col, 'count']
        if counts.empty:
            continue
        chart = (
            alt.Chart(counts)
            .mark_bar()
            .encode(
                x=alt.X('count:Q', title='count'),
                y=alt.Y(f'{col}:N', sort='-x', title=None,
                        axis=alt.Axis(labelLimit=200)),
                tooltip=[alt.Tooltip(f'{col}:N'), alt.Tooltip('count:Q', format=',')],
                color=alt.value(PALETTE['current']),
            )
            .properties(
                height=max(180, 30 + 28 * len(counts)),
                title=f'Top {len(counts)} of {col}',
            )
        )
        st.altair_chart(chart, width='stretch')

if len(num_cols) >= 2:
    st.header('Scatter Plot')
    x_sel = st.selectbox('X axis', num_cols, index=0, key='scatter_x')
    y_sel = st.selectbox('Y axis', num_cols, index=min(1, len(num_cols) - 1), key='scatter_y')
    color_sel = st.selectbox('Color by', ['None'] + cat_cols + num_cols, key='scatter_color')

    enc = dict(
        x=alt.X(f'{x_sel}:Q'),
        y=alt.Y(f'{y_sel}:Q'),
        tooltip=[f'{x_sel}:Q', f'{y_sel}:Q'] + [f'{c}:N' for c in cat_cols[:3]],
    )
    if color_sel != 'None':
        if color_sel in num_cols:
            enc['color'] = alt.Color(f'{color_sel}:Q', scale=alt.Scale(scheme='viridis'))
        else:
            enc['color'] = alt.Color(f'{color_sel}:N', scale=alt.Scale(scheme='tableau10'))
    chart = (
        alt.Chart(df)
        .mark_circle(size=60, opacity=0.6)
        .encode(**enc)
        .properties(height=500, title=f'{y_sel} vs {x_sel}')
    )
    st.altair_chart(chart, width='stretch')

if len(num_cols) >= 2:
    st.header('Correlation Heatmap')
    corr = df[num_cols].corr()
    corr_melted = corr.reset_index().melt(id_vars='index')
    corr_melted.columns = ['var1', 'var2', 'correlation']

    heatmap = (
        alt.Chart(corr_melted)
        .mark_rect()
        .encode(
            x=alt.X('var1:N', title='', sort=None),
            y=alt.Y('var2:N', title='', sort=None),
            color=alt.Color('correlation:Q', scale=alt.Scale(scheme='redblue', domain=[-1, 1])),
            tooltip=['var1:N', 'var2:N', alt.Tooltip('correlation:Q', format='.2f')],
        )
        .properties(height=max(280, 30 * len(num_cols)), title='Correlation Matrix')
    )
    labels = (
        alt.Chart(corr_melted)
        .mark_text(baseline='middle', fontSize=11)
        .encode(
            x=alt.X('var1:N', sort=None),
            y=alt.Y('var2:N', sort=None),
            text=alt.Text('correlation:Q', format='.2f'),
            color=alt.condition(
                alt.datum.correlation > 0.5, alt.value('white'), alt.value('black')
            ),
        )
    )
    st.altair_chart(heatmap + labels, width='stretch')

if date_cols and num_cols:
    st.header('Time Series')
    ts_date = st.selectbox('Date column', date_cols, key='ts_date')
    ts_val = st.selectbox('Value column', num_cols, key='ts_val')

    df_ts = df[[ts_date, ts_val]].dropna().copy()
    df_ts[ts_date] = pd.to_datetime(df_ts[ts_date])
    df_ts = df_ts.sort_values(ts_date)

    chart = (
        alt.Chart(df_ts)
        .mark_line(point=True, color=PALETTE['current'])
        .encode(
            x=alt.X(f'{ts_date}:T', title=ts_date),
            y=alt.Y(f'{ts_val}:Q', title=ts_val),
            tooltip=[f'{ts_date}:T', f'{ts_val}:Q'],
        )
        .properties(height=400, title=f'{ts_val} over Time')
    )
    st.altair_chart(chart, width='stretch')
