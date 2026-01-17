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
    import traceback
    traceback.print_exc()
    KALEIDO_AVAILABLE = False

print(f"=== End Diagnostic ===")


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


def save_zip_with_dialog(data):
    """Opens native save dialog for ZIP file"""
    try:
        root = Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile="financial_charts.zip",
            filetypes=[
                ("ZIP Archive", "*.zip"),
                ("All Files", "*.*")
            ],
            title="Save all charts as..."
        )
        
        root.destroy()
        
        if filepath:
            with open(filepath, 'wb') as f:
                f.write(data)
            return True, filepath
        return False, None
    except Exception as e:
        return False, str(e)


def render_download_section(figures_dict):
    """
    Renders download section for saved figures
    """
    if not figures_dict:
        st.info("No charts available for download")
        return
    
    # Show kaleido status
    if not KALEIDO_AVAILABLE:
        st.error("Image export unavailable - Kaleido not working")
        return
    
    # st.success("Image export ready")
    
    # Show preparing message while generating download buttons
    with st.spinner("Preparing downloads..."):
        # Pre-generate all images
        prepared_downloads = {}
        success_count = 0
        
        for key, data in figures_dict.items():
            try:
                img_bytes = pio.to_image(
                    data['fig'], 
                    format='png', 
                    width=1400, 
                    height=800, 
                    scale=2
                )
                prepared_downloads[key] = {
                    'img_bytes': img_bytes,
                    'filename': data['filename']
                }
                success_count += 1
                print(f"Successfully prepared {key}: {len(img_bytes)} bytes")
            except Exception as e:
                print(f"Error preparing {key}: {str(e)}")
        
       # st.success(f"Prepared {success_count} charts for download")
    
    # Create two main columns
    left_col, right_col = st.columns([1, 1])
    
    # LEFT COLUMN - Individual downloads
    with left_col:
        st.write("#### Individual Chart Downloads")
        
        for key, download_data in prepared_downloads.items():
            label = key.replace('_', ' ').title()
            button_label = f"Save {label} Chart"
            
            if st.button(button_label, key=f"save_{key}", use_container_width=True, type="secondary"):
                success, result = save_file_with_dialog(
                    download_data['img_bytes'], 
                    download_data['filename']
                )
                if success:
                    # st.success(f"Saved to: {result}")
                    print(f"Saved {download_data['filename']} to {result}")
                elif result:
                    st.error(f"Error: {result}")
                else:
                    st.info("Save cancelled")
            
            st.write("")
    
    # RIGHT COLUMN - Batch downloads
    with right_col:
        st.write("#### Batch and Exports")
        
        # ZIP download
        if st.button("Save All Charts (ZIP)", key="save_zip", use_container_width=True, type="primary"):
            try:
                # Create ZIP
                zip_buffer = BytesIO()
                
                with ZipFile(zip_buffer, 'w') as zf:
                    for key, download_data in prepared_downloads.items():
                        zf.writestr(download_data['filename'], download_data['img_bytes'])
                        print(f"Added {download_data['filename']} to ZIP")
                
                zip_data = zip_buffer.getvalue()
                print(f"ZIP created: {len(zip_data)} bytes with {len(prepared_downloads)} files")
                
                # Save with dialog
                success, result = save_zip_with_dialog(zip_data)
                
                if success:
                    # st.success(f"ZIP saved to: {result}")
                    print(f"Saved ZIP to {result}")
                elif result:
                    st.error(f"Error: {result}")
                else:
                    st.info("Save cancelled")
                    
            except Exception as e:
                st.error(f"Error creating ZIP: {str(e)}")
                print(f"ZIP error: {str(e)}")
        
        st.write("")
        
        # PowerPoint Export (disabled)
        st.button(
            "Export to PowerPoint",
            disabled=True,
            use_container_width=True,
            key="export_ppt",
            help="Feature coming soon",
            type="primary"
        )
        
        st.write("")
        
        # PDF Export (disabled)
        st.button(
            "Export to PDF",
            disabled=True,
            use_container_width=True,
            key="export_pdf",
            help="Feature coming soon",
            type="primary"
        )