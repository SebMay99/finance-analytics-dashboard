import streamlit as st 

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
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
