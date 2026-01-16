import streamlit as st 
import plotly.io as pio
from io import BytesIO
from zipfile import ZipFile


def render_download_section(figures_dict):
    """
    Renders download section for saved figures
    """
    if not figures_dict:
        st.info("No charts available for download")
        return
    
    # Show preparing message while generating download buttons
    with st.spinner("Preparing downloads..."):
        # Pre-generate all images
        prepared_downloads = {}
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
            except Exception as e:
                print(f"Error preparing {key}: {str(e)}")
    
    # Create two main columns
    left_col, right_col = st.columns([1, 1])
    
    # LEFT COLUMN - Individual downloads
    with left_col:
        st.write("#### Individual Chart Downloads")
        
        for key, download_data in prepared_downloads.items():
            # Create friendly label from key
            label = key.replace('_', ' ').title()
            button_label = f"Download {label} Chart"
            
            st.download_button(
                label=button_label,
                data=download_data['img_bytes'],
                file_name=download_data['filename'],
                mime="image/png",
                key=f"dl_{key}",
                use_container_width=True,
                type="secondary"
            )
            st.write("")
    
    # RIGHT COLUMN - Batch downloads
    with right_col:
        st.write("#### Batch and Exports")
        
        # Prepare ZIP automatically
        try:
            
            zip_buffer = BytesIO()
            
            with ZipFile(zip_buffer, 'w') as zf:
                for key, download_data in prepared_downloads.items():
                    try:
                        zf.writestr(download_data['filename'], download_data['img_bytes'])
                    except Exception as e:
                        print(f"Failed adding {key} to ZIP: {str(e)}")
            
            # Single download button for ZIP
            st.download_button(
                label=f"Download All Charts (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="financial_charts.zip",
                mime="application/zip",
                key="dl_zip",
                use_container_width=True,
                type="primary"
            )
            
        except Exception as e:
            st.error(f"Error creating ZIP: {str(e)}")
        
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