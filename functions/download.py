import streamlit as st 
import plotly.io as pio
import plotly.graph_objects as go
from io import BytesIO
from zipfile import ZipFile
from tkinter import Tk, filedialog
import sys
import os

# Diagnostic logging
print(f"=== Kaleido Diagnostic ===")
print(f"Python: {sys.executable}")

try:
    import kaleido
    print("Kaleido module imported")
    print(f"Kaleido file: {kaleido.__file__}")
    
    test_fig = go.Figure(data=[go.Bar(x=[1], y=[1])])
    test_img = pio.to_image(test_fig, format='png')
    print(f"SUCCESS: Kaleido working - generated {len(test_img)} bytes")
    KALEIDO_AVAILABLE = True
except Exception as e:
    print(f"KALEIDO FAILED: {e}")
    KALEIDO_AVAILABLE = False

print(f"=== End Diagnostic ===")


def generate_image_bytes(fig):
    """Generate PNG bytes from figure - cached in session state"""
    try:
        img_bytes = pio.to_image(fig, format='png', width=1400, height=800, scale=2)
        return img_bytes
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None


def save_file_with_dialog(data, default_filename):
    """Opens native save dialog and saves file"""
    try:
        root = Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=os.path.splitext(default_filename)[1],
            initialfile=default_filename,
            filetypes=[
                ("PNG Image", "*.png"),
                ("All Files", "*.*")
            ],
            title="Save chart as..."
        )
        
        root.destroy()
        
        if filepath:
            with open(filepath, 'wb') as f:
                f.write(data)
            return True, filepath
        return False, None
    except Exception as e:
        return False, str(e)


def handle_save_chart(key, chart_data):
    """Callback function to handle save without visible rerun"""
    img_bytes = generate_image_bytes(chart_data['fig'])
    
    if img_bytes:
        success, result = save_file_with_dialog(img_bytes, chart_data['filename'])
        if success:
            st.session_state[f'save_message_{key}'] = f"✅ Saved to: {os.path.basename(result)}"
            print(f"Saved {chart_data['filename']} to {result}")
        elif result:
            st.session_state[f'save_message_{key}'] = f"❌ Error: {result}"
        else:
            st.session_state[f'save_message_{key}'] = "ℹ️ Save cancelled"
    else:
        st.session_state[f'save_message_{key}'] = "❌ Failed to generate image"


def save_individual_chart(key, chart_data):
    """Render individual download button below a chart"""
    if not KALEIDO_AVAILABLE:
        return
    
    label = key.replace('_', ' ').title()
    
    # Show message if exists
    if f'save_message_{key}' in st.session_state:
        message = st.session_state[f'save_message_{key}']
        
        if '✅' in message:
            st.toast(message.replace('✅ ', ''), icon="✅")
        elif '❌' in message:
            st.toast(message.replace('❌ ', ''), icon="❌")
        elif 'ℹ️' in message:
            st.toast(message.replace('ℹ️ ', ''), icon="ℹ️")
        
        del st.session_state[f'save_message_{key}']
    
    st.button(
        f"💾 Save {label} Chart", 
        key=f"save_{key}", 
        use_container_width=True, 
        type="secondary",
        on_click=handle_save_chart,
        args=(key, chart_data)
    )


def handle_save_all_zip(figures_dict):
    """Callback function to handle ZIP save without visible rerun"""
    if not KALEIDO_AVAILABLE or not figures_dict:
        st.session_state['zip_message'] = "⚠️ No charts available"
        return
    
    try:
        # Create ZIP
        zip_buffer = BytesIO()
        
        with ZipFile(zip_buffer, 'w') as zf:
            for key, data in figures_dict.items():
                img_bytes = generate_image_bytes(data['fig'])
                if img_bytes:
                    zf.writestr(data['filename'], img_bytes)
                    print(f"Added {data['filename']} to ZIP")
        
        zip_data = zip_buffer.getvalue()
        print(f"ZIP created: {len(zip_data)} bytes with {len(figures_dict)} files")
        
        # Save with dialog
        root = Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile="financial_charts.zip",
            filetypes=[("ZIP Archive", "*.zip"), ("All Files", "*.*")],
            title="Save all charts as..."
        )
        
        root.destroy()
        
        if filepath:
            with open(filepath, 'wb') as f:
                f.write(zip_data)
            st.session_state['zip_message'] = f"✅ ZIP saved: {os.path.basename(filepath)}"
            print(f"Saved ZIP to {filepath}")
        else:
            st.session_state['zip_message'] = "ℹ️ Save cancelled"
            
    except Exception as e:
        st.session_state['zip_message'] = "❌ Error creating ZIP"
        print(f"ZIP error: {str(e)}")


def save_all_charts_zip_button(figures_dict):
    """Render ZIP download button with callback"""
    
    # Show and clear message if exists (before button render)
    if 'zip_message' in st.session_state:
        message = st.session_state['zip_message']
        
        if '✅' in message:
            st.toast(message.replace('✅ ', ''), icon="✅")
        elif '❌' in message:
            st.toast(message.replace('❌ ', ''), icon="❌")
        elif 'ℹ️' in message:
            st.toast(message.replace('ℹ️ ', ''), icon="ℹ️")
        elif '⚠️' in message:
            st.toast(message.replace('⚠️ ', ''), icon="⚠️")
        
        del st.session_state['zip_message']
    
    # Render button with unique key
    st.button(
        "Save All (ZIP)", 
        key="save_all_zip_btn",
        use_container_width=True, 
        type="primary",
        on_click=handle_save_all_zip,
        args=(figures_dict,)
    )


def render_export_buttons():
    """Render PPT and PDF export buttons at the bottom"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.button(
            "Export to PowerPoint",
            disabled=True,
            use_container_width=True,
            key="export_ppt",
            help="Feature coming soon",
            type="primary"
        )
    
    with col2:
        st.button(
            "Export to PDF",
            disabled=True,
            use_container_width=True,
            key="export_pdf",
            help="Feature coming soon",
            type="primary"
        )