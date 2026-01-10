import streamlit as st 
import plotly.express as px
import pandas as pd
import sys
import os
import plotly.graph_objects as go

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Load CSS
def local_css(file_name):
    with open(resource_path(file_name)) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

    product_cats = ["HPC-AI","Compute","Storage","Software","3P/OEM"]
    service_cats = ["Installation","Support", "Complete Care","Managed Services",
                    "Colo","3PP Product","3PP Support","SaaS","SW Services",
                    "Ezmeral"]
    aps_cats = ["A&PS","A&PS 3PP","A&PS Colo"]


    color_map = {}
    # Color scales
    greens = ["#01A982", "#05CC93", "#00E0AF", "#00B88A", "#009F73"]
    blues = ["#0070F8", "#35CFF0", "#62D8F6", "#0094FF", "#0AB3D9",
         "#1A8FE0", "#4AC2FF", "#0082CC", "#2BB0E8", "#5FC7FF"]
    purples = ["#7764FC", "#8A6BFF", "#A07AFF"]

    g_idx, y_idx, p_idx = 0, 0, 0

    for cat in df['Category'].unique():
        if cat in product_cats:
            color_map[cat] = greens[g_idx % len(greens)]
            g_idx += 1
        elif cat in service_cats:
            color_map[cat] = blues[y_idx % len(blues)]
            y_idx += 1
        elif cat in aps_cats:
            color_map[cat] = purples[p_idx % len(purples)]
            p_idx += 1
        
    return color_map

def dynamic_options_selector(results_df):
    # Check if product 
    prod_total_row = results_df[results_df['Category'] == 'Total Product']
    total_prod_cost = prod_total_row['Cost'].values[0] if not prod_total_row.empty else 0

    # Check if services
    serv_total_row = results_df[results_df['Category'] == 'Total Services']
    total_serv_cost = serv_total_row['Cost'].values[0] if not serv_total_row.empty else 0

    # Check if aps 
    aps_total_row = results_df[results_df['Category'] == 'Total A&PS']
    total_aps_cost = aps_total_row['Cost'].values[0] if not aps_total_row.empty else 0

    #Dinamic options list
    available_options =["All"]

    if total_prod_cost > 0:
        available_options.append("Products Only")

    if total_serv_cost > 0:
        available_options.append("Services Only")

    if total_aps_cost > 0:
        available_options.append("A&PS Only")

    return available_options

@st.cache_data # Cache the Excel file
def load_data(uploaded_file):
    # Load the All Reports as a DF and Check if it's a custom file
    try:
        sheet_name = "PL_MGMT Edit"
        df = pd.read_excel(uploaded_file,sheet_name=sheet_name, engine='openpyxl')
        st.success("Custom File Loaded")
    
    except:
        sheet_name = "PL_MGMT"
        df = pd.read_excel(uploaded_file,sheet_name=sheet_name, engine='openpyxl')
        st.success("File Loaded")

    # Cell Mapping for Day 1 financial information
    costs = df.iloc[44, 1:24].tolist()
    revenues = df.iloc[42, 1:24].tolist()
    margins = df.iloc[45, 1:24].tolist()
    percentages = df.iloc[46, 1:24].tolist()

    # Data Transformation
    processed_costs = [cost * 1000 for cost in costs]
    processed_revenue = [revenue * 1000 for revenue in revenues]
    processed_margin = [margin * 1000 for margin in margins]
    processed_margin_percentage = [percentage * 100 for percentage in percentages]

    data = {
        "Category": ["HPC-AI","Compute","Storage","Software","3P/OEM","Total Product","Installation","Support",
                        "Complete Care","Managed Services","Colo","3PP Product","3PP Support","SaaS","SW Services",
                        "Ezmeral","Total Services","Total Products+Services","A&PS","A&PS 3PP","A&PS Colo","Total A&PS","Pan HPE"],
        "Cost": processed_costs,
        "Revenue": processed_revenue,
        "Margin": processed_margin,
        "Percentage": processed_margin_percentage
    }

    results_df = pd.DataFrame(data)
    return results_df

def view_option_select(view_option,results_df,product_cats,service_cats,aps_cats):
    # Filter logic for the graphs
    if view_option == "Products Only":
        plot_df = results_df[results_df['Category'].isin(product_cats)]
        table_df = results_df[results_df['Category'].isin(product_cats + ["Total Product"])]

        total_cost = table_df[table_df['Category'] == 'Total Product']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total Product']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total Product']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total Product']['Percentage'].values[0]

    elif view_option == "Services Only":
        plot_df = results_df[results_df['Category'].isin(service_cats)]
        table_df = results_df[results_df['Category'].isin(service_cats + ["Total Services"])]

        total_cost = table_df[table_df['Category'] == 'Total Services']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total Services']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total Services']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total Services']['Percentage'].values[0]

    elif view_option == "A&PS Only":
        plot_df = results_df[results_df['Category'].isin(aps_cats)]
        table_df = results_df[results_df['Category'].isin(aps_cats + ["Total A&PS"])]

        total_cost = table_df[table_df['Category'] == 'Total A&PS']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total A&PS']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total A&PS']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total A&PS']['Percentage'].values[0]
        

    else:
        plot_df = results_df[(results_df['Category'] != "Total Product") & 
                                (results_df['Category'] != "Total Services") & 
                                (results_df['Category'] != "Total A&PS") & 
                                (results_df['Category'] != "Pan HPE") &
                                (results_df['Category'] != "Total Products+Services")]
        
        table_df = results_df

        total_cost = table_df[table_df['Category'] == 'Pan HPE']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Pan HPE']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Pan HPE']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Pan HPE']['Percentage'].values[0]

    # Remove $0 and 0%     
    filtered_plot_df = plot_df[(plot_df['Cost'] > 0) | (plot_df['Margin'] != 0)]
    filtered_table_df = table_df[(table_df['Cost'] > 0) | (table_df['Margin'] != 0)]
    return filtered_plot_df,filtered_table_df,total_cost, total_revenue,total_margin,total_percentage

def graph_type_selector(filtered_plot_df,chart_type,graph_type,total_cost, 
                        total_revenue,total_margin,total_percentage):
    # Graph colors
    colors = get_color_map(filtered_plot_df)

    # Graph margins
    margins = dict(l=100, r=30, t=80, b=80)

    if chart_type == "Bar Charts":
        bar_graph_generation(filtered_plot_df,colors,margins,graph_type,
                             total_cost, total_revenue,total_margin,total_percentage)
    elif chart_type == "Donut Charts":
        pie_graph_generation(filtered_plot_df,colors,margins,graph_type,
                             total_cost, total_revenue,total_margin)

def bar_graph_generation(filtered_plot_df,colors,margins,graph_type,
                         total_cost, total_revenue,total_margin,total_percentage):
    
    # Config by type of graph
    config = {
        "Cost": {
            "total": total_cost,
            "title": "Cost by Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Cost (USD)",
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Margin": {
            "total": total_margin,
            "title": "Pan HPE FLGM Pre-rebate by Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Margin (USD)",
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Revenue": {
            "total": total_revenue,
            "title": "Revenue by Segment",
            "hover": "%{label}: %{value:,.2f}<extra></extra>",
            "text": "$%{y:,.2f}",
            "yaxis_prefix": "$",
            "yaxis_title": "Revenue (USD)",
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Percentage": {
            "total": total_percentage,
            "title": "Pan HPE FLGM% Pre-rebate by Segment",
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

    st.plotly_chart(fig, width='stretch')
    return fig

def pie_graph_generation(filtered_plot_df, colors, margins, graph_type,
                         total_cost, total_revenue, total_margin):

    # No generar gráfico si es Percentage
    if graph_type == 'Percentage':
        return None

    # Configuración por tipo de gráfico
    config = {
        "Cost": {
            "title": "Cost Distribution",
            "hover": "<b>%{label}</b><br>Cost: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total": total_cost,
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Margin": {
            "title": "Pan HPE FLGM Pre-rebate Distribution",
            "hover": "<b>%{label}</b><br>Margin: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total": total_margin,
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        },
        "Revenue": {
            "title": "Revenue Distribution",
            "hover": "<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>% out of total: %{percent:.2%}<extra></extra>",
            "total": total_revenue,
            "total_label": lambda t: f"<b>Total: ${t:,.2f}</b>"
        }
    }


    cfg = config[graph_type]
    total_label = cfg["total_label"](cfg["total"])

    # Crear gráfico
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

    # Añadir total como elemento de leyenda
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
        uniformtext=dict(minsize=8, mode='hide'),
        title={'y': 0.95, 'x': 0.5, 'xanchor': 'center'}
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    st.plotly_chart(fig, width='stretch')

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

    # Reemplazar los encabezados en el HTML
    html_table = html_table.replace(">Cost<", ">Costs<") \
                        .replace(">Revenue<", ">Revenue<") \
                        .replace(">Margin<", ">FLGM Pre-rebate<")\
                        .replace(">Percentage<", ">FLGM% Pre-rebate<")\
                        
    return html_table
