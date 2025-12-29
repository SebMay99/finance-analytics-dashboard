import streamlit as st 
import pandas as pd
from PIL import Image
import plotly.express as px
from processing import local_css, set_row_style, get_color_map, dynamic_options_selector, load_data

# Page configuration 
st.set_page_config(
    page_title="HPE GreenLake Finance Analytics",
    page_icon = Image.open("assets/HPE_icon.png"),
    layout="wide"
)

# Apply CSS styles
local_css("style.css")

# Sidebar
# with st.sidebar:
#    st.image(Image.open("assets/HPE-logo-2025.png"), width=120)
#    st.title("Navigation")
#    st.markdown("---")
#    st.info("Log in to access advanced features")

    
# Main interface
st.title("HPE GreenLake Finance Analytics")

# File upload section
st.markdown("### 1.Data Ingestion")
uploaded_file = st.file_uploader("Upload your All Reports Excel file", type=["xlsx"])

if uploaded_file:
    try:
        results_df = load_data(uploaded_file)
        available_options = dynamic_options_selector(results_df)

        # Visualization
        st.write("### 2.Financial Analysis Breakdown")

        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            view_option = st.selectbox("Select View", available_options)

        with col_filter2:
            chart_type = st.selectbox("Chart Style",["Bar Charts","Donut Charts"])

        product_cats = ["HPC-AI","Compute","Storage","Software","3P/OEM"]
        service_cats = ["Installation","Support", "Complete Care","Managed Services",
                        "Colo","3PP Product","3PP Support","SaaS","SW Services",
                        "Ezmeral"]
        aps_cats = ["A&PS","A&PS 3PP","A&PS Colo"]

        # Filter logic for the graphs
        if view_option == "Products Only":
            plot_df = results_df[results_df['Category'].isin(product_cats)]
            table_df = results_df[results_df['Category'].isin(product_cats + ["Total Product"])]
        elif view_option == "Services Only":
            plot_df = results_df[results_df['Category'].isin(service_cats)]
            table_df = results_df[results_df['Category'].isin(service_cats + ["Total Services"])]
        elif view_option == "A&PS Only":
            plot_df = results_df[results_df['Category'].isin(aps_cats)]
            table_df = results_df[results_df['Category'].isin(aps_cats + ["Total A&PS"])]
        else:
            plot_df = results_df[(results_df['Category'] != "Total Product") & 
                                 (results_df['Category'] != "Total Services") & 
                                 (results_df['Category'] != "Total A&PS") & 
                                 (results_df['Category'] != "Pan HPE") &
                                 (results_df['Category'] != "Total Products+Services")]
            
            table_df = results_df

        # Remove $0 and 0%     
        filtered_plot_df = plot_df[(plot_df['Cost'] > 0) | (plot_df['Margin'] != 0)]
        filtered_table_df = table_df[(table_df['Cost'] > 0) | (table_df['Margin'] != 0)]

        #Graphs
        # Grid Layout 2x2
        if not filtered_table_df.empty:

            # Graph colors
            colors = get_color_map(filtered_plot_df,product_cats,service_cats,aps_cats)

            # Graph margins
            margins = dict(l=40, r=0, t=80, b=80)

            # Row 1
            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                # Bar Chart:
                if chart_type == "Bar Charts":
                    fig_cost = px.bar(filtered_plot_df, x='Category', y='Cost', title="Cost by Segment", text_auto='.3s',
                                    color="Category",color_discrete_map=colors)
                    fig_cost.update_traces(
                        texttemplate='$%{y:,.2s}',
                        textposition='outside',
                        cliponaxis = False,
                        hovertemplate="<b>%{label}</b><br>Cost: $%{value:,.2f}<extra></extra>"
                    )
                # Pie Chart
                else: 
                    fig_cost = px.pie(filtered_plot_df, values='Cost', names='Category', hole=0.5,title="Cost Distribution",
                                      color='Category', color_discrete_map=colors)
                    fig_cost.update_traces(textinfo='percent+label',
                                           textposition='inside',
                                           insidetextorientation='horizontal',
                                           textfont=dict(
                                               weight="bold"
                                           ),
                                           hovertemplate="<b>%{label}</b><br>Cost: $%{value:,.2f}<extra></extra>"
                                           )
                    fig_cost.update_layout(   uniformtext=dict(
                                               minsize=8,
                                               mode='hide'
                                           )
                                           )
                fig_cost.update_layout(title={
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        }, 
                        margin=margins,
                        title_font=dict(size=20))
                fig_cost.update_yaxes(tickprefix="$", title_text="Cost (USD)")
                st.plotly_chart(fig_cost,width='stretch')
            
            with row1_col2:
                # Bar Chart
                if chart_type == "Bar Charts":
                    fig_cost = px.bar(filtered_plot_df, x='Category', y='Revenue', title="Revenue by Segment", text_auto='.3s',
                                    color="Category",color_discrete_map=colors)
                    fig_cost.update_traces(
                        texttemplate='$%{y:,.2s}',
                        textposition='outside',
                        cliponaxis = False,
                        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<extra></extra>"
                    )
                else: 
                    fig_cost = px.pie(filtered_plot_df, values='Revenue', names='Category', hole=0.5,title="Revenue Distribution",
                                      color='Category', color_discrete_map=colors)
                    fig_cost.update_traces(textinfo='percent+label',
                                           textposition='inside',
                                           insidetextorientation='horizontal',
                                           textfont=dict(
                                               weight="bold"
                                           ),
                                           hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<extra></extra>"
                                           )
                    fig_cost.update_layout(   uniformtext=dict(
                                               minsize=8,
                                               mode='hide'
                                           )
                                           )
                fig_cost.update_layout(title={
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                    }, 
                    margin=margins,
                    title_font=dict(size=20))
                fig_cost.update_yaxes(tickprefix="$", title_text="Revenue (USD)")
                st.plotly_chart(fig_cost,width='stretch')

            # Row 2
            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                # Bar Chart:
                if chart_type == "Bar Charts":
                    fig_cost = px.bar(filtered_plot_df, x='Category', y='Margin', title="FLGM Pre-rebate by Segment", text_auto='.3s',
                                    color="Category",color_discrete_map=colors)
                    fig_cost.update_traces(
                        texttemplate='$%{y:,.2s}',
                        textposition='outside',
                        cliponaxis = False,
                        hovertemplate="<b>%{label}</b><br>Margin: $%{value:,.2f}<extra></extra>"
                    )
                else: 
                    fig_cost = px.pie(filtered_plot_df, values='Margin', names='Category', hole=0.5,title="Margin Distribution",
                                      color='Category', color_discrete_map=colors)
                    fig_cost.update_traces(textinfo='percent+label',
                                           textposition='inside',
                                           insidetextorientation='horizontal',
                                           textfont=dict(
                                               weight="bold"
                                           ),
                                           hovertemplate="<b>%{label}</b><br>Margin: $%{value:,.2f}<extra></extra>"
                                           )
                    fig_cost.update_layout(   uniformtext=dict(
                                               minsize=8,
                                               mode='hide'
                                           )
                                           )
                fig_cost.update_layout(title={
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                    }, 
                    margin=margins,
                    title_font=dict(size=20))
                fig_cost.update_yaxes(tickprefix="$", title_text="Margin(USD)")
                st.plotly_chart(fig_cost,width='stretch')
            
            with row2_col2:
                # Bar Chart only
                if chart_type == "Bar Charts":
                    fig_cost = px.bar(filtered_plot_df, x='Category', y='Percentage', title="FLGM% Pre-rebate by Segment", text_auto= '.2f',
                                    color="Category",color_discrete_map=colors)
                    fig_cost.update_traces(
                        texttemplate='%{y:,.2s}%',
                        textposition='outside',
                        cliponaxis = False,
                        hovertemplate="<b>%{label}</b><br>FLGM%: %{value:,.2f}%<extra></extra>"
                    )
                    fig_cost.update_layout(title={
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                        }, 
                        margin=margins,
                        title_font=dict(size=20))
                    fig_cost.update_yaxes(ticksuffix="%", title_text="Margin (%)")
                    st.plotly_chart(fig_cost,width='stretch')


        # Summary Table
        st.write("### Data Summary")

        if not filtered_table_df.empty:
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


        st.markdown(html_table, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error:{e}")

else:
    st.warning("Awaiting file upload...")
