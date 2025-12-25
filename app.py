import streamlit as st 
import pandas as pd
from PIL import Image
import plotly.express as px

# Page configuration 
st.set_page_config(
    page_title="HPE GreenLake Model Analyzer",
    page_icon = Image.open("assets/HPE_icon.png"),
    layout="wide"
)

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
            "Category": ["HPC-AI","Compute","Storage","Software","3P/OEM","Product","Installation","Support",
                         "Complete Care","Managed Services","Colo","3PP Product","3PP Support","SaaS","SW Services",
                         "Ezmeral","Services"],
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
        elif view_option == "Services Only":
            plot_df = results_df[results_df['Category'].isin(service_cats)]
        else:
            plot_df = results_df[(results_df['Category'] != "Product") & (results_df['Category'] != "Services")]
        
        filtered_plot_df = plot_df[(plot_df['Cost'] > 0) | (plot_df['Margin'] != 0)]
        
        col1, col2, col3 = st.columns(3)

        with col1:
            fig_cost = px.bar(filtered_plot_df, x='Category', y='Cost', title="Total Cost by Segment", text_auto='.3s',
                              color_discrete_sequence=['#01a982'])
            fig_cost.update_yaxes(tickprefix="$", title_text="Amount (USD)")
            st.plotly_chart(fig_cost,use_container_width=True)
        
        with col2:
            fig_cost = px.bar(filtered_plot_df, x='Category', y='Revenue', title="Total Revenue by Segment", text_auto='.3s',
                              color_discrete_sequence=['#01a982'])
            fig_cost.update_yaxes(tickprefix="$", title_text="Amount (USD)")
            st.plotly_chart(fig_cost,use_container_width=True)

        with col3:
            fig_cost = px.bar(filtered_plot_df, x='Category', y='Margin', title="Total Margin by Segment", text_auto= '.2f',
                              color_discrete_sequence=['#004777'])
            fig_cost.update_yaxes(ticksuffix="%", title_text="Margin (%)")
            st.plotly_chart(fig_cost,use_container_width=True)

        # Summary Table
        st.write("### Data Summary")
        st.table(filtered_plot_df.style.format({"Cost": "${:,.2f}","Revenue": "${:,.2f}", "Margin": "{:,.2f}%"}))

    except Exception as e:
        st.error(f"Error:{e}")

else:
    st.warning("Awaiting file upload...")
