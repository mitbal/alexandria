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

alt.themes.register(
    'reddit',
    lambda: {
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
    },
)
alt.themes.enable('reddit')

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

df = pd.read_csv('subreddit_stats.csv')
df = df[df['status'] == 'ok'].copy()
df = df.dropna(subset=['subscribers'])
df['subscribers'] = df['subscribers'].astype(int)
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

hist_chart = (
    alt.Chart(df)
    .mark_bar(cornerRadiusEnd=2)
    .encode(
        x=alt.X('subscribers:Q', bin=alt.Bin(maxbins=30), title='Subscribers'),
        y=alt.Y('count()', title='Number of Subreddits'),
        color=alt.value(PALETTE['secondary']),
        tooltip=[alt.Tooltip('subscribers:Q', bin=True, title='Range'), alt.Tooltip('count()', title='Count')],
    )
    .properties(height=250)
)
st.altair_chart(hist_chart, use_container_width=True)

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### Configuration')
    top_n = st.slider('Top N subreddits', 10, min(100, n_subreddits), 50, key='reddit_top_n')
    min_subs = st.number_input('Minimum subscribers', 0, int(df['subscribers'].max()), 0, key='reddit_min')

plot_df = df[df['subscribers'] >= min_subs].head(top_n).copy()
plot_df = plot_df.sort_values('subscribers', ascending=False)

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
        color=alt.condition(
            alt.datum.subscribers == plot_df['subscribers'].max(),
            alt.value(PALETTE['primary']),
            alt.value(PALETTE['secondary']),
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

st.altair_chart(bar_chart + bar_labels, use_container_width=True)

st.markdown('<hr class="rule" />', unsafe_allow_html=True)

st.markdown('<div class="section-label">Detail Table</div>', unsafe_allow_html=True)
st.dataframe(
    df[['subreddit', 'subscribers']].rename(columns={'subreddit': 'Subreddit', 'subscribers': 'Subscribers'}),
    use_container_width=True,
    hide_index=True,
)
