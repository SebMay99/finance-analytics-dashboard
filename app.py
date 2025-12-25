import streamlit as st 
import pandas as pd
from PIL import Image
import plotly.express as px
from processing import local_css, set_row_style

# Page configuration 
st.set_page_config(
    page_title="HPE GreenLake Model Analyzer",
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
st.title("Financial Model Analytics")
st.write("Professional Automation Tool for Solution Architects")

# File upload section
st.markdown("### 1.Data Ingestion")
uploaded_file = st.file_uploader("Upload your All Reports Excel file", type=["xlsx"])

if uploaded_file:
    try:
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
        costs = df.iloc[44, 1:18].tolist()
        revenues = df.iloc[42, 1:18].tolist()
        margins = df.iloc[46, 1:18].tolist()

        # Data Transformation
        processed_costs = [cost * 1000 for cost in costs]
        processed_revenue = [revenue * 1000 for revenue in revenues]
        processed_margin = [margin * 100 for margin in margins]

        data = {
            "Category": ["HPC-AI","Compute","Storage","Software","3P/OEM","Total Product","Installation","Support",
                         "Complete Care","Managed Services","Colo","3PP Product","3PP Support","SaaS","SW Services",
                         "Ezmeral","Total Services"],
            "Cost": processed_costs,
            "Revenue": processed_revenue,
            "Margin": processed_margin
        }

        results_df = pd.DataFrame(data)
    
        # Visualization
        st.write("### 2.Financial Analysis Breakdown")
        view_option = st.selectbox("Select View", ["All","Products Only","Services Only"])

        product_cats = ["HPC-AI","Compute","Storage","Software","3P/OEM"]
        service_cats = ["Installation","Support", "Complete Care","Managed Services",
                        "Colo","3PP Product","3PP Support","SaaS","SW Services",
                        "Ezmeral"]

        # Filter logic for the graphs
        if view_option == "Products Only":
            plot_df = results_df[results_df['Category'].isin(product_cats)]
            table_df = results_df[results_df['Category'].isin(product_cats + ["Total Product"])]
        elif view_option == "Services Only":
            plot_df = results_df[results_df['Category'].isin(service_cats)]
            table_df = results_df[results_df['Category'].isin(service_cats + ["Total Services"])]
        else:
            plot_df = results_df[(results_df['Category'] != "Total Product") & (results_df['Category'] != "Total Services")]
            table_df = results_df

        # Remove $0 and 0%     
        filtered_plot_df = plot_df[(plot_df['Cost'] > 0) | (plot_df['Margin'] != 0)]
        filtered_table_df = table_df[(table_df['Cost'] > 0) | (table_df['Margin'] != 0)]

        #Graphs
        col1, col2, col3 = st.columns(3)

        with col1:
            fig_cost = px.bar(filtered_plot_df, x='Category', y='Cost', title="Total Cost by Segment", text_auto='.3s',
                              color_discrete_sequence=['#01a982'])
            fig_cost.update_traces(
                texttemplate='$%{y:,.2s}',
                textposition='outside',
                cliponaxis = False
            )
            fig_cost.update_layout(title={
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                }, 
                margin=dict(l=60, r=20, t=80, b=40),
                title_font=dict(size=20))
            fig_cost.update_yaxes(tickprefix="$", title_text="Cost (USD)")
            st.plotly_chart(fig_cost,width='stretch')
        
        with col2:
            fig_cost = px.bar(filtered_plot_df, x='Category', y='Revenue', title="Total Revenue by Segment", text_auto='.3s',
                              color_discrete_sequence=['#01a982'])
            fig_cost.update_traces(
                texttemplate='$%{y:,.2s}',
                textposition='outside',
                cliponaxis = False
            )
            fig_cost.update_layout(title={
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
                }, 
                margin=dict(l=60, r=20, t=80, b=40),
                title_font=dict(size=20))
            fig_cost.update_yaxes(tickprefix="$", title_text="Revenue (USD)")
            st.plotly_chart(fig_cost,width='stretch')

        with col3:
            fig_cost = px.bar(filtered_plot_df, x='Category', y='Margin', title="Total Margin by Segment", text_auto= '.2f',
                              color_discrete_sequence=['#004777'])
            fig_cost.update_traces(
                texttemplate='%{y:,.2s}%',
                textposition='outside',
                cliponaxis = False
            )
            fig_cost.update_layout(title={
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
                }, 
                margin=dict(l=60, r=20, t=80, b=40),
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
                    "Margin": "{:,.2f}%"
                })
                .hide(axis='index')
                .to_html()
            )

        st.markdown(html_table, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error:{e}")

else:
    st.warning("Awaiting file upload...")
