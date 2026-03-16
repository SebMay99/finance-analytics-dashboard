import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Remove only download button, keep other tools
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['toImage', 'downloadImage'],
    'displaylogo': False
}

def set_row_style(row):
    cat = str(row.Category).upper().strip()
    if cat in ["TOTAL PRODUCT", "TOTAL SERVICES", "TOTAL A&PS"]:
        return ['background-color: #04909d; color: white; font-weight: bold;'] * len(row)
    elif cat in ["TOTAL PRODUCTS+SERVICES"]:
        return ['background-color: #01a982; color: white; font-weight: bold;'] * len(row)
    elif cat in ["GRAND TOTAL"]:
        return ['background-color: #7764fc; color: white; font-weight: bold;'] * len(row)
    return [''] * len(row)

@st.cache_data(show_spinner=False)
def get_color_map(df):
    from public import config

    color_map = {}
    greens  = ["#01A982", "#05CC93", "#00E0AF", "#00B88A", "#009F73"]
    blues   = ["#0070F8", "#35CFF0", "#62D8F6", "#0094FF", "#0AB3D9",
               "#1A8FE0", "#4AC2FF", "#0082CC", "#2BB0E8", "#5FC7FF"]
    purples = ["#7764FC", "#8A6BFF", "#A07AFF"]

    g_idx, y_idx, p_idx = 0, 0, 0
    for cat in df['Category'].unique():
        if cat in config.product_cats_colors:
            color_map[cat] = greens[g_idx % len(greens)]
            g_idx += 1
        elif cat in config.service_cats_colors:
            color_map[cat] = blues[y_idx % len(blues)]
            y_idx += 1
        elif cat in config.aps_cats_colors:
            color_map[cat] = purples[p_idx % len(purples)]
            p_idx += 1

    return color_map

@st.cache_data(show_spinner=False)
def table_generation(filtered_table_df):
    display_df = filtered_table_df.copy()
    for col in ["Cost", "Revenue", "Margin", "Percentage"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].fillna(0)

    html_table = (
        display_df.style
        .apply(set_row_style, axis=1)
        .format({
            "Cost": "${:,.2f}",
            "Revenue": "${:,.2f}",
            "Margin": "${:,.2f}",
            "Percentage": "{:,.2f}%"
        })
        .hide(axis='index')
        .to_html()
    )

    html_table = html_table.replace(">Cost<", ">Costs<") \
                           .replace(">Revenue<", ">Revenue<") \
                           .replace(">Margin<", ">FLGM pre-rebate<") \
                           .replace(">Percentage<", ">FLGM% pre-rebate<")

    return html_table

# ─────────────────────────────────────────────────────────────────────────────
# Bar charts
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _build_bar_figure(filtered_plot_df, colors, graph_type,
                      total_cost, total_revenue, total_margin, total_percentage,
                      scenario, segment):
    margins = dict(l=100, r=30, t=80, b=80)

    cfg = {
        "Cost": {
            "title": f"{scenario} Cost by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Cost (USD)",
            "total_label": f"<b>Total: ${total_cost:,.2f}</b>",
        },
        "Margin": {
            "title": f"{scenario} Total FLGM pre-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Margin (USD)",
            "total_label": f"<b>Total: ${total_margin:,.2f}</b>",
        },
        "Revenue": {
            "title": f"{scenario} Revenue pre-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Revenue (USD)",
            "total_label": f"<b>Total: ${total_revenue:,.2f}</b>",
        },
        "Percentage": {
            "title": f"{scenario} Total FLGM% pre-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}%<extra></extra>",
            "text": "%{y:.2f}%",
            "yaxis_prefix": "",
            "yaxis_title": "Percentage (%)",
            "total_label": f"<b>Total: {total_percentage:.2f}%</b>",
        },
    }[graph_type]

    fig = px.bar(
        filtered_plot_df,
        x='Category',
        y=graph_type,
        title=cfg["title"],
        text_auto='.3s',
        color="Category",
        color_discrete_map=colors,
    )
    fig.update_traces(
        texttemplate=cfg["text"],
        textposition='outside',
        cliponaxis=False,
        meta=dict(graph_type=graph_type),
        hovertemplate=cfg["hover"],
    )
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=cfg["total_label"],
        legendgroup='total',
    ))
    fig.update_layout(
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        margin=margins,
        title_font=dict(size=20),
    )
    fig.update_yaxes(tickprefix=cfg["yaxis_prefix"], title_text=cfg["yaxis_title"])
    return fig


def bar_graph_generation(filtered_plot_df, colors, margins, graph_type,
                         total_cost, total_revenue, total_margin, total_percentage,
                         scenario, segment):
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}".replace(" ", "_")
    fig = _build_bar_figure(filtered_plot_df, colors, graph_type,
                            total_cost, total_revenue, total_margin, total_percentage,
                            scenario, segment)
    st.session_state[f'fig_{chart_key}'] = fig
    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG, key=f"plot_{chart_key}")
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# Donut / Pie charts
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _build_pie_figure(filtered_plot_df, colors, graph_type,
                      total_cost, total_revenue, total_margin,
                      scenario, segment):
    if graph_type == 'Percentage':
        return None

    cfg = {
        "Cost": {
            "title": f"{scenario}{segment}Cost Distribution",
            "hover": "<b>%{label}</b><br>Cost: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total_label": f"<b>Total: ${total_cost:,.2f}</b>",
        },
        "Margin": {
            "title": f"{scenario}{segment}Total FLGM pre-rebate Distribution",
            "hover": "<b>%{label}</b><br>Margin: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total_label": f"<b>Total: ${total_margin:,.2f}</b>",
        },
        "Revenue": {
            "title": f"{scenario}{segment}Revenue pre-rebate Distribution",
            "hover": "<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total_label": f"<b>Total: ${total_revenue:,.2f}</b>",
        },
    }[graph_type]

    fig = px.pie(
        filtered_plot_df,
        values=graph_type,
        names='Category',
        hole=0.5,
        title=cfg["title"],
        color='Category',
        color_discrete_map=colors,
    )
    fig.update_traces(
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='horizontal',
        textfont=dict(weight="bold"),
        hovertemplate=cfg["hover"],
    )
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=cfg["total_label"],
        legendgroup='total',
    ))
    fig.update_layout(
        margin=dict(l=100, r=30, t=80, b=80),
        uniformtext=dict(minsize=10, mode='hide'),
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center'},
        title_font=dict(size=20),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def pie_graph_generation(filtered_plot_df, colors, margins, graph_type,
                         total_cost, total_revenue, total_margin, scenario, segment):
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}".replace(" ", "_")
    fig = _build_pie_figure(filtered_plot_df, colors, graph_type,
                            total_cost, total_revenue, total_margin,
                            scenario, segment)
    if fig is None:
        return None
    st.session_state[f'fig_{chart_key}'] = fig
    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG, key=f"plot_{chart_key}")
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# Selectors
# ─────────────────────────────────────────────────────────────────────────────

def graph_type_selector(filtered_plot_df, chart_type, graph_type, total_cost,
                        total_revenue, total_margin, total_percentage, scenario, segment):
    colors = get_color_map(filtered_plot_df)
    margins = dict(l=100, r=30, t=80, b=80)

    if segment == "All":
        segment = " "
    elif segment == "Products Only":
        segment = " Product "
    elif segment == "Services Only":
        segment = " Service "
    elif segment == "A&PS Only":
        segment = " A&PS "

    if chart_type == "Bar Charts":
        fig = bar_graph_generation(filtered_plot_df, colors, margins, graph_type,
                                   total_cost, total_revenue, total_margin, total_percentage,
                                   scenario, segment)
    elif chart_type == "Donut Charts":
        fig = pie_graph_generation(filtered_plot_df, colors, margins, graph_type,
                                   total_cost, total_revenue, total_margin,
                                   scenario, segment)

    filename = f"{scenario}_{graph_type}_by{segment.strip()}_Segment.png"
    return fig, filename

# ─────────────────────────────────────────────────────────────────────────────
# Rebate bar charts
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _build_rebate_bar_figure(df, colors, graph_type, scenario, segment):
    margins = dict(l=100, r=30, t=80, b=80)

    total_revenue, total_percentage = df.loc[df['Category'] == 'Grand Total', ['Revenue', 'Percentage']].values[0]
    filtered_plot_df = df.drop(df[df['Category'] == 'Grand Total'].index)

    if segment.strip() == "Product":
        filtered_plot_df = filtered_plot_df.drop(
            filtered_plot_df[filtered_plot_df['Category'] == 'Total Services'].index)
        total_revenue, total_percentage = df.loc[df['Category'] == 'Total Product', ['Revenue', 'Percentage']].values[0]
    elif segment.strip() == "Service":
        filtered_plot_df = filtered_plot_df.drop(
            filtered_plot_df[filtered_plot_df['Category'] == 'Total Product'].index)
        total_revenue, total_percentage = df.loc[df['Category'] == 'Total Services', ['Revenue', 'Percentage']].values[0]
    elif segment == "A&PS Only":
        return None

    cfg = {
        "Revenue": {
            "title": f"{scenario} Revenue post-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Revenue (USD)",
            "total_label": f"<b>Total: ${total_revenue:,.2f}</b>",
        },
        "Percentage": {
            "title": f"{scenario} Total FLGM% post-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}%<extra></extra>",
            "text": "%{y:.2f}%",
            "yaxis_prefix": "",
            "yaxis_title": "Percentage (%)",
            "total_label": f"<b>Total: {total_percentage:.2f}%</b>",
        },
    }[graph_type]

    fig = px.bar(
        filtered_plot_df,
        x='Category',
        y=graph_type,
        title=cfg["title"],
        text_auto='.3s',
        color="Category",
        color_discrete_map=colors,
    )
    fig.update_traces(
        texttemplate=cfg["text"],
        textposition='outside',
        cliponaxis=False,
        meta=dict(graph_type=graph_type),
        hovertemplate=cfg["hover"],
    )
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=cfg["total_label"],
        legendgroup='total',
    ))
    fig.update_layout(
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        margin=margins,
        title_font=dict(size=20),
    )
    fig.update_yaxes(tickprefix=cfg["yaxis_prefix"], title_text=cfg["yaxis_title"])
    return fig


def rebate_bar_graph_generation(df, colors, margins, graph_type, scenario, segment):
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}_{margins}".replace(" ", "_")
    fig = _build_rebate_bar_figure(df, colors, graph_type, scenario, segment)
    if fig is None:
        return None
    st.session_state[f'fig_{chart_key}'] = fig
    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG, key=f"plot_{chart_key}")
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# Rebate pie charts
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _build_rebate_pie_figure(df, colors, graph_type, scenario, segment):
    if graph_type == 'Percentage':
        return None

    total_revenue = df.loc[df['Category'] == 'Grand Total', ['Revenue']].values[0].item()
    filtered_plot_df = df.drop(df[df['Category'] == 'Grand Total'].index)

    if segment.strip() == "Product":
        filtered_plot_df = filtered_plot_df.drop(
            filtered_plot_df[filtered_plot_df['Category'] == 'Total Services'].index)
        total_revenue = df.loc[df['Category'] == 'Total Product', ['Revenue']].values[0].item()
    elif segment.strip() == "Service":
        filtered_plot_df = filtered_plot_df.drop(
            filtered_plot_df[filtered_plot_df['Category'] == 'Total Product'].index)
        total_revenue = df.loc[df['Category'] == 'Total Services', ['Revenue']].values[0].item()
    elif segment == "A&PS Only":
        return None

    cfg = {
        "title": f"{scenario}{segment}Revenue post-rebate Distribution",
        "hover": "<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
        "total_label": f"<b>Total: ${total_revenue:,.2f}</b>",
    }

    fig = px.pie(
        filtered_plot_df,
        values=graph_type,
        names='Category',
        hole=0.5,
        title=cfg["title"],
        color='Category',
        color_discrete_map=colors,
    )
    fig.update_traces(
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='horizontal',
        textfont=dict(weight="bold"),
        hovertemplate=cfg["hover"],
    )
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=cfg["total_label"],
        legendgroup='total',
    ))
    fig.update_layout(
        margin=dict(l=100, r=30, t=80, b=80),
        uniformtext=dict(minsize=10, mode='hide'),
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center'},
        title_font=dict(size=20),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def rebate_pie_graph_generation(df, colors, margins, graph_type, scenario, segment):
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}_{margins}".replace(" ", "_")
    fig = _build_rebate_pie_figure(df, colors, graph_type, scenario, segment)
    if fig is None:
        return None
    st.session_state[f'fig_{chart_key}'] = fig
    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG, key=f"plot_{chart_key}")
    return fig


def rebate_graph_type_selector(filtered_plot_df, chart_type, graph_type, scenario, segment):
    colors = get_color_map(filtered_plot_df)
    margins = dict(l=100, r=30, t=80, b=80)

    if segment == "All":
        segment = " "
    elif segment == "Products Only":
        segment = " Product "
    elif segment == "Services Only":
        segment = " Service "

    if chart_type == "Bar Charts":
        fig = rebate_bar_graph_generation(filtered_plot_df, colors, margins, graph_type, scenario, segment)
    elif chart_type == "Donut Charts":
        fig = rebate_pie_graph_generation(filtered_plot_df, colors, margins, graph_type, scenario, segment)
    else:
        fig = None

    return fig
