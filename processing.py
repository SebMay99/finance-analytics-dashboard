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
