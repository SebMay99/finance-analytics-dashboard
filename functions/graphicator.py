import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
from public import config

# Remove only download button, keep other tools
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['toImage', 'downloadImage'],
    'displaylogo': False
}

def set_row_style(row):
    cat = str(row.Category).upper().strip()
    if cat in [ "TOTAL PRODUCT", "TOTAL SERVICES", "TOTAL A&PS"]:
        return ['background-color: #04909d; color: white; font-weight: bold;'] * len(row)
    elif cat in ["TOTAL PRODUCTS+SERVICES"]:
        return ['background-color: #01a982; color: white; font-weight: bold;'] * len(row)
    elif cat in ["PAN HPE"]:
        return ['background-color: #7764fc; color: white; font-weight: bold;'] * len(row)
    return [''] * len(row)

def get_color_map(df):
    
    color_map = {}
    # Color scales
    greens = ["#01A982", "#05CC93", "#00E0AF", "#00B88A", "#009F73"]
    blues = ["#0070F8", "#35CFF0", "#62D8F6", "#0094FF", "#0AB3D9",
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

def graph_type_selector(filtered_plot_df,chart_type,graph_type,total_cost, 
                        total_revenue,total_margin,total_percentage,scenario,segment):

    # Graph colors
    colors = get_color_map(filtered_plot_df)

    # Graph margins
    margins = dict(l=100, r=30, t=80, b=80)

    # Normalize for graph title
    if segment == "All":
        segment = " "
    elif segment == "Products Only":
        segment = " Product "
    elif segment == "Services Only":
        segment = " Service "
    elif segment == "A&PS Only":
        segment = " A&PS "

    if chart_type == "Bar Charts":
        fig =bar_graph_generation(filtered_plot_df,colors,margins,graph_type,
                             total_cost, total_revenue,total_margin,total_percentage,scenario,segment)
    elif chart_type == "Donut Charts":
        fig = pie_graph_generation(filtered_plot_df,colors,margins,graph_type,
                             total_cost, total_revenue,total_margin,scenario,segment)
        
    # Return figure and filename
    filename = f"{scenario}_{graph_type}_by{segment.strip()}_Segment.png"
    return fig, filename

def bar_graph_generation(filtered_plot_df,colors,margins,graph_type,
                         total_cost, total_revenue,total_margin,total_percentage,scenario,segment):
    
    # Generar chart_key automáticamente
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}".replace(" ", "_")

    # Config by type of graph
    config = {
        "Cost": {
            "total": total_cost,
            "title": f"{scenario} Cost by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Cost (USD)",
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Margin": {
            "total": total_margin,
            "title": f"{scenario} Pan HPE FLGM pre-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Margin (USD)",
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Revenue": {
            "total": total_revenue,
            "title": f"{scenario} Revenue pre-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Revenue (USD)",
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Percentage": {
            "total": total_percentage,
            "title": f"{scenario} Pan HPE FLGM% pre-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}%<extra></extra>",
            "text": "%{y:.2f}%",
            "yaxis_prefix": "",
            "yaxis_title": "Percentage (%)",
            "total_label": lambda t: f"<b>Total: {t:.2f}%</b>"
        }
    }

    # Get config from graph_type
    cfg = config[graph_type]
    total = cfg["total"]
    graph_title = cfg["title"]
    hover_template = cfg["hover"]
    texttemplate = cfg["text"]
    yaxis_prefix = cfg["yaxis_prefix"]
    yaxis_title = cfg["yaxis_title"]
    total_label = cfg["total_label"](total)

    # Create graph
    fig = px.bar(
        filtered_plot_df,
        x='Category',
        y=graph_type,
        title=graph_title,
        text_auto='.3s',
        color="Category",
        color_discrete_map=colors
    )

    fig.update_traces(
        texttemplate=texttemplate,
        textposition='outside',
        cliponaxis=False,
        meta=dict(graph_type=graph_type),
        hovertemplate=hover_template
    )

    # Add total to legend
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=total_label,
        legendgroup='total',
    ))

    # Layout
    fig.update_layout(
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        margin=margins,
        title_font=dict(size=20)
    )

    # Y axis
    fig.update_yaxes(
        tickprefix=yaxis_prefix,
        title_text=yaxis_title
    )

    # Save fig in session_state
    st.session_state[f'fig_{chart_key}'] = fig

    st.plotly_chart(fig, width='stretch', config= PLOTLY_CONFIG, key=f"plot_{chart_key}")

    return fig

def pie_graph_generation(filtered_plot_df, colors, margins, graph_type,
                         total_cost, total_revenue, total_margin,scenario,segment):

    # Generar chart_key automáticamente
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}".replace(" ", "_")

    # No pie graph for Percentage
    if graph_type == 'Percentage':
        return None

    # Config by graph type
    config = {
        "Cost": {
            "title": f"{scenario}{segment}Cost Distribution",
            "hover": "<b>%{label}</b><br>Cost: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total": total_cost,
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Margin": {
            "title": f"{scenario}{segment}Pan HPE FLGM pre-rebate Distribution",
            "hover": "<b>%{label}</b><br>Margin: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total": total_margin,
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Revenue": {
            "title": f"{scenario}{segment}Revenue pre-rebate Distribution",
            "hover": "<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total": total_revenue,
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        }
    }


    cfg = config[graph_type]
    total_label = cfg["total_label"](cfg["total"])

    # Create graph
    fig = px.pie(
        filtered_plot_df,
        values=graph_type,
        names='Category',
        hole=0.5,
        title=cfg["title"],
        color='Category',
        color_discrete_map=colors
    )

    fig.update_traces(
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='horizontal',
        textfont=dict(weight="bold"),
        hovertemplate=cfg["hover"]
    )

    # Add total at the end of the legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=total_label,
        legendgroup='total',
    ))

    fig.update_layout(
        margin=margins,
        uniformtext=dict(minsize=10, mode='hide'),
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center'},
        title_font=dict(size=20)
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Save fig in session_state
    st.session_state[f'fig_{chart_key}'] = fig

    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG, key=f"plot_{chart_key}")

    return fig

def table_generation(filtered_table_df):
    html_table = (
                filtered_table_df.style
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

    # Change HTML headers
    html_table = html_table.replace(">Cost<", ">Costs<") \
                        .replace(">Revenue<", ">Revenue<") \
                        .replace(">Margin<", ">FLGM pre-rebate<")\
                        .replace(">Percentage<", ">FLGM% pre-rebate<")\
                        
    return html_table

def rebate_bar_graph_generation(df,colors,margins,graph_type,scenario,segment):
    # Generar chart_key automáticamente
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}_{margins}".replace(" ", "_")

    total_revenue, total_percentage = df.loc[df['Category'] == 'Pan HPE', ['Revenue','Percentage']].values[0]

    filtered_plot_df = df.drop(df[df['Category'] == 'Pan HPE'].index)

    if segment.strip() == "Product":
        filtered_plot_df = filtered_plot_df.drop(filtered_plot_df[filtered_plot_df['Category'] == 'Total Services'].index)
        total_revenue, total_percentage = df.loc[df['Category'] == 'Total Product', ['Revenue','Percentage']].values[0] 
    elif segment.strip() == "Service":
        filtered_plot_df = filtered_plot_df.drop(filtered_plot_df[filtered_plot_df['Category'] == 'Total Product'].index)
        total_revenue, total_percentage = df.loc[df['Category'] == 'Total Services', ['Revenue','Percentage']].values[0] 
    elif segment == "A&PS Only":
        return None

    # Config by type of graph
    config = {
        "Revenue": {
            "total": total_revenue,
            "title": f"{scenario} Revenue post-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Revenue (USD)",
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Percentage": {
            "total": total_percentage,
            "title": f"{scenario} Pan HPE FLGM% post-rebate by{segment}Segment",
            "hover": "%{label}: %{value:,.2f}%<extra></extra>",
            "text": "%{y:.2f}%",
            "yaxis_prefix": "",
            "yaxis_title": "Percentage (%)",
            "total_label": lambda t: f"<b>Total: {t:.2f}%</b>"
        }
    }

    # Get config from graph_type
    cfg = config[graph_type]
    total = cfg["total"]
    graph_title = cfg["title"]
    hover_template = cfg["hover"]
    texttemplate = cfg["text"]
    yaxis_prefix = cfg["yaxis_prefix"]
    yaxis_title = cfg["yaxis_title"]
    total_label = cfg["total_label"](total)

    # Create graph
    fig = px.bar(
        filtered_plot_df,
        x='Category',
        y=graph_type,
        title=graph_title,
        text_auto='.3s',
        color="Category",
        color_discrete_map=colors
    )

    fig.update_traces(
        texttemplate=texttemplate,
        textposition='outside',
        cliponaxis=False,
        meta=dict(graph_type=graph_type),
        hovertemplate=hover_template
    )

    # Add total to legend
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=total_label,
        legendgroup='total',
    ))

    # Layout
    fig.update_layout(
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        margin=margins,
        title_font=dict(size=20)
    )

    # Y axis
    fig.update_yaxes(
        tickprefix=yaxis_prefix,
        title_text=yaxis_title
    )

    # Save fig in session_state
    st.session_state[f'fig_{chart_key}'] = fig

    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG, key=f"plot_{chart_key}")

    return fig

def rebate_pie_graph_generation(df, colors, margins, graph_type,scenario,segment):
    # Generar chart_key automáticamente
    chart_key = f"{scenario}_{graph_type}_{segment}_{graph_type}_{margins}".replace(" ", "_")

    total_revenue = df.loc[df['Category'] == 'Pan HPE', ['Revenue']].values[0].item()

    filtered_plot_df = df.drop(df[df['Category'] == 'Pan HPE'].index)

    if segment.strip() == "Product":
        filtered_plot_df = filtered_plot_df.drop(filtered_plot_df[filtered_plot_df['Category'] == 'Total Services'].index)
        total_revenue = df.loc[df['Category'] == 'Total Product', ['Revenue']].values[0].item()
    elif segment.strip() == "Service":
        filtered_plot_df = filtered_plot_df.drop(filtered_plot_df[filtered_plot_df['Category'] == 'Total Product'].index)
        total_revenue = df.loc[df['Category'] == 'Total Services', ['Revenue']].values[0].item()
    elif segment == "A&PS Only":
        return None
    # No pie graph for Percentage
    if graph_type == 'Percentage':
        return None

    # Config by graph type
    config = {
        "Revenue": {
            "title": f"{scenario}{segment}Revenue post-rebate Distribution",
            "hover": "<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total": total_revenue,
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        }
    }
  

    cfg = config[graph_type]
    total_label = cfg["total_label"](cfg["total"])
   

    # Create graph
    fig = px.pie(
        filtered_plot_df,
        values=graph_type,
        names='Category',
        hole=0.5,
        title=cfg["title"],
        color='Category',
        color_discrete_map=colors
    )

    fig.update_traces(
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='horizontal',
        textfont=dict(weight="bold"),
        hovertemplate=cfg["hover"]
    )

    # Add total at the end of the legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=0),
        showlegend=True,
        name=total_label,
        legendgroup='total',
    ))

    fig.update_layout(
        margin=margins,
        uniformtext=dict(minsize=10, mode='hide'),
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center'},
        title_font=dict(size=20)
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Save fig in session_state
    st.session_state[f'fig_{chart_key}'] = fig

    st.plotly_chart(fig, width='stretch', config=PLOTLY_CONFIG, key=f"plot_{chart_key}")
    
    return fig

def rebate_graph_type_selector(filtered_plot_df,chart_type,graph_type,scenario,segment):

    # Graph colors
    colors = get_color_map(filtered_plot_df)
    # Graph margins
    margins = dict(l=100, r=30, t=80, b=80)

    # Normalize for graph title
    if segment == "All":
        segment = " "
    elif segment == "Products Only":
        segment = " Product "
    elif segment == "Services Only":
        segment = " Service "

    if chart_type == "Bar Charts":
        fig = rebate_bar_graph_generation(filtered_plot_df,colors,margins,graph_type,scenario,segment)
    elif chart_type == "Donut Charts":
        fig= rebate_pie_graph_generation(filtered_plot_df,colors,margins,graph_type,scenario,segment)
    else:
        fig = None
    
    return fig  # Add this line to return the figure

