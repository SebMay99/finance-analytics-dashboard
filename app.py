import streamlit as st 
import pandas as pd
from PIL import Image
import plotly.express as px
from processing import local_css, set_row_style

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
        processed_margin = [margin * 100 for margin in margins]
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
    
        # Visualization
        st.write("### 2.Financial Analysis Breakdown")
        view_option = st.selectbox("Select View", ["All","Products Only","Services Only","A&PS Only"])

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
                                 (results_df['Category'] != "Products+Services")]
            
            table_df = results_df

        # Remove $0 and 0%     
        filtered_plot_df = plot_df[(plot_df['Cost'] > 0) | (plot_df['Margin'] != 0)]
        filtered_table_df = table_df[(table_df['Cost'] > 0) | (table_df['Margin'] != 0)]

        #Graphs
        # Grid Layout 2x2
        if not filtered_table_df.empty:
            # Row 1
            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                fig_cost = px.bar(filtered_plot_df, x='Category', y='Cost', title="Cost by Segment", text_auto='.3s',
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
            
            with row1_col2:
                fig_cost = px.bar(filtered_plot_df, x='Category', y='Revenue', title="Revenue by Segment", text_auto='.3s',
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

            # Row 2
            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                fig_cost = px.bar(filtered_plot_df, x='Category', y='Margin', title="FLGM Pre-rebate by Segment", text_auto='.3s',
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
                fig_cost.update_yaxes(tickprefix="$", title_text="Margin(USD)")
                st.plotly_chart(fig_cost,width='stretch')
            
            with row2_col2:
                fig_cost = px.bar(filtered_plot_df, x='Category', y='Percentage', title="FLGM% Pre-rebate by Segment", text_auto= '.2f',
                                color_discrete_sequence=['#01a982'])
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
