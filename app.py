import streamlit as st
import pandas as pd
import json
import os
import zipfile
import io
from datetime import datetime

# Try to import PDF libraries
try:
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas as pdf_canvas
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Configuration for Template Storage
TEMPLATE_DIR = "templates"
SAVED_FILES_DIR = "saved_files"
DRIVER_KEY = "Driver Run Sheet Processor"
KITCHEN_KEY = "Kitchen Order List Processor"
PDF_LABEL_KEY = "PDF Label Numbering"

# Create directories if they don't exist
for directory in [TEMPLATE_DIR, SAVED_FILES_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_template_path(tool_name):
    """Return a safe filesystem path for storing templates for the given tool."""
    # Ensure tool_name is converted to string and strip/normalize characters
    safe_name = "".join(
        c for c in str(tool_name) if c.isalnum() or c in (" ", "-", "_")
    ).strip().replace(" ", "_").lower()
    # Use a robust falsy check for empty names
    if not safe_name:
        safe_name = "default"
    filename = f"{safe_name}.json"
    return os.path.join(TEMPLATE_DIR, filename)

def load_templates(tool_name):
    """Loads templates from a JSON file for the given tool."""
    path = get_template_path(tool_name)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_templates(tool_name, templates):
    """Saves the current template configurations to a JSON file."""
    path = get_template_path(tool_name)
    with open(path, 'w') as f:
        json.dump(templates, f, indent=4)

def save_processed_file(df, filename):
    """Save processed DataFrame to the saved_files directory."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{filename}_{timestamp}.xlsx"
    filepath = os.path.join(SAVED_FILES_DIR, safe_filename)
    df.to_excel(filepath, index=False)
    return filepath

def get_saved_files():
    """Get list of saved files from saved_files directory."""
    if not os.path.exists(SAVED_FILES_DIR):
        return []
    files = [f for f in os.listdir(SAVED_FILES_DIR) if f.endswith(('.xlsx', '.csv'))]
    files.sort(reverse=True)
    return files

def load_saved_file(filename):
    """Load a saved file as DataFrame."""
    filepath = os.path.join(SAVED_FILES_DIR, filename)
    if filename.endswith('.csv'):
        return pd.read_csv(filepath)
    else:
        return pd.read_excel(filepath)

def process_data(df, template_config):
    """Applies column selection and reordering based on the template."""
    if not df.empty and template_config and 'columns' in template_config:
        ordered_columns = template_config['columns']
        df = df[[col for col in ordered_columns if col in df.columns]]
        return df
    return df

def pdf_label_numbering_tool():
    """Adds route numbers to existing PDF labels by matching order numbers."""
    
    st.header("🏷️ Smart PDF Label Numbering")
    st.markdown("**Match order numbers and add correct route numbers to labels**")
    
    if not PDF_SUPPORT:
        st.error("❌ PDF support not available!")
        st.code("pip install PyPDF2 reportlab", language="bash")
        st.info("Run this command in your terminal, then restart the app.")
        return
    
    st.markdown("---")
    
    if 'loaded_driver_df' not in st.session_state:
        st.session_state.loaded_driver_df = None
    
    settings_file = os.path.join(TEMPLATE_DIR, "pdf_label_settings.json")
    default_settings = {
        "font_size": 72,
        "x_position": 30,
        "y_offset": 90,
        "color": "Red"
    }
    
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            saved_settings = json.load(f)
    else:
        saved_settings = default_settings
    
    st.subheader("1️⃣ Get Driver Run Sheet")
    
    tab1, tab2 = st.tabs(["📤 Upload New File", "💾 Use Saved File"])
    
    driver_df = None
    
    with tab1:
        st.info("💡 Upload your processed run sheet with stop numbers and order numbers")
        driver_file = st.file_uploader(
            "Choose your driver run file",
            type=['csv', 'xlsx', 'xls'],
            key="pdf_driver_upload",
            help="Excel file with stop orders and order reference numbers"
        )
        
        if driver_file:
            try:
                if driver_file.name.endswith('.csv'):
                    driver_df = pd.read_csv(driver_file)
                else:
                    excel_file = pd.ExcelFile(driver_file)
                    sheet_name = excel_file.sheet_names[0]
                    
                    best_df = None
                    best_unnamed_count = float('inf')
                    
                    for header_row in range(0, 5):
                        temp_df = pd.read_excel(driver_file, sheet_name=sheet_name, header=header_row)
                        unnamed_count = sum(1 for col in temp_df.columns if str(col).startswith('Unnamed:'))
                        
                        if unnamed_count < best_unnamed_count:
                            best_unnamed_count = unnamed_count
                            best_df = temp_df
                        
                        if unnamed_count == 0:
                            break
                    
                    driver_df = best_df
                
                driver_df = driver_df.dropna(how='all')
                st.session_state.loaded_driver_df = driver_df
                st.success(f"✅ Loaded run sheet with {len(driver_df)} stops")
                
            except Exception as e:
                st.error(f"❌ Error reading run sheet: {e}")
    
    with tab2:
        saved_files = get_saved_files()
        
        if saved_files:
            st.info(f"💡 Found {len(saved_files)} saved file(s)")
            
            selected_saved_file = st.selectbox(
                "Select a previously saved run sheet:",
                saved_files,
                format_func=lambda x: f"{x.replace('_', ' ').replace('.xlsx', '').replace('.csv', '')}"
            )
            
            if st.button("📂 Load This File", use_container_width=True):
                try:
                    driver_df = load_saved_file(selected_saved_file)
                    driver_df = driver_df.dropna(how='all')
                    st.session_state.loaded_driver_df = driver_df
                    st.success(f"✅ Loaded saved file with {len(driver_df)} stops")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error loading saved file: {e}")
        else:
            st.warning("⚠️ No saved files found. Process a run sheet first in 'Driver Run Sheet Processor'")
    
    if st.session_state.loaded_driver_df is not None:
        driver_df = st.session_state.loaded_driver_df

    if driver_df is not None and not driver_df.empty:
        with st.expander("📊 Preview Run Sheet Data"):
            st.dataframe(driver_df.head(10), use_container_width=True)
    
    st.subheader("2️⃣ Upload Label PDF")
    st.info("💡 Upload the PDF with all labels (can be in any order)")
    
    label_pdf = st.file_uploader(
        "Upload label PDF file",
        type=['pdf'],
        key="pdf_labels_upload",
        help="PDF file with labels from your delivery system"
    )

    if driver_df is not None and label_pdf:
        st.markdown("---")
        
        st.subheader("3️⃣ Map Your Columns")
        
        col1, col2, col3 = st.columns(3)
        
        stop_default = None
        order_default = None
        
        for i, col in enumerate(driver_df.columns):
            col_lower = str(col).lower()
            sample_values = driver_df[col].dropna().astype(str).head(3).tolist()
            
            if stop_default is None:
                try:
                    numeric_count = sum(1 for v in sample_values if v.replace('.','').isdigit())
                    if numeric_count >= 2:
                        avg_val = sum(float(v) for v in sample_values if v.replace('.','').isdigit()) / numeric_count
                        if avg_val < 100:
                            stop_default = i
                except:
                    pass
            
            if order_default is None and ('ref' in col_lower or 'order' in col_lower):
                order_default = i
        
        if stop_default is None:
            stop_default = 0
        if order_default is None:
            order_default = min(len(driver_df.columns) - 1, 1)
        
        with col1:
            st.markdown("**🔢 Stop Numbers**")
            stop_col = st.selectbox(
                "Column with route order (1, 2, 3...)",
                driver_df.columns,
                index=stop_default,
                key="pdf_stop"
            )
            st.caption(f"Sample: {driver_df[stop_col].head(3).tolist()}")
        
        with col2:
            st.markdown("**📦 Order Reference**")
            order_col = st.selectbox(
                "Column with order numbers/IDs",
                driver_df.columns,
                index=order_default,
                key="pdf_order"
            )
            st.caption(f"Sample: {driver_df[order_col].head(3).tolist()}")
        
        with col3:
            st.markdown("**👤 Driver Filter (optional)**")
            has_driver_col = st.checkbox("Filter by driver?", value=False)
            if has_driver_col:
                driver_col = st.selectbox(
                    "Driver name column",
                    driver_df.columns,
                    key="pdf_driver"
                )
                unique_drivers = driver_df[driver_col].unique()
                selected_driver = st.selectbox("Select driver:", unique_drivers)
                driver_df = driver_df[driver_df[driver_col] == selected_driver]
        
        st.markdown("---")
        
        order_to_stop = {}
        for _, row in driver_df.iterrows():
            order_num = str(row[order_col]).strip()
            stop_num = str(int(float(row[stop_col])))
            order_to_stop[order_num] = stop_num
        
        st.write(f"**📋 Created mapping for {len(order_to_stop)} orders**")
        
        with st.expander("🔍 Preview Order Mapping"):
            mapping_df = pd.DataFrame(list(order_to_stop.items()), columns=['Order Ref', 'Stop #'])
            st.dataframe(mapping_df.head(20), use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("4️⃣ Customize Number Placement")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            font_size = st.slider("Font Size", 20, 200, saved_settings["font_size"], 5)
        
        with col_b:
            x_position = st.slider("Horizontal Position (from left)", 0, 600, saved_settings["x_position"], 10)
        
        with col_c:
            y_offset = st.slider("Vertical Position (from top)", 0, 800, saved_settings["y_offset"], 10)
        
        col_d, col_e = st.columns(2)
        
        with col_d:
            color_options = ["Red", "Black", "Blue", "Green", "Orange"]
            default_color_index = color_options.index(saved_settings["color"]) if saved_settings["color"] in color_options else 0
            
            color_choice = st.selectbox(
                "Number Color",
                color_options,
                index=default_color_index
            )
            color_map = {
                "Red": (1, 0, 0),
                "Black": (0, 0, 0),
                "Blue": (0, 0, 1),
                "Green": (0, 0.5, 0),
                "Orange": (1, 0.5, 0)
            }
            number_color = color_map[color_choice]
        
        with col_e:
            st.markdown("**Preview Settings:**")
            st.write(f"• Font: {font_size}pt, {color_choice}")
            st.write(f"• Position: ({x_position}, {y_offset})")
            st.info("💡 Increase Y to move DOWN")
            
            if st.button("💾 Save These Settings as Default", use_container_width=True):
                new_settings = {
                    "font_size": font_size,
                    "x_position": x_position,
                    "y_offset": y_offset,
                    "color": color_choice
                }
                with open(settings_file, 'w') as f:
                    json.dump(new_settings, f, indent=4)
                st.success("✅ Settings saved! These will be your defaults next time.")
        
        st.markdown("---")
        
        st.subheader("5️⃣ Process Labels")
        
        reader = PdfReader(label_pdf)
        st.write(f"**📄 Found {len(reader.pages)} label(s) in PDF**")
        
        if st.button("🎨 Add Route Numbers to Labels", type="primary", use_container_width=True):
            with st.spinner("Processing labels..."):
                try:
                    writer = PdfWriter()
                    matched_count = 0
                    unmatched_orders = []
                    
                    for page_idx, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        
                        found_order = None
                        for order_ref in order_to_stop.keys():
                            if order_ref in page_text:
                                found_order = order_ref
                                break
                        
                        if found_order:
                            stop_num = order_to_stop[found_order]
                            matched_count += 1
                        else:
                            stop_num = "?"
                            unmatched_orders.append(f"Page {page_idx + 1}")
                        
                        packet = io.BytesIO()
                        page_width = float(page.mediabox.width)
                        page_height = float(page.mediabox.height)
                        
                        can = pdf_canvas.Canvas(packet, pagesize=(page_width, page_height))
                        can.setFont("Helvetica-Bold", font_size)
                        can.setFillColorRGB(*number_color)
                        can.drawString(x_position, page_height - y_offset, stop_num)
                        can.save()
                        packet.seek(0)
                        
                        overlay = PdfReader(packet)
                        page.merge_page(overlay.pages[0])
                        writer.add_page(page)
                    
                    output = io.BytesIO()
                    writer.write(output)
                    output.seek(0)
                    
                    st.success(f"✅ Successfully matched {matched_count} out of {len(reader.pages)} labels!")
                    
                    if unmatched_orders:
                        st.warning(f"⚠️ Could not match {len(unmatched_orders)} labels: {', '.join(unmatched_orders[:5])}")
                        st.info("💡 These will be marked with '?' - check if order numbers match exactly")
                    
                    st.markdown("---")
                    
                    st.download_button(
                        label="⬇️ Download Numbered Labels",
                        data=output,
                        file_name=f"numbered_labels_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    st.balloons()
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())

def file_processor_tool(tool_name):
    """Generates the UI and logic for a specific file processing tool."""

    st.header(tool_name)

    uploaded_file = st.file_uploader(
        f"**1. Upload your daily file** (CSV, Excel with multiple sheets, or ZIP containing these files) for the {tool_name}", 
        type=['csv', 'xlsx', 'xls', 'zip']
    )

    if uploaded_file is not None:
        try:
            df = None
            original_columns = []
            
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                try:
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_names = excel_file.sheet_names
                    
                    st.subheader(f"📊 Found {len(sheet_names)} sheet(s)")
                    
                    if len(sheet_names) == 1:
                        st.info(f"Only one sheet found: **{sheet_names[0]}**")
                        selected_sheet = sheet_names[0]
                    else:
                        selected_sheet = st.selectbox(
                            "**Select which sheet to process:**",
                            sheet_names,
                            key=f"{tool_name}_sheet_selector"
                        )
                    
                    st.write(f"**Selected sheet:** `{selected_sheet}`")
                    
                    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                    
                    unnamed_count = sum(1 for col in df.columns if str(col).startswith('Unnamed:'))
                    if unnamed_count > len(df.columns) / 2:
                        for header_row in range(0, min(5, len(df))):
                            temp_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, header=header_row)
                            temp_unnamed = sum(1 for col in temp_df.columns if str(col).startswith('Unnamed:'))
                            
                            if temp_unnamed < unnamed_count:
                                df = temp_df
                                break
                    
                except Exception as excel_error:
                    st.error(f"❌ Error reading Excel file: {excel_error}")
                    return
            
            elif uploaded_file.name.endswith('.zip'):
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    all_files = zip_ref.namelist()
                    
                    file_list = []
                    for f in all_files:
                        filename = f.split('/')[-1]
                        
                        if (f.endswith(('.csv', '.xlsx', '.xls')) and 
                            not f.startswith('__MACOSX/') and 
                            not filename.startswith('.') and
                            filename != '' and
                            not f.endswith('/')):
                            file_list.append(f)
                    
                    if not file_list:
                        st.error("No CSV or Excel files found in the ZIP archive.")
                        st.info("💡 **Tip:** Make sure your ZIP contains files with extensions: .csv, .xlsx, or .xls")
                        return
                    
                    st.subheader(f"📁 Found {len(file_list)} file(s) in ZIP")
                    
                    if len(file_list) == 1:
                        st.info(f"Only one supported file found: **{file_list[0].split('/')[-1]}**")
                        selected_file = file_list[0]
                    else:
                        selected_file = st.selectbox(
                            "**Select which file to process:**", 
                            file_list,
                            format_func=lambda x: x.split('/')[-1],
                            key=f"{tool_name}_file_selector"
                        )
                    
                    st.write(f"**Selected file:** `{selected_file}`")
                    
                    if selected_file:
                        try:
                            with zip_ref.open(selected_file) as file_in_zip:
                                file_content = file_in_zip.read()
                                
                                if selected_file.endswith('.csv'):
                                    try:
                                        df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
                                    except UnicodeDecodeError:
                                        try:
                                            df = pd.read_csv(io.StringIO(file_content.decode('latin-1')))
                                            st.warning("⚠️ Used latin-1 encoding for CSV file")
                                        except:
                                            df = pd.read_csv(io.StringIO(file_content.decode('cp1252')))
                                            st.warning("⚠️ Used cp1252 encoding for CSV file")
                                elif selected_file.endswith(('.xlsx', '.xls')):
                                    df = pd.read_excel(io.BytesIO(file_content))
                                
                                st.success(f"✅ Successfully loaded: **{selected_file.split('/')[-1]}** ({len(df)} rows, {len(df.columns)} columns)")
                        except Exception as file_error:
                            st.error(f"❌ Error reading file '{selected_file}': {file_error}")
                            return
            
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Successfully loaded: **{uploaded_file.name}** ({len(df)} rows, {len(df.columns)} columns)")

            if df is not None:
                original_columns = list(df.columns)

                templates = load_templates(tool_name)
                template_names = list(templates.keys())

                st.subheader("2. Apply or Create Template")

                col_temp1, col_temp2 = st.columns([3, 1])
                
                with col_temp1:
                    selected_template_name = st.selectbox(
                        "**Select Template**", 
                        ["<New Template>"] + template_names,
                        key=f"{tool_name}_template_selector_{uploaded_file.name}"
                    )
                
                with col_temp2:
                    if selected_template_name != "<New Template>":
                        if st.button("🗑️ Delete Template", key=f"delete_{selected_template_name}", use_container_width=True):
                            del templates[selected_template_name]
                            save_templates(tool_name, templates)
                            st.success(f"Template **'{selected_template_name}'** deleted!")
                            st.rerun()

                current_config = None
                if selected_template_name != "<New Template>":
                    current_config = templates[selected_template_name]

                st.markdown("---")
                st.subheader("Customize Columns")

                initial_cols = current_config['columns'] if current_config else original_columns

                st.write("Use the multiselect below to **reorder** and **remove/keep** columns.")

                session_key = f"{tool_name}_template_state"
                file_key = f"{tool_name}_file_state"
                
                if (session_key not in st.session_state or 
                    file_key not in st.session_state or 
                    st.session_state[file_key] != uploaded_file.name or
                    st.session_state.get(f"{session_key}_name") != selected_template_name):
                    
                    st.session_state[session_key] = initial_cols
                    st.session_state[file_key] = uploaded_file.name
                    st.session_state[f"{session_key}_name"] = selected_template_name

                new_column_order = st.multiselect(
                    '**Processed Column Order**:',
                    options=original_columns,
                    default=st.session_state[session_key],
                    key=f'{tool_name}_multiselect_{uploaded_file.name}_{selected_template_name}'
                )

                processed_df = process_data(df, {'columns': new_column_order})

                if tool_name == KITCHEN_KEY and not processed_df.empty:
                    type_column = None
                    for col in processed_df.columns:
                        if col.lower() == 'type':
                            type_column = col
                            break
                    
                    if type_column:
                        st.markdown("---")
                        st.subheader("🔍 Filter by Type")
                        
                        unique_types = processed_df[type_column].dropna().unique().tolist()
                        
                        filter_options = st.multiselect(
                            "**Select which types to include:**",
                            options=unique_types,
                            default=unique_types,
                            help="Remove a type to filter it out from the results",
                            key=f"{tool_name}_type_filter"
                        )
                        
                        if filter_options:
                            processed_df = processed_df[processed_df[type_column].isin(filter_options)]
                            st.info(f"Showing **{len(processed_df)}** rows with type(s): {', '.join(filter_options)}")
                        else:
                            st.warning("⚠️ No types selected. Showing all rows.")

                st.markdown("---")
                st.subheader("3. Preview and Export")

                st.dataframe(processed_df, use_container_width=True)
                
                if not processed_df.empty:
                    html_table = processed_df.to_html(index=False, border=1, escape=False)
                    
                    print_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tool_name} - Print View</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; padding: 20px; background: white; }}
        table {{ width: 100%; border-collapse: collapse; margin: 0 auto; font-size: 11px; }}
        th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
        th {{ background-color: #f0f0f0; font-weight: bold; color: #333; }}
        tbody tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .footer {{ margin-top: 20px; text-align: center; font-size: 10px; color: #666; }}
        @media print {{
            body {{ padding: 10px; }}
            th {{ background-color: #f0f0f0 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            tbody tr:nth-child(even) {{ background-color: #f9f9f9 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
        @page {{ size: A4 landscape; margin: 0.5in; }}
    </style>
</head>
<body>
    {html_table}
    <div class="footer">
        <p>Business Automation Platform | Printed in landscape mode</p>
    </div>
</body>
</html>"""

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 🖨️ Print Options")
                        
                        if st.button("🖨️ Open Print Preview", type="primary", use_container_width=True, key="open_print_preview"):
                            import base64
                            b64_html = base64.b64encode(print_html.encode()).decode()
                            
                            st.components.v1.html(f"""
                                <script>
                                    var printWindow = window.open('', '_blank');
                                    var htmlContent = atob('{b64_html}');
                                    printWindow.document.write(htmlContent);
                                    printWindow.document.close();
                                    
                                    printWindow.onload = function() {{
                                        setTimeout(function() {{
                                            printWindow.print();
                                        }}, 500);
                                    }};
                                </script>
                            """, height=0)
                            st.success("✅ Print preview opened in new tab!")
                        
                        st.download_button(
                            label="📄 Download Print File (HTML)",
                            data=print_html,
                            file_name=f"{tool_name.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html",
                            help="Download HTML file if print preview doesn't work",
                            use_container_width=True
                        )

                    with col2:
                        if selected_template_name != "<New Template>":
                            with st.expander("✏️ Update This Template"):
                                st.info(f"Currently editing: **{selected_template_name}**")
                                
                                rename_template = st.text_input(
                                    "Rename to (leave empty to keep current name):", 
                                    value="",
                                    key="rename_template_input"
                                )
                                
                                if st.button("💾 Save Changes", key="update_template", use_container_width=True):
                                    final_name = rename_template.strip() if rename_template.strip() else selected_template_name
                                    
                                    if final_name != selected_template_name and final_name in templates:
                                        st.error(f"Template '{final_name}' already exists. Choose a different name.")
                                    else:
                                        if final_name != selected_template_name:
                                            del templates[selected_template_name]
                                        
                                        templates[final_name] = {'columns': new_column_order}
                                        save_templates(tool_name, templates)
                                        
                                        if final_name != selected_template_name:
                                            st.success(f"Template renamed from **'{selected_template_name}'** to **'{final_name}'** and updated!")
                                        else:
                                            st.success(f"Template **'{final_name}'** updated successfully!")
                                        st.rerun()
                        
                        with st.expander("💾 Save as New Template"):
                            new_template_name = st.text_input("New Template Name:", key="new_template_input")

                            if st.button("Save Configuration", disabled=not new_template_name, key="save_new_template"):
                                if new_template_name in templates:
                                    st.error(f"Template '{new_template_name}' already exists. Choose a different name.")
                                else:
                                    new_template = {'columns': new_column_order}
                                    templates[new_template_name] = new_template
                                    save_templates(tool_name, templates)
                                    st.success(f"Template **'{new_template_name}'** saved successfully!")
                                    st.rerun()
                        
                        st.markdown("---")
                        st.subheader("📥 Export Data")
                        
                        if tool_name == DRIVER_KEY:
                            if st.button("💾 Save for PDF Labeling", use_container_width=True, type="primary"):
                                try:
                                    saved_path = save_processed_file(processed_df, "driver_run_sheet")
                                    st.success(f"✅ Saved! You can now use this in 'PDF Label Numbering' → 'Use Saved File'")
                                    st.info(f"📁 Saved as: `{os.path.basename(saved_path)}`")
                                except Exception as e:
                                    st.error(f"❌ Error saving file: {e}")
                        
                        csv_data = processed_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Download as CSV",
                            data=csv_data,
                            file_name=f"processed_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

        except Exception as e:
            st.error(f"An error occurred during file processing: {e}")
            st.info("Please ensure your file is a valid CSV or Excel format.")

# Main app
st.set_page_config(
    layout="wide", 
    page_title="Business Automation Platform", 
    page_icon="⚙️"
)

st.title("⚙️ Business Automation Platform")

st.markdown("Streamline your daily file processing with reusable templates.")

st.sidebar.title("🔧 Automation Tools")
selected_tool = st.sidebar.radio(
    "Select a Processor:",
    [DRIVER_KEY, KITCHEN_KEY, PDF_LABEL_KEY],
    help="Choose which automation tool to use"
)

# Show tool descriptions
tool_descriptions = {
    DRIVER_KEY: "📋 Process driver run sheets - organize delivery routes and stops",
    KITCHEN_KEY: "🍳 Process kitchen order lists - organize food preparation orders",
    PDF_LABEL_KEY: "🏷️ Add route numbers to PDF labels automatically"
}

st.sidebar.markdown("---")
st.sidebar.info(tool_descriptions[selected_tool])

# Run the selected tool
if selected_tool == PDF_LABEL_KEY:
    pdf_label_numbering_tool()
else:
    file_processor_tool(selected_tool)