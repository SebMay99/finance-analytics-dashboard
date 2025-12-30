import streamlit as st 
import pandas as pd
import sys
import os

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

def get_color_map(df,product_cats,service_cats,aps_cats):
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
        else:
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
