from pathlib import Path

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

PALETTE = {
    'primary': '#FF4500',
    'secondary': '#0079D3',
    'ink': '#16202A',
    'muted': '#6B7785',
    'grid': '#E6E2D9',
    'bg_card': '#F7F5F0',
}

@alt.theme.register('reddit', enable=True)
def reddit_theme():
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

st.set_page_config(page_title='Reddit Stats', layout='wide')

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
        .kpi-card {
            background: #F7F5F0; border-radius: 10px; padding: 1.2rem 1.4rem;
            border: 1px solid #E6E2D9;
        }
        .kpi-label { font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
            color: #6B7785; font-weight: 600; }
        .kpi-value { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.02em; color: #16202A;
            line-height: 1.1; margin-top: 0.2rem; }
        .rule { height: 1px; background: #E6E2D9; margin: 2.25rem 0; border: none; }
        .section-label {
            font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
            color: #6B7785; font-weight: 600; margin-bottom: 0.5rem; margin-top: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">Reddit Stats</div>', unsafe_allow_html=True)
st.title('Indonesian Subreddit Subscribers')
st.markdown(
    '<p class="lede">Subscriber counts for Indonesian-related subreddits. '
    'Data scraped from Reddit API.</p>',
    unsafe_allow_html=True,
)

def _find_csv(name: str = 'subreddit_stats.csv') -> Path:
    start = Path(__file__).resolve().parent
    for parent in [start, *start.parents]:
        candidate = parent / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find {name} starting from {start}")


df = pd.read_csv(_find_csv())
df = df[df['status'] == 'ok'].copy()
df = df.dropna(subset=['subscribers'])
df['subscribers'] = df['subscribers'].astype(int)
df['created_utc'] = pd.to_datetime(df['created_utc'], errors='coerce', utc=True)
df = df.dropna(subset=['created_utc']).copy()
now_utc = pd.Timestamp.now(tz='UTC')
df['age_years'] = (now_utc - df['created_utc']).dt.total_seconds() / (365.25 * 24 * 60 * 60)
df = df.sort_values('subscribers', ascending=False).reset_index(drop=True)

total_subs = df['subscribers'].sum()
n_subreddits = len(df)
mean_subs = df['subscribers'].mean()
median_subs = df['subscribers'].median()
std_subs = df['subscribers'].std()
max_subs = df['subscribers'].max()
min_subs_val = df['subscribers'].min()
q1 = df['subscribers'].quantile(0.25)
q3 = df['subscribers'].quantile(0.75)
top_sub = df.iloc[0]['subreddit']

mean_age = df['age_years'].mean()
median_age = df['age_years'].median()
oldest_sub = df.loc[df['age_years'].idxmax(), 'subreddit']
oldest_age = df['age_years'].max()
newest_sub = df.loc[df['age_years'].idxmin(), 'subreddit']
newest_age = df['age_years'].min()

c1, c2, c3, c4 = st.columns(4)
c1.markdown(
    f'<div class="kpi-card">'
    f'<div class="kpi-label">Total Subscribers</div>'
    f'<div class="kpi-value">{total_subs:,}</div>'
    f'</div>',
    unsafe_allow_html=True,
)
c2.markdown(
    f'<div class="kpi-card">'
    f'<div class="kpi-label">Subreddits</div>'
    f'<div class="kpi-value">{n_subreddits}</div>'
    f'</div>',
    unsafe_allow_html=True,
)
c3.markdown(
    f'<div class="kpi-card">'
    f'<div class="kpi-label">Largest</div>'
    f'<div class="kpi-value">{max_subs:,}</div>'
    f'<div class="kpi-label" style="margin-top:4px">r/{top_sub}</div>'
    f'</div>',
    unsafe_allow_html=True,
)
c4.markdown(
    f'<div class="kpi-card">'
    f'<div class="kpi-label">Median</div>'
    f'<div class="kpi-value">{median_subs:,.0f}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

st.markdown('<div class="section-label">Distribution</div>', unsafe_allow_html=True)

stat_cols = st.columns(6)
stat_cols[0].markdown(f'<div class="kpi-card"><div class="kpi-label">Mean</div><div class="kpi-value" style="font-size:1.3rem">{mean_subs:,.0f}</div></div>', unsafe_allow_html=True)
stat_cols[1].markdown(f'<div class="kpi-card"><div class="kpi-label">Std Dev</div><div class="kpi-value" style="font-size:1.3rem">{std_subs:,.0f}</div></div>', unsafe_allow_html=True)
stat_cols[2].markdown(f'<div class="kpi-card"><div class="kpi-label">Min</div><div class="kpi-value" style="font-size:1.3rem">{min_subs_val:,}</div></div>', unsafe_allow_html=True)
stat_cols[3].markdown(f'<div class="kpi-card"><div class="kpi-label">Q1 (25%)</div><div class="kpi-value" style="font-size:1.3rem">{q1:,.0f}</div></div>', unsafe_allow_html=True)
stat_cols[4].markdown(f'<div class="kpi-card"><div class="kpi-label">Q3 (75%)</div><div class="kpi-value" style="font-size:1.3rem">{q3:,.0f}</div></div>', unsafe_allow_html=True)
stat_cols[5].markdown(f'<div class="kpi-card"><div class="kpi-label">Max</div><div class="kpi-value" style="font-size:1.3rem">{max_subs:,}</div></div>', unsafe_allow_html=True)

log_subs = np.log10(df['subscribers'].replace(0, np.nan)).dropna()
log_lo = float(np.floor(log_subs.min()))
log_hi = float(np.ceil(log_subs.max()))
bin_max = max(2, min(60, int(np.ceil((log_hi - log_lo) * 4)) + 1))
log_edges = list(np.linspace(log_lo, log_hi, bin_max + 1))


def _fmt_si(n: float) -> str:
    n = float(n)
    sign = '-' if n < 0 else ''
    n = abs(n)
    for threshold, suffix in [(1e9, 'B'), (1e6, 'M'), (1e3, 'K')]:
        if n >= threshold:
            value = n / threshold
            return f'{sign}{value:.0f}{suffix}' if value >= 10 else f'{sign}{value:.1f}{suffix}'
    return f'{sign}{n:.0f}'


edge_labels = [_fmt_si(10 ** e) for e in log_edges]

bin_idx = np.clip(np.digitize(log_subs, log_edges) - 1, 0, bin_max - 1)
all_ranges = [f'{edge_labels[i]} – {edge_labels[i + 1]}' for i in range(bin_max)]
ranges = [all_ranges[i] for i in bin_idx]
hist_summary = (
    pd.DataFrame({'range': ranges})
    .groupby('range', as_index=False)
    .size()
    .rename(columns={'size': 'count'})
)
present = set(hist_summary['range'])
ordered = [r for r in all_ranges if r in present]
hist_summary['range'] = pd.Categorical(hist_summary['range'], categories=ordered, ordered=True)
hist_summary = hist_summary.sort_values('range').reset_index(drop=True)

hist_chart = (
    alt.Chart(hist_summary)
    .mark_bar(cornerRadiusEnd=2)
    .encode(
        x=alt.X(
            'range:N',
            title='Subscribers (log10 scale)',
            sort=ordered,
            axis=alt.Axis(labelAngle=0, labelFontSize=10),
        ),
        y=alt.Y('count:Q', title='Number of Subreddits'),
        color=alt.value(PALETTE['secondary']),
        tooltip=[
            alt.Tooltip('range:N', title='Subscribers range'),
            alt.Tooltip('count:Q', title='Count'),
        ],
    )
    .properties(height=250)
)
st.altair_chart(hist_chart, width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

st.markdown('<div class="section-label">Age</div>', unsafe_allow_html=True)

age_cols = st.columns(5)
age_cols[0].markdown(f'<div class="kpi-card"><div class="kpi-label">Mean Age</div><div class="kpi-value" style="font-size:1.3rem">{mean_age:.1f} yrs</div></div>', unsafe_allow_html=True)
age_cols[1].markdown(f'<div class="kpi-card"><div class="kpi-label">Median Age</div><div class="kpi-value" style="font-size:1.3rem">{median_age:.1f} yrs</div></div>', unsafe_allow_html=True)
age_cols[2].markdown(f'<div class="kpi-card"><div class="kpi-label">Oldest</div><div class="kpi-value" style="font-size:1.3rem">{oldest_age:.1f} yrs</div><div class="kpi-label" style="margin-top:4px">r/{oldest_sub}</div></div>', unsafe_allow_html=True)
age_cols[3].markdown(f'<div class="kpi-card"><div class="kpi-label">Newest</div><div class="kpi-value" style="font-size:1.3rem">{newest_age:.1f} yrs</div><div class="kpi-label" style="margin-top:4px">r/{newest_sub}</div></div>', unsafe_allow_html=True)
age_cols[4].markdown(f'<div class="kpi-card"><div class="kpi-label">Correlation</div><div class="kpi-value" style="font-size:1.3rem">{df["subscribers"].corr(df["age_years"]):.2f}</div><div class="kpi-label" style="margin-top:4px">subs vs age</div></div>', unsafe_allow_html=True)

age_hist = (
    alt.Chart(df)
    .mark_bar(cornerRadiusEnd=2)
    .encode(
        x=alt.X('age_years:Q', bin=alt.Bin(maxbins=25), title='Age (years)'),
        y=alt.Y('count()', title='Number of Subreddits'),
        color=alt.value(PALETTE['secondary']),
        tooltip=[alt.Tooltip('age_years:Q', bin=True, title='Age range'), alt.Tooltip('count()', title='Count')],
    )
    .properties(height=250)
)
st.altair_chart(age_hist, width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### Configuration')
    top_n = st.slider('Top N subreddits', 10, min(100, n_subreddits), 50, key='reddit_top_n')
    min_subs = st.number_input('Minimum subscribers', 0, int(df['subscribers'].max()), 0, key='reddit_min')
    show_scatter_labels = st.checkbox('Show labels on scatter plot', value=False, key='reddit_show_labels')
    label_all_points = st.checkbox('Label all points', value=False, key='reddit_label_all', disabled=not show_scatter_labels)
    n_scatter_labels = st.slider(
        'Number of labels (spread across plot)', 1, n_subreddits, min(10, n_subreddits),
        key='reddit_n_labels', disabled=not show_scatter_labels or label_all_points,
    )
    top_n_age = st.slider('Top N subreddits by age', 5, min(50, n_subreddits), 20, key='reddit_top_n_age')

st.markdown('<div class="section-label">Growth Rate</div>', unsafe_allow_html=True)

df['growth_rate'] = np.where(df['age_years'] > 0, df['subscribers'] / df['age_years'], np.nan)
mean_growth = df['growth_rate'].mean()
median_growth = df['growth_rate'].median()
fastest_idx = df['growth_rate'].idxmax()
fastest_sub = df.loc[fastest_idx, 'subreddit']
fastest_rate = df.loc[fastest_idx, 'growth_rate']

growth_cols = st.columns(4)
growth_cols[0].markdown(f'<div class="kpi-card"><div class="kpi-label">Mean Growth</div><div class="kpi-value" style="font-size:1.3rem">{mean_growth:,.0f}</div><div class="kpi-label" style="margin-top:4px">subs / year</div></div>', unsafe_allow_html=True)
growth_cols[1].markdown(f'<div class="kpi-card"><div class="kpi-label">Median Growth</div><div class="kpi-value" style="font-size:1.3rem">{median_growth:,.0f}</div><div class="kpi-label" style="margin-top:4px">subs / year</div></div>', unsafe_allow_html=True)
growth_cols[2].markdown(f'<div class="kpi-card"><div class="kpi-label">Fastest</div><div class="kpi-value" style="font-size:1.3rem">{fastest_rate:,.0f}</div><div class="kpi-label" style="margin-top:4px">subs / year</div></div>', unsafe_allow_html=True)
growth_cols[3].markdown(f'<div class="kpi-card"><div class="kpi-label">Fastest Subreddit</div><div class="kpi-value" style="font-size:1.3rem">r/{fastest_sub}</div></div>', unsafe_allow_html=True)

growth_df = df[df['subscribers'] >= min_subs].nlargest(top_n, 'growth_rate').copy()
growth_df = growth_df.sort_values('growth_rate', ascending=False).reset_index(drop=True)
growth_df['_highlight'] = np.where(
    growth_df['growth_rate'].eq(growth_df['growth_rate'].max()), 'Highest', 'Other'
)

growth_chart = (
    alt.Chart(growth_df)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X(
            'growth_rate:Q',
            title='Subscribers per Year',
            axis=alt.Axis(format='~s', grid=True),
        ),
        y=alt.Y(
            'subreddit:N',
            sort=None,
            title=None,
            axis=alt.Axis(labelLimit=200, labelFontSize=12),
        ),
        color=alt.Color(
            '_highlight:N',
            legend=None,
            scale=alt.Scale(
                domain=['Other', 'Highest'],
                range=[PALETTE['secondary'], PALETTE['primary']],
            ),
        ),
        tooltip=[
            alt.Tooltip('subreddit:N', title='Subreddit'),
            alt.Tooltip('growth_rate:Q', format=',.0f', title='Subs / Year'),
            alt.Tooltip('subscribers:Q', format=',', title='Subscribers'),
            alt.Tooltip('age_years:Q', format='.1f', title='Age (years)'),
        ],
    )
    .properties(height=max(300, 28 * len(growth_df)))
)

growth_labels = (
    alt.Chart(growth_df)
    .mark_text(align='left', dx=6, fontSize=11, fontWeight=600, color=PALETTE['ink'])
    .encode(
        x=alt.X('growth_rate:Q'),
        y=alt.Y('subreddit:N', sort=None),
        text=alt.Text('growth_rate:Q', format='.0f'),
    )
)

st.altair_chart(growth_chart + growth_labels, width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

st.markdown('<div class="section-label">Age vs Subscribers</div>', unsafe_allow_html=True)

scatter_df = df[['subreddit', 'subscribers', 'age_years', 'created_utc']].copy()
scatter_df['created_date'] = scatter_df['created_utc'].dt.strftime('%Y-%m-%d')
scatter_df['log_subscribers'] = np.log10(scatter_df['subscribers'].replace(0, np.nan))

x_min = scatter_df['log_subscribers'].min()
x_max = scatter_df['log_subscribers'].max()
y_min = scatter_df['age_years'].min()
y_max = scatter_df['age_years'].max()
x_pad = (x_max - x_min) * 0.08 if x_max > x_min else 0.5
y_pad = (y_max - y_min) * 0.12 if y_max > y_min else 1

x_domain = [x_min - x_pad * 0.1, x_max + x_pad]
y_domain = [y_min - y_pad * 0.1, y_max + y_pad]


def _x_scale():
    return alt.Scale(domain=x_domain, zero=False)


def _y_scale():
    return alt.Scale(domain=y_domain, zero=False)


scatter = (
    alt.Chart(scatter_df)
    .mark_circle(size=80, opacity=0.7)
    .encode(
        x=alt.X(
            'log_subscribers:Q',
            title='Subscribers (log10 scale)',
            scale=_x_scale(),
            axis=alt.Axis(
                values=[0, 1, 2, 3, 4, 5, 6],
                labelExpr="format(pow(10, datum.value), '.0s')",
            ),
        ),
        y=alt.Y(
            'age_years:Q',
            title='Age (years)',
            scale=_y_scale(),
        ),
        color=alt.value(PALETTE['primary']),
        tooltip=[
            alt.Tooltip('subreddit:N', title='Subreddit'),
            alt.Tooltip('subscribers:Q', format=',', title='Subscribers'),
            alt.Tooltip('age_years:Q', format='.1f', title='Age (years)'),
            alt.Tooltip('created_date:N', title='Created'),
        ],
    )
    .properties(height=420)
)

scatter_trend = (
    alt.Chart(scatter_df)
    .transform_regression('log_subscribers', 'age_years')
    .mark_line(color=PALETTE['ink'], opacity=0.4, strokeDash=[4, 4])
    .encode(x='log_subscribers:Q', y='age_years:Q')
)

scatter_layers = [scatter, scatter_trend]
def _select_spread_labels(data, n_labels, x_col='log_subscribers', y_col='age_years', value_col='subscribers'):
    """Pick up to n_labels points spread across the x/y plane instead of just
    the top-N by value. Buckets points into a coarse grid over (x_col, y_col)
    and keeps the highest-value point per occupied cell, so labels land across
    the whole scatter rather than clustering at the top (highest-subscriber) end."""
    if n_labels <= 0 or data.empty:
        return data.iloc[0:0]
    n_labels = min(n_labels, len(data))
    grid_size = max(1, int(np.ceil(np.sqrt(n_labels))))
    x_bins = pd.cut(data[x_col], bins=grid_size, labels=False, include_lowest=True)
    y_bins = pd.cut(data[y_col], bins=grid_size, labels=False, include_lowest=True)
    tmp = data.copy()
    tmp['_cell'] = list(zip(x_bins, y_bins))
    picked = tmp.loc[tmp.groupby('_cell')[value_col].idxmax()]
    if len(picked) > n_labels:
        picked = picked.nlargest(n_labels, value_col)
    return picked.drop(columns='_cell')


if show_scatter_labels:
    label_df = scatter_df if label_all_points else _select_spread_labels(scatter_df, n_scatter_labels)
    scatter_labels = (
        alt.Chart(label_df)
        .mark_text(
            align='left',
            baseline='middle',
            dx=10,
            dy=-10,
            fontSize=11,
            fontWeight=600,
            color=PALETTE['ink'],
            stroke='white',
            strokeWidth=0.1,
            strokeJoin='round',
            clip=False,
        )
        .encode(
            x=alt.X('log_subscribers:Q', scale=_x_scale()),
            y=alt.Y('age_years:Q', scale=_y_scale()),
            text='subreddit:N',
        )
    )
    scatter_layers.append(scatter_labels)

scatter_chart = (
    alt.layer(*scatter_layers)
    .properties(height=420)
    .interactive()
    .configure_view(clip=False)
)
st.altair_chart(scatter_chart, width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

plot_df = df[df['subscribers'] >= min_subs].head(top_n).copy()
plot_df = plot_df.sort_values('subscribers', ascending=False)
plot_df['_highlight'] = np.where(
    plot_df['subscribers'].eq(plot_df['subscribers'].max()), 'Largest', 'Other'
)

st.markdown('<div class="section-label">Subscribers by Subreddit</div>', unsafe_allow_html=True)

bar_chart = (
    alt.Chart(plot_df)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X(
            'subscribers:Q',
            title='Subscribers',
            axis=alt.Axis(format='~s', grid=True),
        ),
        y=alt.Y(
            'subreddit:N',
            sort=None,
            title=None,
            axis=alt.Axis(labelLimit=200, labelFontSize=12),
        ),
        color=alt.Color(
            '_highlight:N',
            legend=None,
            scale=alt.Scale(
                domain=['Other', 'Largest'],
                range=[PALETTE['secondary'], PALETTE['primary']],
            ),
        ),
        tooltip=[
            alt.Tooltip('subreddit:N', title='Subreddit'),
            alt.Tooltip('subscribers:Q', format=',', title='Subscribers'),
        ],
    )
    .properties(height=max(300, 28 * len(plot_df)))
)

bar_labels = (
    alt.Chart(plot_df)
    .mark_text(align='left', dx=6, fontSize=11, fontWeight=600, color=PALETTE['ink'])
    .encode(
        x=alt.X('subscribers:Q'),
        y=alt.Y('subreddit:N', sort=None),
        text=alt.Text('subscribers:Q', format=','),
    )
)

st.altair_chart(bar_chart + bar_labels, width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

st.markdown('<div class="section-label">Age by Subreddit</div>', unsafe_allow_html=True)

age_bar_df = df[df['subscribers'] >= min_subs].nlargest(top_n_age, 'age_years').copy()
age_bar_df = age_bar_df.sort_values('age_years', ascending=False).reset_index(drop=True)
age_bar_df['_highlight'] = np.where(
    age_bar_df['age_years'].eq(age_bar_df['age_years'].max()), 'Oldest', 'Other'
)

age_bar_chart = (
    alt.Chart(age_bar_df)
    .mark_bar(cornerRadiusEnd=2)
    .encode(
        x=alt.X(
            'subreddit:N',
            sort='-y',
            title=None,
            axis=alt.Axis(labelAngle=45, labelFontSize=10, labelLimit=120),
        ),
        y=alt.Y('age_years:Q', title='Age (years)', axis=alt.Axis(format='.1f')),
        color=alt.Color(
            '_highlight:N',
            legend=None,
            scale=alt.Scale(
                domain=['Other', 'Oldest'],
                range=[PALETTE['secondary'], PALETTE['primary']],
            ),
        ),
        tooltip=[
            alt.Tooltip('subreddit:N', title='Subreddit'),
            alt.Tooltip('age_years:Q', format='.1f', title='Age (years)'),
            alt.Tooltip('subscribers:Q', format=',', title='Subscribers'),
        ],
    )
    .properties(height=300)
)

st.altair_chart(age_bar_chart, width='stretch')

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

st.markdown('<div class="section-label">Detail Table</div>', unsafe_allow_html=True)
display_df = df[['subreddit', 'subscribers', 'age_years', 'growth_rate', 'created_utc']].copy()
display_df['created_date'] = display_df['created_utc'].dt.strftime('%Y-%m-%d')
st.dataframe(
    display_df[['subreddit', 'subscribers', 'age_years', 'growth_rate', 'created_date']].rename(
        columns={
            'subreddit': 'Subreddit',
            'subscribers': 'Subscribers',
            'age_years': 'Age (years)',
            'growth_rate': 'Growth Rate (subs/year)',
            'created_date': 'Created',
        }
    ),
    width='stretch',
    hide_index=True,
)
