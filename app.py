import streamlit as st 
from PIL import Image
from functions.processing import local_css,dynamic_options_selector, load_data, resource_path,view_option_select
from functions.graphicator import graph_type_selector,table_generation

icon_path = resource_path("assets/HPE_icon.webp")

# Page configuration 
st.set_page_config(
    page_title="HPE GreenLake Finance Analytics v0.3",
    page_icon = Image.open(icon_path),
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
        
        # Load Excel file to memory
        day1_df,growth_df = load_data(uploaded_file)

        # Visualization
        st.write("### 2.Financial Analysis Breakdown")

        # Switch between Day 1 and Growth scenarios
        scenario_option = st.selectbox("Select Sceneario", ["Day 1","Growth"])
        if scenario_option == "Day 1":
            results_df = day1_df
        elif scenario_option == "Growth":
            results_df = growth_df

        # Select Segments view
        available_options = dynamic_options_selector(results_df)

        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            view_option = st.selectbox("Select View", available_options)

        with col_filter2:
            chart_type = st.selectbox("Chart Style",["Bar Charts","Donut Charts"])

        # Filter logic for the graphs and table
        filtered_plot_df,filtered_table_df,total_cost, total_revenue,total_margin,total_percentage= view_option_select(view_option,results_df)

        #Graphs
        # Grid Layout 2x2
        if not filtered_table_df.empty:

            # Row 1
            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                graph_type_selector(filtered_plot_df,chart_type,'Cost',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)
            
            with row1_col2:
                graph_type_selector(filtered_plot_df,chart_type,'Revenue',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)

            # Row 2
            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                graph_type_selector(filtered_plot_df,chart_type,'Margin',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)
        
            with row2_col2:
                graph_type_selector(filtered_plot_df,chart_type,'Percentage',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)
                    
        # Summary Table
        st.write("### Data Summary")

        if not filtered_table_df.empty:
            html_table = table_generation(filtered_table_df)
        st.markdown(html_table, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error:{e}")

else:
    st.warning("Awaiting file upload...")
