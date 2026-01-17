import streamlit as st 
from PIL import Image
from functions.processing import local_css,dynamic_options_selector, load_data, resource_path,view_option_select
from functions.graphicator import graph_type_selector,table_generation,rebate_graph_type_selector
from functions.download import save_individual_chart, save_all_charts_zip_button, render_export_buttons

icon_path = resource_path("assets/HPE_icon.webp")

# Initialize session state for figures
if 'figures' not in st.session_state:
    st.session_state.figures = {}

# Page configuration 
st.set_page_config(
    page_title="HPE GreenLake Finance Analytics v0.3",
    page_icon = Image.open(icon_path),
    layout="wide"
)

# Apply CSS styles
local_css("style.css")
    
# Main interface
st.title("HPE GreenLake Finance Analytics")

# File upload section
st.markdown("### 1. Data Ingestion")
uploaded_file = st.file_uploader("Upload your All Reports Excel file", type=["xlsx"])

if uploaded_file:
    try:
        
        # Load Excel file to memory
        day1_df,growth_df,sales_motion,day1_rebate,growth_rebate = load_data(uploaded_file)

        st.markdown("#### Model Summary")
        st.info(f"Sales Motion: {sales_motion}")
        
        # Visualization
        st.write("### 2. Financial Analysis Breakdown")

        # Switch between Day 1 and Growth scenarios
        scenario_option = st.selectbox("Select Sceneario", ["Day 1","Growth"])

        # Track changes and clear figures when needed
        if 'previous_scenario' not in st.session_state:
            st.session_state.previous_scenario = scenario_option
        if 'previous_view' not in st.session_state:
            st.session_state.previous_view = None
        if 'previous_chart_type' not in st.session_state:
            st.session_state.previous_chart_type = None

        if scenario_option == "Day 1":
            results_df = day1_df
            rebate_df = day1_rebate
            
        elif scenario_option == "Growth":
            results_df = growth_df
            rebate_df = growth_rebate
          
        # Select Segments view
        available_options = dynamic_options_selector(results_df)

        col_filter1, col_filter2 = st.columns([4, 1])

        with col_filter1:
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                view_option = st.selectbox("Select View", available_options)
            with sub_col2:
                chart_type = st.selectbox("Chart Style",["Bar Charts","Donut Charts"])

        with col_filter2:
            st.write("")  # Spacer
            st.write("")  # Extra spacer to align
            # Create placeholder for ZIP button
            zip_button_placeholder = st.empty()

        st.markdown("---")

        # Filter logic for the graphs and table
        filtered_plot_df,filtered_table_df,total_cost, total_revenue,total_margin,total_percentage= view_option_select(view_option,results_df)

        # Clear figures when any filter changes
        if (st.session_state.previous_scenario != scenario_option or 
            st.session_state.previous_view != view_option or 
            st.session_state.previous_chart_type != chart_type):
            st.session_state.figures = {}
            st.session_state.previous_scenario = scenario_option
            st.session_state.previous_view = view_option
            st.session_state.previous_chart_type = chart_type

        # Graphs Grid Layout 2x2
        if not filtered_table_df.empty:

            # Row 1
            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                fig, filename = graph_type_selector(filtered_plot_df,chart_type,'Cost',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)
                st.session_state.figures['cost'] = {'fig': fig, 'filename': filename}
                save_individual_chart('cost', st.session_state.figures['cost'])
            
            with row1_col2:
                fig, filename = graph_type_selector(filtered_plot_df,chart_type,'Revenue',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)
                st.session_state.figures['revenue'] = {'fig': fig, 'filename': filename}
                save_individual_chart('revenue', st.session_state.figures['revenue'])

            # Row 2
            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                fig, filename = graph_type_selector(filtered_plot_df,chart_type,'Margin',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)
                st.session_state.figures['margin_pre_rebate'] = {'fig': fig, 'filename': filename}
                save_individual_chart('margin_pre_rebate', st.session_state.figures['margin_pre_rebate'])

            with row2_col2:
                if sales_motion == "Indirect" and chart_type == "Donut Charts":
                    fig = rebate_graph_type_selector(rebate_df,chart_type,'Revenue',scenario_option,view_option)
                    if fig:
                        filename = f"{scenario_option}_Revenue_post_rebate_by{view_option.replace(' ', '_')}_Segment.png"
                        st.session_state.figures['revenue_post_rebate'] = {'fig': fig, 'filename': filename}
                        save_individual_chart('revenue_post_rebate', st.session_state.figures['revenue_post_rebate'])
                    
                else:
                    fig, filename = graph_type_selector(filtered_plot_df,chart_type,'Percentage',total_cost, total_revenue,total_margin,total_percentage,scenario_option,view_option)
                    st.session_state.figures['percentage'] = {'fig': fig, 'filename': filename}
                    save_individual_chart('percentage', st.session_state.figures['percentage'])

            # Row 3 if Indirect
            if sales_motion == "Indirect":
                row3_col1, row3_col2 = st.columns(2)

                with row3_col1:
                    if chart_type == "Bar Charts":
                        fig = rebate_graph_type_selector(rebate_df,chart_type,'Revenue',scenario_option,view_option)
                        if fig:
                            filename = f"{scenario_option}_Revenue_post_rebate_by{view_option.replace(' ', '_')}_Segment.png"
                            st.session_state.figures['revenue_post_rebate'] = {'fig': fig, 'filename': filename}
                            save_individual_chart('revenue_post_rebate', st.session_state.figures['revenue_post_rebate'])
                
                with row3_col2:
                    if chart_type == "Bar Charts":
                        fig = rebate_graph_type_selector(rebate_df,chart_type,'Percentage',scenario_option,view_option)
                        if fig:
                            filename = f"{scenario_option}_Percentage_post_rebate_by{view_option.replace(' ', '_')}_Segment.png"
                            st.session_state.figures['percentage_post_rebate'] = {'fig': fig, 'filename': filename}
                            save_individual_chart('percentage_post_rebate', st.session_state.figures['percentage_post_rebate'])
        
        # NOW populate the ZIP button after figures are generated
        with zip_button_placeholder.container():
            save_all_charts_zip_button(st.session_state.figures)

        # Summary Table
        st.write("### Data Summary")

        if not filtered_table_df.empty:
            html_table = table_generation(filtered_table_df)
        st.markdown(html_table, unsafe_allow_html=True)

        # Export buttons at the bottom
        st.write("### 3. Additional Exports")
        render_export_buttons()

    except Exception as e:
        st.error(f"Error:{e}")

else:
    st.warning("Awaiting file upload...")