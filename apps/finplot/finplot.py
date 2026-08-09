import re
from pathlib import Path

import pandas as pd
import altair as alt
import streamlit as st

# --------------------------------------------------------------------------- #
# Theme: financial / editorial aesthetic
# --------------------------------------------------------------------------- #

st.set_page_config(page_title='FinPlot', layout='wide')

THEMES = {
    'Classic Editorial': {
        'palette': {
            'revenue': '#1B3A5C',
            'revenue_light': '#A8C4DA',
            'cost': '#B5483C',
            'profit': '#2E7D6B',
            'expense': '#C9A66B',
            'net': '#5B4A9E',
            'positive': '#2E7D6B',
            'negative': '#B5483C',
            'neutral': '#5A6B7B',
            'ink': '#16202A',
            'muted': '#6B7785',
            'grid': '#E6E2D9',
            'accent': '#D4763C',
            'bg_card': '#F7F5F0',
        },
        'fin_colors': [
            '#1B3A5C', '#2E7D6B', '#C9A66B', '#B5483C', '#5B4A9E',
            '#D4763C', '#3A7CA5', '#8B6DB0', '#5A8F5A', '#C76B8E',
        ],
    },
    'Modern Corporate': {
        'palette': {
            'revenue': '#2563EB',
            'revenue_light': '#93C5FD',
            'cost': '#DC2626',
            'profit': '#059669',
            'expense': '#F59E0B',
            'net': '#4F46E5',
            'positive': '#059669',
            'negative': '#DC2626',
            'neutral': '#64748B',
            'ink': '#1E293B',
            'muted': '#64748B',
            'grid': '#E2E8F0',
            'accent': '#7C3AED',
            'bg_card': '#F8FAFC',
        },
        'fin_colors': [
            '#2563EB', '#059669', '#F59E0B', '#DC2626', '#4F46E5',
            '#7C3AED', '#0891B2', '#DB2777', '#16A34A', '#38BDF8',
        ],
    },
    'Forest / ESG': {
        'palette': {
            'revenue': '#1F4E3D',
            'revenue_light': '#86EFAC',
            'cost': '#9A3412',
            'profit': '#4ADE80',
            'expense': '#D97706',
            'net': '#78716C',
            'positive': '#4ADE80',
            'negative': '#9A3412',
            'neutral': '#78716C',
            'ink': '#292524',
            'muted': '#78716C',
            'grid': '#E7E5E4',
            'accent': '#65A30D',
            'bg_card': '#F5F5F4',
        },
        'fin_colors': [
            '#1F4E3D', '#4ADE80', '#D97706', '#9A3412', '#65A30D',
            '#16A34A', '#0D9488', '#A8A29E', '#CA8A04', '#3F6212',
        ],
    },
    'Ocean Breeze': {
        'palette': {
            'revenue': '#0C4A6E',
            'revenue_light': '#7DD3FC',
            'cost': '#C2410C',
            'profit': '#0D9488',
            'expense': '#FBBF24',
            'net': '#475569',
            'positive': '#0D9488',
            'negative': '#C2410C',
            'neutral': '#64748B',
            'ink': '#0F172A',
            'muted': '#64748B',
            'grid': '#E2E8F0',
            'accent': '#0891B2',
            'bg_card': '#F0F9FF',
        },
        'fin_colors': [
            '#0C4A6E', '#0D9488', '#FBBF24', '#C2410C', '#0891B2',
            '#0284C7', '#38BDF8', '#FB923C', '#14B8A6', '#6366F1',
        ],
    },
    'Crimson Statement': {
        'palette': {
            'revenue': '#9F1239',
            'revenue_light': '#FDA4AF',
            'cost': '#7C2D12',
            'profit': '#065F46',
            'expense': '#B45309',
            'net': '#475569',
            'positive': '#065F46',
            'negative': '#BE123C',
            'neutral': '#78716C',
            'ink': '#1C1917',
            'muted': '#78716C',
            'grid': '#E7E5E4',
            'accent': '#BE123C',
            'bg_card': '#FFF1F2',
        },
        'fin_colors': [
            '#9F1239', '#BE123C', '#FB7185', '#B45309', '#065F46',
            '#475569', '#7C2D12', '#881337', '#78716C', '#92400E',
        ],
    },
}


with st.sidebar:
    st.markdown('### Theme')
    _theme_name = st.selectbox(
        'Color scheme',
        list(THEMES.keys()),
        key='fin_theme',
        help='Choose a polished color scheme for the dashboard.',
    )

PALETTE = THEMES[_theme_name]['palette']
FIN_COLORS = THEMES[_theme_name]['fin_colors']

@alt.theme.register('financial', enable=True)
def financial_theme():
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

_CSS_TEMPLATE = """
<style>
    .block-container { padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1180px; }
    h1, h2, h3 { letter-spacing: -0.01em; }
    .eyebrow {
        font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase;
        color: __muted__; font-weight: 600; margin-bottom: 0.25rem;
    }
    .lede { color: __neutral__; font-size: 1.05rem; line-height: 1.6; margin-bottom: 1.75rem; }
    .kpi-card {
        background: __bg_card__; border-radius: 10px; padding: 1.2rem 1.4rem;
        border: 1px solid __grid__;
    }
    .kpi-label { font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
        color: __muted__; font-weight: 600; }
    .kpi-value { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.02em; color: __ink__;
        line-height: 1.1; margin-top: 0.2rem; }
    .kpi-sub { font-size: 0.82rem; font-weight: 600; margin-top: 0.15rem; }
    .up   { color: __positive__; }
    .down { color: __negative__; }
    .flat { color: __neutral__; }
    .rule { height: 1px; background: __grid__; margin: 2.25rem 0; border: none; }
    .section-label {
        font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
        color: __muted__; font-weight: 600; margin-bottom: 0.5rem; margin-top: 0.5rem;
    }
</style>
"""
_css = _CSS_TEMPLATE
for _key, _value in PALETTE.items():
    _css = _css.replace(f'__{_key}__', _value)
st.markdown(_css, unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Financial Plot</div>', unsafe_allow_html=True)
st.title('Financial Dashboard')
st.markdown(
    '<p class="lede">Upload a financial CSV to generate an interactive dashboard. '
    'Automatically detects categorical, absolute, and percentage columns. '
    'Demo data loads from <code>sample.csv</code>.</p>',
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Load data
# --------------------------------------------------------------------------- #
def _parse_numeric(series: pd.Series) -> pd.Series:
    """Try to parse a string series as numbers with Indonesian formatting."""
    s = series.astype(str).str.strip()
    # Ignore clearly non-numeric values
    if not s.str.match(r'^[\d\s\.\,\-\(\)\%]+$', na=False).any():
        return series
    cleaned = (
        s.str.replace(r'\s+', '', regex=True)
        .str.replace('%', '', regex=False)
        .str.replace(r'\(([^)]+)\)', r'-\1', regex=True)
    )
    # Heuristic: if a comma exists, treat it as the decimal separator and
    # dots as thousand separators. Otherwise treat dots as thousand separators.
    if cleaned.str.contains(',', regex=False).any():
        cleaned = cleaned.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    else:
        cleaned = cleaned.str.replace('.', '', regex=False)
    numeric = pd.to_numeric(cleaned, errors='coerce')
    return numeric if numeric.notna().any() else series


def load_csv(source):
    df = pd.read_csv(source, sep=None, engine='python')
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = _parse_numeric(df[col])
    return df


uploaded_file = st.file_uploader('Upload a CSV file', type='csv')
if uploaded_file is not None:
    df = load_csv(uploaded_file)
else:
    df = load_csv(Path(__file__).parent / 'sample.csv')

# Keep edits in session state and reset when the source changes.
source_key = uploaded_file.name if uploaded_file is not None else '__sample__'
if st.session_state.get('finplot_source_key') != source_key:
    st.session_state['finplot_source_key'] = source_key
    st.session_state['finplot_df'] = df.copy()

with st.expander('Data Editor', expanded=False):
    edited_df = st.data_editor(
        st.session_state['finplot_df'],
        width='stretch',
        num_rows='dynamic',
        key='finplot_editor',
    )
    st.session_state['finplot_df'] = edited_df

    csv_buffer = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='Download edited CSV',
        data=csv_buffer,
        file_name='finplot_edited.csv',
        mime='text/csv',
        key='finplot_download',
    )

# `raw_df` is what the editor works on and reflects user edits. The dashboard
# below uses `df`, which may be an aggregated view derived from `raw_df`.
raw_df = st.session_state['finplot_df']
df = raw_df

# --------------------------------------------------------------------------- #
# Column classification
# --------------------------------------------------------------------------- #
num_cols = df.select_dtypes(include='number').columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()

PCT_RE = re.compile(r'(%|pct|margin|share|growth|rate|ratio|yield|change)', re.IGNORECASE)
pct_cols = [c for c in num_cols if PCT_RE.search(c)]
abs_cols = [c for c in num_cols if c not in pct_cols]

LABEL_COL = cat_cols[0] if cat_cols else None

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def fmt_abs(n):
    if abs(n) >= 1e9:
        return f'{n / 1e9:,.1f}B'
    if abs(n) >= 1e6:
        return f'{n / 1e6:,.1f}M'
    if abs(n) >= 1e3:
        return f'{n / 1e3:,.1f}K'
    return f'{n:,.0f}'


def fmt_pct(n):
    return f'{n:.1f}%'


def delta_class(v):
    if v > 0:
        return 'up'
    if v < 0:
        return 'down'
    return 'flat'


def delta_arrow(v):
    if v > 0:
        return '&#9650;'
    if v < 0:
        return '&#9660;'
    return '&#9654;'


MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]

TIME_PERIOD_RE = re.compile(
    r'^\s*(?:'
    r'\d{4}(?:[-/]\d{1,2})?'
    r'|\d{1,2}[-/]\d{4}'
    r'|Q[1-4]\s*\d{4}'
    r'|(?:' + '|'.join(MONTHS) + r')\s+\d{4}'
    r'|\d{1,2}\s+(?:' + '|'.join(MONTHS) + r')\s+\d{4}'
    r')\s*$',
    re.IGNORECASE,
)


def _period_sort_key(name):
    s = str(name).strip()
    m = re.fullmatch(r'(\d{4})-(\d{1,2})', s)
    if m:
        return (int(m.group(1)), int(m.group(2)), 0)
    m = re.fullmatch(r'(\d{4})/(\d{1,2})', s)
    if m:
        return (int(m.group(1)), int(m.group(2)), 0)
    m = re.fullmatch(r'(\d{4})', s)
    if m:
        return (int(m.group(1)), 0, 0)
    m = re.fullmatch(r'(\d{1,2})[-/](\d{4})', s)
    if m:
        return (int(m.group(2)), int(m.group(1)), 0)
    m = re.fullmatch(r'Q([1-4])\s*(\d{4})', s, re.I)
    if m:
        return (int(m.group(2)), 0, int(m.group(1)))
    m = re.fullmatch(r'(' + '|'.join(MONTHS) + r')\s+(\d{4})', s, re.I)
    if m:
        return (int(m.group(2)), MONTHS.index(m.group(1).title()) + 1, 0)
    m = re.fullmatch(r'(\d{1,2})\s+(' + '|'.join(MONTHS) + r')\s+(\d{4})', s, re.I)
    if m:
        return (int(m.group(3)), MONTHS.index(m.group(2).title()) + 1, int(m.group(1)))
    return (0, 0, 0)


# --------------------------------------------------------------------------- #
# Time-period detection (two comparable periods, e.g. 2024 vs 2025)
# --------------------------------------------------------------------------- #
_time_cols = [c for c in df.columns if TIME_PERIOD_RE.match(str(c))]
_time_cols_sorted = sorted(_time_cols, key=_period_sort_key)
PERIOD_PREV, PERIOD_CURR = None, None
if len(_time_cols_sorted) >= 2:
    PERIOD_PREV, PERIOD_CURR = _time_cols_sorted[-2], _time_cols_sorted[-1]


# --------------------------------------------------------------------------- #
# User configuration
# --------------------------------------------------------------------------- #
if not LABEL_COL:
    st.warning('No categorical column found. Please upload a CSV with at least one text column.')
    st.stop()

if not num_cols:
    st.warning(
        'No numeric columns found. Please upload a CSV with numeric values '
        '(semicolon or comma separators are supported).'
    )
    st.stop()

with st.sidebar:
    st.markdown('### Configuration')
    selected_label = st.selectbox('Category column', cat_cols, key='fin_label')
    LABEL_COL = selected_label

    has_duplicates = df[LABEL_COL].duplicated().any()
    aggregate_dups = False
    if has_duplicates:
        aggregate_dups = st.checkbox(
            f'Aggregate duplicate {LABEL_COL} rows (sum)',
            value=True,
            key='fin_aggregate',
            help='Sum numeric columns for rows sharing the same category value.',
        )

    if has_duplicates and aggregate_dups:
        num_for_agg = raw_df.select_dtypes(include='number').columns.tolist()
        df = raw_df.groupby(LABEL_COL, as_index=False)[num_for_agg].sum()
        st.caption(f'Aggregated into {len(df)} unique {LABEL_COL}.')

    if PERIOD_PREV and PERIOD_CURR:
        period_df = df[[LABEL_COL, PERIOD_PREV, PERIOD_CURR]].copy()
        period_df['Diff'] = period_df[PERIOD_CURR] - period_df[PERIOD_PREV]
        _denom = period_df[PERIOD_PREV].replace(0, pd.NA)
        period_df['Change %'] = period_df['Diff'] / _denom * 100
    else:
        period_df = None

    primary_options = abs_cols if abs_cols else num_cols
    PRIMARY_COL = st.selectbox(
        'Primary metric',
        primary_options,
        index=0 if primary_options else None,
        key='fin_primary',
    )

    secondary_options = [c for c in abs_cols if c != PRIMARY_COL] if abs_cols else []
    SECONDARY_COL = (
        st.selectbox('Secondary metric', ['None'] + secondary_options, key='fin_secondary')
        if secondary_options
        else 'None'
    )
    if SECONDARY_COL == 'None':
        SECONDARY_COL = None

    pct_options = pct_cols if pct_cols else ['None']
    PCT_PRIMARY = st.selectbox('Percentage metric', pct_options, key='fin_pct')
    if PCT_PRIMARY == 'None':
        PCT_PRIMARY = None

    growth_options = [c for c in pct_cols if c != PCT_PRIMARY] if pct_cols else ['None']
    GROWTH_COL = (
        st.selectbox('Growth / change metric', ['None'] + growth_options, key='fin_growth')
        if growth_options
        else 'None'
    )
    if GROWTH_COL == 'None':
        GROWTH_COL = None

    if GROWTH_COL:
        SHOW_GROWTH_LABELS = st.checkbox(
            'Show growth labels', value=True, key='fin_growth_labels',
            help='Display the value next to each lollipop dot.',
        )
    else:
        SHOW_GROWTH_LABELS = False

# --------------------------------------------------------------------------- #
# KPI Cards
# --------------------------------------------------------------------------- #
st.markdown('<div class="section-label">Key Metrics</div>', unsafe_allow_html=True)

kpi_cols = st.columns(4)

total_primary = df[PRIMARY_COL].sum()
kpi_cols[0].markdown(
    f'<div class="kpi-card">'
    f'<div class="kpi-label">Total {PRIMARY_COL}</div>'
    f'<div class="kpi-value">{fmt_abs(total_primary)}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

if SECONDARY_COL:
    total_secondary = df[SECONDARY_COL].sum()
    ratio = (total_secondary / total_primary * 100) if total_primary else 0
    kpi_cols[1].markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Total {SECONDARY_COL}</div>'
        f'<div class="kpi-value">{fmt_abs(total_secondary)}</div>'
        f'<div class="kpi-sub flat">{ratio:.1f}% of {PRIMARY_COL}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

if PCT_PRIMARY:
    avg_pct = df[PCT_PRIMARY].mean()
    cls = delta_class(avg_pct)
    kpi_cols[2].markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Avg {PCT_PRIMARY}</div>'
        f'<div class="kpi-value">{fmt_pct(avg_pct)}</div>'
        f'<div class="kpi-sub {cls}">{delta_arrow(avg_pct)} across segments</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

if GROWTH_COL:
    avg_growth = df[GROWTH_COL].mean()
    cls = delta_class(avg_growth)
    kpi_cols[3].markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Avg {GROWTH_COL}</div>'
        f'<div class="kpi-value">{fmt_pct(avg_growth)}</div>'
        f'<div class="kpi-sub {cls}">{delta_arrow(avg_growth)} avg change</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

if PERIOD_PREV and PERIOD_CURR:
    tot_prev = period_df[PERIOD_PREV].sum()
    tot_curr = period_df[PERIOD_CURR].sum()
    tot_diff = tot_curr - tot_prev
    tot_pct = (tot_diff / tot_prev * 100) if tot_prev else 0.0
    pcols = st.columns(2)
    cls = delta_class(tot_diff)
    pcols[0].markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{PERIOD_CURR} minus {PERIOD_PREV} (Diff)</div>'
        f'<div class="kpi-value">{tot_diff:+,.0f}</div>'
        f'<div class="kpi-sub {cls}">{delta_arrow(tot_diff)} {fmt_abs(abs(tot_diff))} change</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    cls2 = delta_class(tot_pct)
    pcols[1].markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{PERIOD_CURR} vs {PERIOD_PREV} (Change)</div>'
        f'<div class="kpi-value">{tot_pct:+.1f}%</div>'
        f'<div class="kpi-sub {cls2}">{delta_arrow(tot_pct)} vs prior period</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# 1. Primary Metric — Horizontal Bar
# --------------------------------------------------------------------------- #
st.markdown('<div class="section-label">Primary Metric Breakdown</div>', unsafe_allow_html=True)

bar_df = df[[LABEL_COL, PRIMARY_COL]].copy()
bar_df = bar_df.sort_values(PRIMARY_COL, ascending=True)
bar_df['_pct'] = bar_df[PRIMARY_COL] / bar_df[PRIMARY_COL].sum() * 100

bar_chart = (
    alt.Chart(bar_df)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X(
            f'{PRIMARY_COL}:Q',
            title=None,
            axis=alt.Axis(format='~s', grid=True),
        ),
        y=alt.Y(
            f'{LABEL_COL}:N',
            sort=None,
            title=None,
            axis=alt.Axis(labelLimit=200, labelFontSize=13),
        ),
        color=alt.condition(
            alt.datum[PRIMARY_COL] == bar_df[PRIMARY_COL].max(),
            alt.value(PALETTE['revenue']),
            alt.value(PALETTE['revenue_light']),
        ),
        tooltip=[
            alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
            alt.Tooltip(f'{PRIMARY_COL}:Q', format=',', title=PRIMARY_COL),
            alt.Tooltip('_pct:Q', format='.1f', title='Share (%)'),
        ],
    )
    .properties(height=max(220, 50 * len(bar_df)))
)

bar_labels = (
    alt.Chart(bar_df)
    .mark_text(align='left', dx=6, fontSize=12, fontWeight=600, color=PALETTE['ink'])
    .encode(
        x=alt.X(f'{PRIMARY_COL}:Q'),
        y=alt.Y(f'{LABEL_COL}:N', sort=None),
        text=alt.Text('_pct:Q', format='.1f'),
    )
)

st.altair_chart(bar_chart + bar_labels, width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# 2. Cost Structure — Stacked Bar (if multiple absolute columns)
# --------------------------------------------------------------------------- #
if len(abs_cols) >= 3:
    st.markdown('<div class="section-label">Cost Structure</div>', unsafe_allow_html=True)

    stack_cols = abs_cols[:5]
    stack_df = df[[LABEL_COL] + stack_cols].melt(
        id_vars=[LABEL_COL],
        value_vars=stack_cols,
        var_name='Metric',
        value_name='Value',
    )

    stack_order = (
        df.groupby(LABEL_COL)[stack_cols[0]].sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    stack_chart = (
        alt.Chart(stack_df)
        .mark_bar(cornerRadiusEnd=2)
        .encode(
            x=alt.X(
                f'{LABEL_COL}:N',
                sort=stack_order,
                title=None,
                axis=alt.Axis(labelAngle=-20, labelLimit=160),
            ),
            y=alt.Y('Value:Q', title='Value', axis=alt.Axis(format='~s')),
            color=alt.Color(
                'Metric:N',
                sort=stack_cols,
                scale=alt.Scale(range=FIN_COLORS[:len(stack_cols)]),
                legend=alt.Legend(title=None, orient='top', columns=3),
            ),
            tooltip=[
                alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                alt.Tooltip('Metric:N'),
                alt.Tooltip('Value:Q', format=','),
            ],
        )
        .properties(height=340)
    )

    st.altair_chart(stack_chart, width='stretch')
    st.markdown('<hr class="rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# 3. Margin / Percentage Comparison
# --------------------------------------------------------------------------- #
if PCT_PRIMARY and len(pct_cols) >= 2:
    st.markdown('<div class="section-label">Profitability Metrics</div>', unsafe_allow_html=True)

    pct_compare = pct_cols[:4]
    pct_df = df[[LABEL_COL] + pct_compare].melt(
        id_vars=[LABEL_COL],
        value_vars=pct_compare,
        var_name='Metric',
        value_name='Value',
    )

    pct_order = (
        df.groupby(LABEL_COL)[pct_compare[0]].sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    pct_chart = (
        alt.Chart(pct_df)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X(
                f'{LABEL_COL}:N',
                sort=pct_order,
                title=None,
                axis=alt.Axis(labelAngle=-20, labelLimit=160),
            ),
            y=alt.Y('Value:Q', title='Percentage', axis=alt.Axis(format='.0f')),
            xOffset='Metric:N',
            color=alt.Color(
                'Metric:N',
                sort=pct_compare,
                scale=alt.Scale(range=FIN_COLORS[:len(pct_compare)]),
                legend=alt.Legend(title=None, orient='top', columns=3),
            ),
            tooltip=[
                alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                alt.Tooltip('Metric:N'),
                alt.Tooltip('Value:Q', format='.1f'),
            ],
        )
        .properties(height=320)
    )

    st.altair_chart(pct_chart, width='stretch')
    st.markdown('<hr class="rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# 4. Growth / Change — Diverging Lollipop
# --------------------------------------------------------------------------- #
if GROWTH_COL:
    st.markdown('<div class="section-label">Growth Landscape</div>', unsafe_allow_html=True)

    growth_df = df[[LABEL_COL, GROWTH_COL]].copy()
    growth_df = growth_df.sort_values(GROWTH_COL, ascending=True)
    growth_df['Direction'] = growth_df[GROWTH_COL].map(
        lambda x: 'Positive' if x >= 0 else 'Negative'
    )

    lol_base = alt.Chart(growth_df).encode(
        y=alt.Y(
            f'{LABEL_COL}:N',
            sort=None,
            title=None,
            axis=alt.Axis(labelLimit=200, labelFontSize=13),
        ),
    )

    lol_stem = lol_base.mark_rule(strokeWidth=2.5).encode(
        x=alt.X(
            f'{GROWTH_COL}:Q',
            title=GROWTH_COL,
            scale=alt.Scale(zero=True),
            axis=alt.Axis(format='.0f'),
        ),
        color=alt.Color(
            'Direction:N',
            scale=alt.Scale(
                domain=['Negative', 'Positive'],
                range=[PALETTE['negative'], PALETTE['positive']],
            ),
            legend=None,
        ),
    )

    lol_dot = lol_base.mark_circle(size=200, opacity=0.95).encode(
        x=alt.X(f'{GROWTH_COL}:Q', scale=alt.Scale(zero=True)),
        color=alt.Color(
            'Direction:N',
            scale=alt.Scale(
                domain=['Negative', 'Positive'],
                range=[PALETTE['negative'], PALETTE['positive']],
            ),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
            alt.Tooltip(f'{GROWTH_COL}:Q', format='+.1f', title=GROWTH_COL),
        ],
    )

    lol_label = (
        alt.Chart(growth_df)
        .transform_filter(alt.datum[GROWTH_COL] >= 0)
        .mark_text(
            align='left',
            dx=8,
            fontSize=12,
            fontWeight=600,
        )
        .encode(
            x=alt.X(f'{GROWTH_COL}:Q'),
            y=alt.Y(f'{LABEL_COL}:N', sort=None),
            text=alt.Text(f'{GROWTH_COL}:Q', format='+.1f'),
            color=alt.value(PALETTE['positive']),
        )
    )

    lol_label_neg = (
        alt.Chart(growth_df)
        .transform_filter(alt.datum[GROWTH_COL] < 0)
        .mark_text(
            align='right',
            dx=-8,
            fontSize=12,
            fontWeight=600,
        )
        .encode(
            x=alt.X(f'{GROWTH_COL}:Q'),
            y=alt.Y(f'{LABEL_COL}:N', sort=None),
            text=alt.Text(f'{GROWTH_COL}:Q', format='+.1f'),
            color=alt.value(PALETTE['negative']),
        )
    )

    zero_line = (
        alt.Chart(pd.DataFrame({'x': [0]}))
        .mark_rule(color=PALETTE['grid'], strokeWidth=1.5)
        .encode(x='x:Q')
    )

    growth_labels = lol_label + lol_label_neg if SHOW_GROWTH_LABELS else alt.Chart().mark_point(opacity=0)

    growth_chart = (zero_line + lol_stem + lol_dot + growth_labels).properties(
        height=max(250, 55 * len(growth_df)),
        title=alt.Title(
            f'{GROWTH_COL} by {LABEL_COL}',
            subtitle='Diverging growth by category.',
        ),
    )

    st.altair_chart(growth_chart, width='stretch')
    st.markdown('<hr class="rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# 5a. Period Change — diff and percentage change between two periods
# --------------------------------------------------------------------------- #
if PERIOD_PREV and PERIOD_CURR:
    st.markdown('<div class="section-label">Period Change</div>', unsafe_allow_html=True)

    chg_df = period_df.sort_values('Diff', ascending=True).copy()
    chg_df['Direction'] = chg_df['Diff'].map(lambda x: 'Positive' if x >= 0 else 'Negative')

    chg_base = alt.Chart(chg_df).encode(
        y=alt.Y(
            f'{LABEL_COL}:N',
            sort=None,
            title=None,
            axis=alt.Axis(labelLimit=200, labelFontSize=13),
        ),
    )

    chg_color = alt.Color(
        'Direction:N',
        scale=alt.Scale(
            domain=['Negative', 'Positive'],
            range=[PALETTE['negative'], PALETTE['positive']],
        ),
        legend=None,
    )

    chg_stem = chg_base.mark_rule(strokeWidth=2.5).encode(
        x=alt.X(
            'Diff:Q',
            title=f'Diff ({PERIOD_PREV} \u2192 {PERIOD_CURR})',
            scale=alt.Scale(zero=True),
            axis=alt.Axis(format='~s'),
        ),
        color=chg_color,
    )

    chg_dot = chg_base.mark_circle(size=200, opacity=0.95).encode(
        x=alt.X('Diff:Q', scale=alt.Scale(zero=True)),
        color=chg_color,
        tooltip=[
            alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
            alt.Tooltip('Diff:Q', format='+,', title='Diff'),
            alt.Tooltip('Change %:Q', format='+.1f', title='Change %'),
            alt.Tooltip(f'{PERIOD_PREV}:Q', format=',', title=PERIOD_PREV),
            alt.Tooltip(f'{PERIOD_CURR}:Q', format=',', title=PERIOD_CURR),
        ],
    )

    chg_label_pos = (
        alt.Chart(chg_df)
        .transform_filter(alt.datum['Diff'] >= 0)
        .mark_text(align='left', dx=8, fontSize=12, fontWeight=600)
        .encode(
            x=alt.X('Diff:Q'),
            y=alt.Y(f'{LABEL_COL}:N', sort=None),
            text=alt.Text('Change %:Q', format='+.1f'),
            color=alt.value(PALETTE['positive']),
        )
    )

    chg_label_neg = (
        alt.Chart(chg_df)
        .transform_filter(alt.datum['Diff'] < 0)
        .mark_text(align='right', dx=-8, fontSize=12, fontWeight=600)
        .encode(
            x=alt.X('Diff:Q'),
            y=alt.Y(f'{LABEL_COL}:N', sort=None),
            text=alt.Text('Change %:Q', format='+.1f'),
            color=alt.value(PALETTE['negative']),
        )
    )

    chg_zero = (
        alt.Chart(pd.DataFrame({'x': [0]}))
        .mark_rule(color=PALETTE['grid'], strokeWidth=1.5)
        .encode(x='x:Q')
    )

    period_chart = (
        chg_zero + chg_stem + chg_dot + chg_label_pos + chg_label_neg
    ).properties(
        height=max(250, 55 * len(chg_df)),
        title=alt.Title(
            f'{PERIOD_CURR} vs {PERIOD_PREV}',
            subtitle='Diverging diff lollipop; labels show percentage change.',
        ),
    )

    st.altair_chart(period_chart, width='stretch')
    st.markdown('<hr class="rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# 5b. Composition — Donut Chart (side by side when two periods are detected)
# --------------------------------------------------------------------------- #
st.markdown('<div class="section-label">Composition</div>', unsafe_allow_html=True)


def _donut(value_col, legend_title):
    cdf = df[[LABEL_COL, value_col]].copy()
    total = cdf[value_col].sum()
    cdf['_share'] = cdf[value_col] / total * 100 if total else 0
    cdf = cdf.sort_values(value_col, ascending=False)
    arc = (
        alt.Chart(cdf)
        .mark_arc(innerRadius=85, stroke='white', strokeWidth=3)
        .encode(
            theta=alt.Theta(f'{value_col}:Q', title=None),
            color=alt.Color(
                f'{LABEL_COL}:N',
                sort=cdf[LABEL_COL].tolist(),
                scale=alt.Scale(range=FIN_COLORS[:len(cdf)]),
                legend=alt.Legend(
                    title=legend_title,
                    orient='right',
                    labelLimit=180,
                    symbolSize=140,
                ),
            ),
            tooltip=[
                alt.Tooltip(f'{LABEL_COL}:N', title=LABEL_COL),
                alt.Tooltip(f'{value_col}:Q', format=',', title=value_col),
                alt.Tooltip('_share:Q', format='.1f', title='Share (%)'),
            ],
        )
        .properties(height=380)
    )
    center = (
        alt.Chart(pd.DataFrame({'text': [fmt_abs(total)]}))
        .mark_text(fontSize=22, fontWeight=700, color=PALETTE['ink'])
        .encode(text='text:N')
    )
    return arc + center


if PERIOD_PREV and PERIOD_CURR:
    st.caption(
        f'Side-by-side composition of **{PERIOD_PREV}** and **{PERIOD_CURR}**. '
        f'Use the Period Change chart above for diff and percentage change.'
    )
    _dc = st.columns(2)
    with _dc[0]:
        st.altair_chart(_donut(PERIOD_PREV, str(PERIOD_PREV)), width='stretch')
    with _dc[1]:
        st.altair_chart(_donut(PERIOD_CURR, str(PERIOD_CURR)), width='stretch')
else:
    st.altair_chart(_donut(PRIMARY_COL, f'Total {PRIMARY_COL}'), width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# 6. Detailed Table
# --------------------------------------------------------------------------- #
st.markdown('<div class="section-label">Detail Table</div>', unsafe_allow_html=True)

display_df = df.copy()
for col in abs_cols:
    display_df[col] = display_df[col].apply(fmt_abs)
for col in pct_cols:
    display_df[col] = display_df[col].apply(lambda x: f'{x:.1f}%')

st.dataframe(display_df, width='stretch', hide_index=True)
