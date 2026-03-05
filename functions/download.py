import plotly.io as pio
import plotly.graph_objects as go

# Check if kaleido is available
try:
    from kaleido.scopes.plotly import PlotlyScope
    KALEIDO_AVAILABLE = True
except Exception:
    KALEIDO_AVAILABLE = False

def generate_image_bytes(fig):
    """Generate PNG bytes from figure - cached in session state"""
    try:
        img_bytes = pio.to_image(fig, format='png', width=1400, height=800, scale=2)
        return img_bytes
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None


def save_file_with_dialog(data, default_filename):
    import os
    from tkinter import Tk, filedialog

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
    import os
    import streamlit as st 

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
    import streamlit as st 

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
    from zipfile import ZipFile
    from tkinter import Tk, filedialog
    from io import BytesIO
    import streamlit as st 
    import os

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
    import streamlit as st 

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


def handle_save_table_png(df):
    import os
    import streamlit as st
    from tkinter import Tk, filedialog

    category_col = df['Category'].tolist()
    cost_col     = ['${:,.2f}'.format(v) for v in df['Cost']]
    revenue_col  = ['${:,.2f}'.format(v) for v in df['Revenue']]
    margin_col   = ['${:,.2f}'.format(v) for v in df['Margin']]
    pct_col      = ['{:,.2f}%'.format(v) for v in df['Percentage']]

    highlight = {'TOTAL PRODUCT', 'TOTAL SERVICES', 'TOTAL A&PS'}
    grand     = {'TOTAL PRODUCTS+SERVICES'}
    pan       = {'PAN HPE'}

    fill_colors = []
    font_colors = []
    for cat in category_col:
        u = cat.upper().strip()
        if u in highlight:
            fill_colors.append('#04909d')
            font_colors.append('white')
        elif u in grand:
            fill_colors.append('#01a982')
            font_colors.append('white')
        elif u in pan:
            fill_colors.append('#7764fc')
            font_colors.append('white')
        else:
            fill_colors.append('white')
            font_colors.append('black')

    fig = go.Figure(data=[go.Table(
        columnwidth=[180, 120, 120, 150, 130],
        header=dict(
            values=['<b>Category</b>', '<b>Costs</b>', '<b>Revenue</b>',
                    '<b>FLGM pre-rebate</b>', '<b>FLGM% pre-rebate</b>'],
            fill_color='#333333',
            font=dict(color='white', size=12),
            align=['left', 'right', 'right', 'right', 'right'],
            height=32
        ),
        cells=dict(
            values=[category_col, cost_col, revenue_col, margin_col, pct_col],
            fill_color=[fill_colors] * 5,
            font=dict(color=[font_colors] * 5, size=11),
            align=['left', 'right', 'right', 'right', 'right'],
            height=28
        )
    )])

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

    try:
        height = max(300, len(df) * 28 + 72)
        img_bytes = pio.to_image(fig, format='png', width=1100, height=height, scale=2)
    except Exception:
        st.session_state['table_png_message'] = "❌ Failed to generate image"
        return

    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialfile="data_summary.png",
        filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        title="Save table as PNG..."
    )
    root.destroy()

    if filepath:
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
        st.session_state['table_png_message'] = f"✅ Saved to: {os.path.basename(filepath)}"
    else:
        st.session_state['table_png_message'] = "ℹ️ Save cancelled"


def handle_save_table_excel(df):
    import os
    import pandas as pd
    import streamlit as st
    from io import BytesIO
    from tkinter import Tk, filedialog

    export_df = df.copy()
    export_df = export_df.rename(columns={
        'Cost': 'Costs',
        'Margin': 'FLGM pre-rebate',
        'Percentage': 'FLGM% pre-rebate'
    })

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Data Summary')
        ws = writer.sheets['Data Summary']
        ws.column_dimensions['A'].width = 28
        for col_letter in ['B', 'C', 'D']:
            ws.column_dimensions[col_letter].width = 18
        ws.column_dimensions['E'].width = 16
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row[1:4]:
                cell.number_format = '$#,##0.00'
            row[4].number_format = '0.00"%"'

    excel_bytes = buffer.getvalue()

    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        initialfile="data_summary.xlsx",
        filetypes=[("Excel File", "*.xlsx"), ("All Files", "*.*")],
        title="Save table as Excel..."
    )
    root.destroy()

    if filepath:
        with open(filepath, 'wb') as f:
            f.write(excel_bytes)
        st.session_state['table_excel_message'] = f"✅ Saved to: {os.path.basename(filepath)}"
    else:
        st.session_state['table_excel_message'] = "ℹ️ Save cancelled"


def render_table_export_buttons(df):
    import streamlit as st

    for session_key in ['table_png_message', 'table_excel_message']:
        if session_key in st.session_state:
            message = st.session_state[session_key]
            if '✅' in message:
                st.toast(message.replace('✅ ', ''), icon="✅")
            elif '❌' in message:
                st.toast(message.replace('❌ ', ''), icon="❌")
            elif 'ℹ️' in message:
                st.toast(message.replace('ℹ️ ', ''), icon="ℹ️")
            del st.session_state[session_key]

    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "📷 Export Table as PNG",
            key="export_table_png",
            use_container_width=True,
            type="secondary",
            on_click=handle_save_table_png,
            args=(df,),
            disabled=not KALEIDO_AVAILABLE
        )
    with col2:
        st.button(
            "📊 Export Table as Excel",
            key="export_table_excel",
            use_container_width=True,
            type="secondary",
            on_click=handle_save_table_excel,
            args=(df,)
        )


def render_export_buttons():
    import streamlit as st 

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