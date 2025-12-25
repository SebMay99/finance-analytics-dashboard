import streamlit as st 

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def set_row_style(row):
    if "TOTAL" in str(row.Category).upper():
        return ['background-color: #01a982; color: white; font-weight: bold;'] * len(row)
    return [''] * len(row)
