import streamlit as st 
import pandas as pd
import sys
import os
from public import config

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Load CSS
def local_css(file_name):
    with open(resource_path(file_name)) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

def view_option_select(view_option,results_df):
    # Filter logic for the graphs
    if view_option == "Products Only":
        plot_df = results_df[results_df['Category'].isin(config.product_cats)]
        table_df = results_df[results_df['Category'].isin(config.product_cats + ["Total Product"])]

        total_cost = table_df[table_df['Category'] == 'Total Product']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total Product']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total Product']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total Product']['Percentage'].values[0]

    elif view_option == "Services Only":
        plot_df = results_df[results_df['Category'].isin(config.service_cats)]
        table_df = results_df[results_df['Category'].isin(config.service_cats + ["Total Services"])]

        total_cost = table_df[table_df['Category'] == 'Total Services']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total Services']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total Services']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total Services']['Percentage'].values[0]

    elif view_option == "A&PS Only":
        plot_df = results_df[results_df['Category'].isin(config.aps_cats)]
        table_df = results_df[results_df['Category'].isin(config.aps_cats + ["Total A&PS"])]

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
    
    # Don't show Total Products+Services in the table if there's no A&PS (Redudant)
    filtered_table_df = filtered_table_df[~(~filtered_table_df['Category'].eq('Total A&PS').any() & filtered_table_df['Category'].eq('Total Products+Services'))]

    #print(filtered_table_df)

    return filtered_plot_df,filtered_table_df,total_cost, total_revenue,total_margin,total_percentage

