import streamlit as st
import pandas as pd
import json
import os
import zipfile
import io
from datetime import datetime

# Time-based gradient functions
def get_time_based_gradient():
    """Returns gradient CSS classes based on current time of day"""
    hour = datetime.now().hour

    if 5 <= hour < 12:
        # Morning: Fresh, energetic blues and warm yellows
        return {
            'background': 'linear-gradient(135deg, #e0f2fe 0%, #dbeafe 50%, #e0e7ff 100%)',
            'orb1': 'radial-gradient(circle, rgba(96, 165, 250, 0.3) 0%, rgba(34, 211, 238, 0.3) 100%)',
            'orb2': 'radial-gradient(circle, rgba(34, 211, 238, 0.3) 0%, rgba(20, 184, 166, 0.3) 100%)'
        }
    elif 12 <= hour < 17:
        # Afternoon: Bright, productive purples and pinks
        return {
            'background': 'linear-gradient(135deg, #ede9fe 0%, #f3e8ff 50%, #fae8ff 100%)',
            'orb1': 'radial-gradient(circle, rgba(192, 132, 252, 0.3) 0%, rgba(236, 72, 153, 0.3) 100%)',
            'orb2': 'radial-gradient(circle, rgba(232, 121, 249, 0.3) 0%, rgba(192, 132, 252, 0.3) 100%)'
        }
    elif 17 <= hour < 20:
        # Evening: Warm sunset oranges and pinks
        return {
            'background': 'linear-gradient(135deg, #fed7aa 0%, #fecdd3 50%, #fbcfe8 100%)',
            'orb1': 'radial-gradient(circle, rgba(251, 146, 60, 0.3) 0%, rgba(251, 113, 133, 0.3) 100%)',
            'orb2': 'radial-gradient(circle, rgba(251, 113, 133, 0.3) 0%, rgba(244, 114, 182, 0.3) 100%)'
        }
    else:
        # Night: Deep, calm indigos and purples
        return {
            'background': 'linear-gradient(135deg, #c7d2fe 0%, #ddd6fe 50%, #e9d5ff 100%)',
            'orb1': 'radial-gradient(circle, rgba(129, 140, 248, 0.3) 0%, rgba(167, 139, 250, 0.3) 100%)',
            'orb2': 'radial-gradient(circle, rgba(167, 139, 250, 0.3) 0%, rgba(192, 132, 252, 0.3) 100%)'
        }

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
MESSAGES_DIR = "messages"
DRIVER_KEY = "Driver Run Sheet Processor"
KITCHEN_KEY = "Kitchen Order List Processor"
PDF_LABEL_KEY = "PDF Label Numbering"
COMMS_KEY = "Customer Communication Hub"

# Create directories if they don't exist
for directory in [TEMPLATE_DIR, SAVED_FILES_DIR, MESSAGES_DIR]:
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

def save_processed_file(df, filename, driver_name=None):
    """Save processed DataFrame to the saved_files directory with optional driver name."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create a descriptive filename with driver name if available
    if driver_name:
        # Clean driver name for filename
        clean_driver_name = "".join(c for c in str(driver_name) if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        safe_filename = f"{filename}_{clean_driver_name}_{timestamp}.xlsx"
    else:
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

def format_saved_file_display(filename):
    """Format saved file name for better display with driver name extraction."""
    # Remove extension
    name_without_ext = filename.replace('.xlsx', '').replace('.csv', '')
    
    # Try to extract driver name if present
    # Expected format: driver_run_sheet_DriverName_YYYYMMDD_HHMMSS
    parts = name_without_ext.split('_')
    
    if len(parts) >= 4 and 'driver' in name_without_ext.lower():
        try:
            # Find the timestamp (last two parts should be date and time)
            date_part = parts[-2]  # YYYYMMDD
            time_part = parts[-1]  # HHMMSS
            
            # Check if these look like timestamp parts
            if (len(date_part) == 8 and date_part.isdigit() and 
                len(time_part) == 6 and time_part.isdigit()):
                
                # Extract driver name (everything between 'sheet' and timestamp)
                sheet_index = None
                for i, part in enumerate(parts):
                    if 'sheet' in part.lower():
                        sheet_index = i
                        break
                
                if sheet_index is not None and sheet_index + 1 < len(parts) - 2:
                    driver_parts = parts[sheet_index + 1:-2]
                    driver_name = ' '.join(driver_parts).replace('_', ' ').title()
                    
                    # Format timestamp for display
                    try:
                        date_obj = datetime.strptime(date_part + time_part, '%Y%m%d%H%M%S')
                        formatted_date = date_obj.strftime('%m/%d/%Y %I:%M %p')
                        
                        return f"🚛 {driver_name} - {formatted_date}"
                    except:
                        return f"🚛 {driver_name} - {date_part}_{time_part}"
        except:
            pass
    
    # Fallback to basic formatting
    formatted = name_without_ext.replace('_', ' ').title()
    return f"📄 {formatted}"

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
    
    # Initialize session state for persistent driver file and column mappings
    if 'loaded_driver_df' not in st.session_state:
        st.session_state.loaded_driver_df = None
    if 'pdf_stop_column' not in st.session_state:
        st.session_state.pdf_stop_column = None
    if 'pdf_order_column' not in st.session_state:
        st.session_state.pdf_order_column = None
    if 'pdf_driver_column' not in st.session_state:
        st.session_state.pdf_driver_column = None
    if 'pdf_selected_driver' not in st.session_state:
        st.session_state.pdf_selected_driver = None
    if 'pdf_use_driver_filter' not in st.session_state:
        st.session_state.pdf_use_driver_filter = False
    
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
    
    st.subheader("1️⃣ Driver Run Sheet")
    
    # Check if we already have a loaded driver file
    if st.session_state.loaded_driver_df is not None:
        df_info = st.session_state.loaded_driver_df
        st.success(f"✅ **Driver file already loaded** ({len(df_info)} stops)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Show a preview of the current file
            with st.expander("📊 Current Driver Data Preview", expanded=False):
                st.dataframe(df_info.head(10), use_container_width=True)
        
        with col2:
            if st.button("🔄 Load Different File", use_container_width=True):
                # Clear the current driver data to allow selecting a new one
                st.session_state.loaded_driver_df = None
                st.rerun()
            
            if st.button("🗑️ Clear All Settings", use_container_width=True, help="Reset column mappings and driver selections"):
                # Clear all PDF tool settings
                st.session_state.pdf_stop_column = None
                st.session_state.pdf_order_column = None
                st.session_state.pdf_driver_column = None
                st.session_state.pdf_selected_driver = None
                st.session_state.pdf_use_driver_filter = False
                st.success("✅ All settings cleared!")
                st.rerun()
    else:
        # Show the file selection interface only if no file is loaded
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
                st.info(f"💡 Found {len(saved_files)} saved driver run sheet(s)")
                
                # Show a preview of available files
                with st.expander("📋 Preview Available Files", expanded=False):
                    for file in saved_files[:5]:  # Show first 5 files
                        display_name = format_saved_file_display(file)
                        st.write(f"• {display_name}")
                    if len(saved_files) > 5:
                        st.write(f"• ... and {len(saved_files) - 5} more files")
                
                selected_saved_file = st.selectbox(
                    "Select a previously saved run sheet:",
                    saved_files,
                    format_func=format_saved_file_display,
                    help="Files are sorted by date (newest first). Driver names are extracted when available."
                )
                
                if st.button("📂 Load This File", use_container_width=True):
                    try:
                        driver_df = load_saved_file(selected_saved_file)
                        driver_df = driver_df.dropna(how='all')
                        st.session_state.loaded_driver_df = driver_df
                        
                        # Extract driver name from filename for display
                        display_name = format_saved_file_display(selected_saved_file)
                        clean_display = display_name.replace('🚛 ', '').replace('📄 ', '')
                        
                        st.success(f"✅ Loaded: **{clean_display}** ({len(driver_df)} stops)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error loading saved file: {e}")
            else:
                st.warning("⚠️ No saved files found. Process a run sheet first in 'Driver Run Sheet Processor'")
    
    # Get the current driver dataframe for processing
    driver_df = st.session_state.loaded_driver_df
    
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
        
        st.subheader("3️⃣ Column Mapping")
        
        # Auto-detect columns if not previously set or if columns don't exist in current data
        if (st.session_state.pdf_stop_column is None or 
            st.session_state.pdf_stop_column not in driver_df.columns or
            st.session_state.pdf_order_column is None or 
            st.session_state.pdf_order_column not in driver_df.columns):
            
            # Smart auto-detection for first time or when columns are missing
            stop_default = None
            order_default = None
            
            for col in driver_df.columns:
                col_lower = str(col).lower()
                sample_values = driver_df[col].dropna().astype(str).head(5).tolist()
                
                # Detect stop numbers (should be small sequential numbers like 1,2,3,4,5)
                if stop_default is None:
                    try:
                        numeric_values = []
                        for v in sample_values:
                            clean_v = str(v).strip()
                            if clean_v.replace('.','').isdigit():
                                numeric_values.append(float(clean_v))
                        
                        if len(numeric_values) >= 3:
                            avg_val = sum(numeric_values) / len(numeric_values)
                            max_val = max(numeric_values)
                            # Stop numbers should be small (under 50) and sequential-ish
                            if max_val < 50 and avg_val < 20 and ('stop' in col_lower or 'order' in col_lower):
                                stop_default = col
                    except:
                        pass
                
                # Detect order reference (longer alphanumeric strings)
                if order_default is None:
                    if ('ref' in col_lower or 'order' in col_lower or 'number' in col_lower):
                        # Check if values look like order numbers (longer strings)
                        long_values = [v for v in sample_values if len(str(v).strip()) > 3]
                        if len(long_values) >= 2:  # At least 2 samples with longer values
                            order_default = col
            
            # Fallback logic if auto-detection didn't work
            if stop_default is None:
                # Look for columns with small numeric values
                for col in driver_df.columns:
                    sample_values = driver_df[col].dropna().astype(str).head(5).tolist()
                    try:
                        numeric_values = [float(v) for v in sample_values if str(v).replace('.','').isdigit()]
                        if len(numeric_values) >= 2:
                            max_val = max(numeric_values)
                            if max_val < 100:  # Likely stop numbers
                                stop_default = col
                                break
                    except:
                        continue
                        
                if stop_default is None:
                    stop_default = driver_df.columns[0]
            
            if order_default is None:
                # Find a column that's different from stop_default
                for col in driver_df.columns:
                    if col != stop_default:
                        order_default = col
                        break
                        
                if order_default is None:
                    order_default = driver_df.columns[min(len(driver_df.columns) - 1, 1)]
                
            # Set the detected columns
            st.session_state.pdf_stop_column = stop_default
            st.session_state.pdf_order_column = order_default
            
            st.success(f"✅ **Auto-detected columns:** Stop Numbers = '{stop_default}', Order Reference = '{order_default}'")
        else:
            st.info(f"📌 **Using saved column mapping:** Stop Numbers = '{st.session_state.pdf_stop_column}', Order Reference = '{st.session_state.pdf_order_column}'")
        
        # Show current mapping with option to change
        with st.expander("🔧 Adjust Column Mapping (if needed)", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🔢 Stop Numbers**")
                stop_col = st.selectbox(
                    "Column with route order (1, 2, 3...)",
                    driver_df.columns,
                    index=list(driver_df.columns).index(st.session_state.pdf_stop_column),
                    key="pdf_stop_selector"
                )
                st.caption(f"Sample: {driver_df[stop_col].head(3).tolist()}")
                
                # Update session state if changed
                if stop_col != st.session_state.pdf_stop_column:
                    st.session_state.pdf_stop_column = stop_col
            
            with col2:
                st.markdown("**📦 Order Reference**")
                order_col = st.selectbox(
                    "Column with order numbers/IDs",
                    driver_df.columns,
                    index=list(driver_df.columns).index(st.session_state.pdf_order_column),
                    key="pdf_order_selector"
                )
                st.caption(f"Sample: {driver_df[order_col].head(3).tolist()}")
                
                # Update session state if changed
                if order_col != st.session_state.pdf_order_column:
                    st.session_state.pdf_order_column = order_col
            
            with col3:
                st.markdown("**👤 Driver Filter (optional)**")
                has_driver_col = st.checkbox(
                    "Filter by driver?", 
                    value=st.session_state.pdf_use_driver_filter,
                    key="pdf_use_driver_filter_checkbox"
                )
                # Update session state only if it changed
                if has_driver_col != st.session_state.pdf_use_driver_filter:
                    st.session_state.pdf_use_driver_filter = has_driver_col
                
                if has_driver_col:
                    # Auto-detect driver column if not set
                    if st.session_state.pdf_driver_column is None or st.session_state.pdf_driver_column not in driver_df.columns:
                        driver_col_options = [col for col in driver_df.columns if 'driver' in str(col).lower() or 'member' in str(col).lower() or 'assigned' in str(col).lower()]
                        if driver_col_options:
                            st.session_state.pdf_driver_column = driver_col_options[0]
                        else:
                            st.session_state.pdf_driver_column = driver_df.columns[0]
                    
                    driver_col = st.selectbox(
                        "Driver name column",
                        driver_df.columns,
                        index=list(driver_df.columns).index(st.session_state.pdf_driver_column),
                        key="pdf_driver_selector"
                    )
                    
                    if driver_col != st.session_state.pdf_driver_column:
                        st.session_state.pdf_driver_column = driver_col
                        st.session_state.pdf_selected_driver = None  # Reset selected driver
                    
                    unique_drivers = driver_df[driver_col].unique()
                    
                    # Auto-select previous driver if still available
                    driver_index = 0
                    if st.session_state.pdf_selected_driver in unique_drivers:
                        driver_index = list(unique_drivers).index(st.session_state.pdf_selected_driver)
                    
                    selected_driver = st.selectbox(
                        "Select driver:", 
                        unique_drivers,
                        index=driver_index,
                        key="pdf_selected_driver_selector"
                    )
                    st.session_state.pdf_selected_driver = selected_driver
                    
                    # Filter the dataframe by selected driver
                    driver_df = driver_df[driver_df[driver_col] == selected_driver]
        
        # Use the stored column selections
        stop_col = st.session_state.pdf_stop_column
        order_col = st.session_state.pdf_order_column
        
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
                        # Try multiple matching strategies
                        for order_ref in order_to_stop.keys():
                            # Exact match
                            if order_ref in page_text:
                                found_order = order_ref
                                break
                            # Try without # if order_ref starts with #
                            elif order_ref.startswith('#') and order_ref[1:] in page_text:
                                found_order = order_ref
                                break
                            # Try with # if order_ref doesn't start with #
                            elif not order_ref.startswith('#') and f"#{order_ref}" in page_text:
                                found_order = order_ref
                                break
                        
                        if found_order:
                            stop_num = order_to_stop[found_order]
                            matched_count += 1
                        else:
                            stop_num = "?"
                            unmatched_orders.append(f"Page {page_idx + 1}")
                        
                        # Create overlay with the stop number
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

def customer_communication_hub():
    """Unified customer communication hub with template library and multi-platform support."""

    st.header("💬 Customer Communication Hub")
    st.markdown("**Manage all customer messages and replies from one place**")

    # File paths for data storage
    templates_file = os.path.join(TEMPLATE_DIR, "message_templates.json")
    messages_file = os.path.join(MESSAGES_DIR, "conversations.json")
    api_config_file = os.path.join(TEMPLATE_DIR, "api_config.json")

    # Load or initialize data
    def load_message_templates():
        try:
            with open(templates_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_message_templates(templates):
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=4)

    def load_conversations():
        try:
            with open(messages_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Sample data for demo purposes
            return [
                {
                    "id": "msg_001",
                    "platform": "Email",
                    "customer_name": "John Smith",
                    "customer_contact": "john@example.com",
                    "subject": "Order Inquiry",
                    "message": "Hi, I'd like to check the status of my order #12345",
                    "timestamp": "2024-11-13 09:30:00",
                    "status": "unread",
                    "replies": []
                },
                {
                    "id": "msg_002",
                    "platform": "Facebook",
                    "customer_name": "Sarah Johnson",
                    "customer_contact": "@sarahj",
                    "subject": "Delivery Question",
                    "message": "What time will my delivery arrive today?",
                    "timestamp": "2024-11-13 10:15:00",
                    "status": "unread",
                    "replies": []
                }
            ]

    def save_conversations(conversations):
        with open(messages_file, 'w') as f:
            json.dump(conversations, f, indent=4)

    def load_api_config():
        try:
            with open(api_config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "email": {"configured": False, "provider": "outlook", "credentials": {}},
                "facebook": {"configured": False, "api_key": "", "page_id": ""},
                "instagram": {"configured": False, "api_key": "", "account_id": ""},
                "whatsapp": {"configured": False, "api_key": "", "phone_id": ""},
                "twitter": {"configured": False, "api_key": "", "api_secret": ""}
            }

    def save_api_config(config):
        with open(api_config_file, 'w') as f:
            json.dump(config, f, indent=4)

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Inbox", "📝 Templates Library", "🔌 API Configuration", "📊 Statistics"])

    # TAB 1: INBOX
    with tab1:
        st.subheader("Unified Inbox")

        conversations = load_conversations()

        # Filter options
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            platform_filter = st.selectbox(
                "Filter by Platform:",
                ["All"] + list(set([msg["platform"] for msg in conversations])),
                key="platform_filter"
            )

        with col2:
            status_filter = st.selectbox(
                "Filter by Status:",
                ["All", "unread", "replied", "resolved"],
                key="status_filter"
            )

        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        # Apply filters
        filtered_messages = conversations
        if platform_filter != "All":
            filtered_messages = [m for m in filtered_messages if m["platform"] == platform_filter]
        if status_filter != "All":
            filtered_messages = [m for m in filtered_messages if m["status"] == status_filter]

        st.markdown(f"**Showing {len(filtered_messages)} message(s)**")

        # Display messages
        if not filtered_messages:
            st.info("📭 No messages to display. Connect your platforms in the API Configuration tab.")
        else:
            for idx, msg in enumerate(filtered_messages):
                status_emoji = "🔵" if msg["status"] == "unread" else "✅" if msg["status"] == "replied" else "✔️"

                with st.expander(f"{status_emoji} [{msg['platform']}] {msg['customer_name']} - {msg['subject']}", expanded=(idx == 0)):
                    col_a, col_b = st.columns([3, 1])

                    with col_a:
                        st.markdown(f"**From:** {msg['customer_name']} ({msg['customer_contact']})")
                        st.markdown(f"**Time:** {msg['timestamp']}")
                        st.markdown(f"**Platform:** {msg['platform']}")

                    with col_b:
                        current_status = st.selectbox(
                            "Status:",
                            ["unread", "replied", "resolved"],
                            index=["unread", "replied", "resolved"].index(msg["status"]),
                            key=f"status_{msg['id']}"
                        )
                        if current_status != msg["status"]:
                            msg["status"] = current_status
                            save_conversations(conversations)
                            st.success("Status updated!")

                    st.markdown("---")
                    st.markdown("**Message:**")
                    st.info(msg["message"])

                    # Show reply history
                    if msg.get("replies"):
                        st.markdown("**Conversation History:**")
                        for reply in msg["replies"]:
                            st.markdown(f"**You** ({reply['timestamp']}):")
                            st.success(reply['text'])

                    st.markdown("---")
                    st.markdown("**Reply to Customer:**")

                    # Template selector for quick replies
                    templates = load_message_templates()
                    if templates:
                        col_t1, col_t2 = st.columns([3, 1])
                        with col_t1:
                            selected_template = st.selectbox(
                                "Quick Insert Template:",
                                ["None"] + list(templates.keys()),
                                key=f"template_select_{msg['id']}"
                            )
                        with col_t2:
                            if selected_template != "None":
                                if st.button("📋 Insert", key=f"insert_template_{msg['id']}", use_container_width=True):
                                    st.session_state[f"reply_text_{msg['id']}"] = templates[selected_template]["content"]
                                    st.rerun()

                    # Reply text area
                    reply_text = st.text_area(
                        "Your reply:",
                        value=st.session_state.get(f"reply_text_{msg['id']}", ""),
                        height=150,
                        key=f"reply_{msg['id']}",
                        placeholder="Type your reply here..."
                    )

                    col_r1, col_r2 = st.columns([1, 4])
                    with col_r1:
                        if st.button("📤 Send Reply", key=f"send_{msg['id']}", type="primary", use_container_width=True):
                            if reply_text.strip():
                                # Add reply to conversation
                                if "replies" not in msg:
                                    msg["replies"] = []
                                msg["replies"].append({
                                    "text": reply_text,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                msg["status"] = "replied"
                                save_conversations(conversations)

                                st.success("✅ Reply sent!")
                                st.info(f"💡 Note: This is a demo. Connect your {msg['platform']} API to send real messages.")

                                # Clear reply text
                                if f"reply_text_{msg['id']}" in st.session_state:
                                    del st.session_state[f"reply_text_{msg['id']}"]
                                st.rerun()
                            else:
                                st.error("Please enter a reply message.")

                    with col_r2:
                        if st.button("📝 Add Internal Note", key=f"note_{msg['id']}", use_container_width=True):
                            st.info("Internal notes feature - Coming soon!")

    # TAB 2: TEMPLATES LIBRARY
    with tab2:
        st.subheader("📝 Message Templates Library")
        st.markdown("Create and manage reusable message templates for quick replies")

        templates = load_message_templates()

        col_lib1, col_lib2 = st.columns([2, 1])

        with col_lib1:
            st.markdown("### Current Templates")

            if not templates:
                st.info("📋 No templates yet. Create your first template below!")
            else:
                for template_name, template_data in templates.items():
                    with st.expander(f"📄 {template_name}", expanded=False):
                        st.markdown(f"**Category:** {template_data.get('category', 'General')}")
                        st.markdown(f"**Created:** {template_data.get('created', 'N/A')}")
                        st.markdown("**Content:**")
                        st.info(template_data["content"])

                        col_t1, col_t2, col_t3 = st.columns(3)

                        with col_t1:
                            if st.button("✏️ Edit", key=f"edit_{template_name}", use_container_width=True):
                                st.session_state["editing_template"] = template_name
                                st.session_state["edit_template_content"] = template_data["content"]
                                st.session_state["edit_template_category"] = template_data.get("category", "General")
                                st.rerun()

                        with col_t2:
                            if st.button("📋 Copy", key=f"copy_{template_name}", use_container_width=True):
                                st.session_state["clipboard"] = template_data["content"]
                                st.success("Copied to clipboard!")

                        with col_t3:
                            if st.button("🗑️ Delete", key=f"del_{template_name}", use_container_width=True):
                                del templates[template_name]
                                save_message_templates(templates)
                                st.success(f"Template '{template_name}' deleted!")
                                st.rerun()

        with col_lib2:
            st.markdown("### Add/Edit Template")

            # Check if editing existing template
            if "editing_template" in st.session_state:
                st.info(f"✏️ Editing: **{st.session_state['editing_template']}**")
                template_name_input = st.text_input("Template Name:", value=st.session_state['editing_template'], key="edit_name")
                template_category = st.selectbox(
                    "Category:",
                    ["General", "Order Updates", "Delivery", "Support", "Greetings", "Apology", "Thank You", "Custom"],
                    index=["General", "Order Updates", "Delivery", "Support", "Greetings", "Apology", "Thank You", "Custom"].index(st.session_state.get("edit_template_category", "General")),
                    key="edit_cat"
                )
                template_content = st.text_area(
                    "Template Content:",
                    value=st.session_state.get("edit_template_content", ""),
                    height=200,
                    key="edit_content",
                    placeholder="Enter your message template here..."
                )

                col_save1, col_save2 = st.columns(2)
                with col_save1:
                    if st.button("💾 Save Changes", type="primary", use_container_width=True):
                        if template_name_input.strip() and template_content.strip():
                            # Remove old template if name changed
                            if template_name_input != st.session_state['editing_template']:
                                del templates[st.session_state['editing_template']]

                            templates[template_name_input] = {
                                "content": template_content,
                                "category": template_category,
                                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_message_templates(templates)

                            # Clear editing state
                            del st.session_state["editing_template"]
                            if "edit_template_content" in st.session_state:
                                del st.session_state["edit_template_content"]
                            if "edit_template_category" in st.session_state:
                                del st.session_state["edit_template_category"]

                            st.success("Template updated!")
                            st.rerun()
                        else:
                            st.error("Please fill in all fields.")

                with col_save2:
                    if st.button("❌ Cancel", use_container_width=True):
                        del st.session_state["editing_template"]
                        if "edit_template_content" in st.session_state:
                            del st.session_state["edit_template_content"]
                        if "edit_template_category" in st.session_state:
                            del st.session_state["edit_template_category"]
                        st.rerun()
            else:
                # Create new template
                template_name_input = st.text_input("Template Name:", placeholder="e.g., Order Confirmation")
                template_category = st.selectbox(
                    "Category:",
                    ["General", "Order Updates", "Delivery", "Support", "Greetings", "Apology", "Thank You", "Custom"]
                )
                template_content = st.text_area(
                    "Template Content:",
                    height=200,
                    placeholder="Enter your message template here...\n\nTip: Use placeholders like {customer_name}, {order_number} for personalization"
                )

                if st.button("➕ Create Template", type="primary", use_container_width=True):
                    if template_name_input.strip() and template_content.strip():
                        if template_name_input in templates:
                            st.error("Template name already exists. Choose a different name.")
                        else:
                            templates[template_name_input] = {
                                "content": template_content,
                                "category": template_category,
                                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_message_templates(templates)
                            st.success(f"Template '{template_name_input}' created!")
                            st.rerun()
                    else:
                        st.error("Please fill in all fields.")

        st.markdown("---")
        st.markdown("### 📦 Template Management")

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            if templates:
                # Export templates
                templates_json = json.dumps(templates, indent=4)
                st.download_button(
                    label="⬇️ Export All Templates",
                    data=templates_json,
                    file_name=f"message_templates_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with col_exp2:
            # Import templates
            uploaded_templates = st.file_uploader("⬆️ Import Templates", type=['json'], key="import_templates")
            if uploaded_templates:
                try:
                    imported = json.load(uploaded_templates)
                    templates.update(imported)
                    save_message_templates(templates)
                    st.success(f"Imported {len(imported)} template(s)!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing templates: {e}")

    # TAB 3: API CONFIGURATION
    with tab3:
        st.subheader("🔌 API Configuration")
        st.markdown("Connect your email and social media accounts to receive and send messages")

        api_config = load_api_config()

        st.info("💡 **Setup Instructions:** Check the `API_SETUP_GUIDE.md` file in your project folder for detailed instructions on obtaining API credentials.")

        # Email Configuration
        with st.expander("📧 Email (Outlook)", expanded=True):
            st.markdown("**Status:** " + ("✅ Connected" if api_config["email"]["configured"] else "❌ Not Connected"))

            email_provider = st.selectbox("Email Provider:", ["Outlook", "Gmail", "Custom SMTP"], key="email_provider")

            if email_provider == "Outlook":
                st.markdown("**Microsoft Graph API Configuration:**")
                client_id = st.text_input("Client ID:", value=api_config["email"]["credentials"].get("client_id", ""), type="password", key="outlook_client_id")
                client_secret = st.text_input("Client Secret:", value=api_config["email"]["credentials"].get("client_secret", ""), type="password", key="outlook_client_secret")
                tenant_id = st.text_input("Tenant ID:", value=api_config["email"]["credentials"].get("tenant_id", ""), key="outlook_tenant_id")

                if st.button("💾 Save Outlook Config", key="save_outlook"):
                    api_config["email"] = {
                        "configured": bool(client_id and client_secret and tenant_id),
                        "provider": "outlook",
                        "credentials": {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "tenant_id": tenant_id
                        }
                    }
                    save_api_config(api_config)
                    st.success("✅ Outlook configuration saved!")
                    st.rerun()

            elif email_provider == "Gmail":
                st.markdown("**Gmail API Configuration:**")
                st.info("📖 See API_SETUP_GUIDE.md for Gmail setup instructions")
                credentials_file = st.file_uploader("Upload credentials.json from Google Console", type=['json'], key="gmail_creds")

                if credentials_file and st.button("💾 Save Gmail Config"):
                    api_config["email"] = {
                        "configured": True,
                        "provider": "gmail",
                        "credentials": json.load(credentials_file)
                    }
                    save_api_config(api_config)
                    st.success("✅ Gmail configuration saved!")

        # Facebook Configuration
        with st.expander("📘 Facebook Messenger", expanded=False):
            st.markdown("**Status:** " + ("✅ Connected" if api_config["facebook"]["configured"] else "❌ Not Connected"))

            fb_api_key = st.text_input("Page Access Token:", value=api_config["facebook"].get("api_key", ""), type="password", key="fb_token")
            fb_page_id = st.text_input("Page ID:", value=api_config["facebook"].get("page_id", ""), key="fb_page_id")

            if st.button("💾 Save Facebook Config", key="save_fb"):
                api_config["facebook"] = {
                    "configured": bool(fb_api_key and fb_page_id),
                    "api_key": fb_api_key,
                    "page_id": fb_page_id
                }
                save_api_config(api_config)
                st.success("✅ Facebook configuration saved!")
                st.rerun()

        # Instagram Configuration
        with st.expander("📷 Instagram", expanded=False):
            st.markdown("**Status:** " + ("✅ Connected" if api_config["instagram"]["configured"] else "❌ Not Connected"))

            ig_api_key = st.text_input("Access Token:", value=api_config["instagram"].get("api_key", ""), type="password", key="ig_token")
            ig_account_id = st.text_input("Instagram Account ID:", value=api_config["instagram"].get("account_id", ""), key="ig_account")

            if st.button("💾 Save Instagram Config", key="save_ig"):
                api_config["instagram"] = {
                    "configured": bool(ig_api_key and ig_account_id),
                    "api_key": ig_api_key,
                    "account_id": ig_account_id
                }
                save_api_config(api_config)
                st.success("✅ Instagram configuration saved!")
                st.rerun()

        # WhatsApp Configuration
        with st.expander("💬 WhatsApp Business", expanded=False):
            st.markdown("**Status:** " + ("✅ Connected" if api_config["whatsapp"]["configured"] else "❌ Not Connected"))

            wa_api_key = st.text_input("API Key:", value=api_config["whatsapp"].get("api_key", ""), type="password", key="wa_token")
            wa_phone_id = st.text_input("Phone Number ID:", value=api_config["whatsapp"].get("phone_id", ""), key="wa_phone")

            if st.button("💾 Save WhatsApp Config", key="save_wa"):
                api_config["whatsapp"] = {
                    "configured": bool(wa_api_key and wa_phone_id),
                    "api_key": wa_api_key,
                    "phone_id": wa_phone_id
                }
                save_api_config(api_config)
                st.success("✅ WhatsApp configuration saved!")
                st.rerun()

        # Twitter/X Configuration
        with st.expander("🐦 Twitter / X", expanded=False):
            st.markdown("**Status:** " + ("✅ Connected" if api_config["twitter"]["configured"] else "❌ Not Connected"))

            tw_api_key = st.text_input("API Key:", value=api_config["twitter"].get("api_key", ""), type="password", key="tw_key")
            tw_api_secret = st.text_input("API Secret:", value=api_config["twitter"].get("api_secret", ""), type="password", key="tw_secret")

            if st.button("💾 Save Twitter Config", key="save_tw"):
                api_config["twitter"] = {
                    "configured": bool(tw_api_key and tw_api_secret),
                    "api_key": tw_api_key,
                    "api_secret": tw_api_secret
                }
                save_api_config(api_config)
                st.success("✅ Twitter configuration saved!")
                st.rerun()

        # Custom Platform
        st.markdown("---")
        st.markdown("### ➕ Add Custom Platform")

        with st.expander("Add New Platform Integration", expanded=False):
            new_platform_name = st.text_input("Platform Name:", placeholder="e.g., Telegram, Discord, LinkedIn")
            new_platform_api = st.text_input("API Key/Token:", type="password")
            new_platform_endpoint = st.text_input("API Endpoint:", placeholder="https://api.example.com")

            if st.button("➕ Add Platform", key="add_custom_platform"):
                if new_platform_name and new_platform_api:
                    api_config[new_platform_name.lower()] = {
                        "configured": True,
                        "api_key": new_platform_api,
                        "endpoint": new_platform_endpoint
                    }
                    save_api_config(api_config)
                    st.success(f"✅ {new_platform_name} added!")
                    st.rerun()
                else:
                    st.error("Please provide platform name and API key.")

        st.markdown("---")
        if st.button("🧪 Test All Connections", type="primary", use_container_width=True):
            st.info("🔄 Testing connections... (This feature will be activated once APIs are configured)")
            for platform, config in api_config.items():
                if config.get("configured"):
                    st.success(f"✅ {platform.title()}: Configuration found")
                else:
                    st.warning(f"⚠️ {platform.title()}: Not configured")

    # TAB 4: STATISTICS
    with tab4:
        st.subheader("📊 Communication Statistics")

        conversations = load_conversations()

        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

        with col_stat1:
            st.metric("Total Messages", len(conversations))

        with col_stat2:
            unread_count = len([m for m in conversations if m["status"] == "unread"])
            st.metric("Unread", unread_count)

        with col_stat3:
            replied_count = len([m for m in conversations if m["status"] == "replied"])
            st.metric("Replied", replied_count)

        with col_stat4:
            templates = load_message_templates()
            st.metric("Templates", len(templates))

        st.markdown("---")

        # Platform breakdown
        st.markdown("### Messages by Platform")
        platform_counts = {}
        for msg in conversations:
            platform = msg["platform"]
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        if platform_counts:
            df_platforms = pd.DataFrame(list(platform_counts.items()), columns=["Platform", "Messages"])
            st.bar_chart(df_platforms.set_index("Platform"))
        else:
            st.info("No message data available yet.")

        st.markdown("---")

        # Recent activity
        st.markdown("### Recent Activity")
        recent_messages = sorted(conversations, key=lambda x: x["timestamp"], reverse=True)[:5]

        for msg in recent_messages:
            st.markdown(f"**{msg['timestamp']}** - [{msg['platform']}] {msg['customer_name']}: {msg['subject']}")

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

                # Create file hash and safe names early for consistent use
                import hashlib
                file_hash = hashlib.md5(uploaded_file.name.encode()).hexdigest()[:8]
                safe_tool_name = "".join(c for c in tool_name if c.isalnum() or c == "_")[:20]

                col_temp1, col_temp2 = st.columns([3, 1])
                
                with col_temp1:
                    # Create a safe key for template selector to avoid conflicts
                    template_selector_key = f"{safe_tool_name}_template_{file_hash}"
                    
                    # Add template compatibility info
                    def format_template_option(template_name):
                        if template_name == "<New Template>":
                            return template_name
                        
                        template_data = templates.get(template_name, {})
                        if 'columns' not in template_data:
                            return f"{template_name} ⚠️"
                        
                        matching_cols = len([col for col in template_data['columns'] if col in original_columns])
                        total_cols = len(template_data['columns'])
                        
                        if matching_cols == total_cols:
                            return f"{template_name} ✅ ({matching_cols}/{total_cols})"
                        elif matching_cols > 0:
                            return f"{template_name} ⚠️ ({matching_cols}/{total_cols})"
                        else:
                            return f"{template_name} ❌ (0/{total_cols})"
                    
                    selected_template_name = st.selectbox(
                        "**Select Template**", 
                        ["<New Template>"] + template_names,
                        key=template_selector_key,
                        format_func=format_template_option,
                        help="✅ = All columns match, ⚠️ = Some columns match, ❌ = No columns match"
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

                # Validate and filter template columns against current file columns
                if current_config and 'columns' in current_config:
                    # Only keep columns that exist in the current file
                    valid_template_cols = [col for col in current_config['columns'] if col in original_columns]
                    
                    if len(valid_template_cols) != len(current_config['columns']):
                        missing_cols = [col for col in current_config['columns'] if col not in original_columns]
                        st.warning(f"⚠️ Template '{selected_template_name}' contains columns not found in this file: {', '.join(missing_cols[:3])}")
                        if len(missing_cols) > 3:
                            st.info(f"And {len(missing_cols) - 3} more missing columns...")
                    
                    initial_cols = valid_template_cols if valid_template_cols else original_columns
                else:
                    initial_cols = original_columns

                st.write("Use the multiselect below to **reorder** and **remove/keep** columns.")

                # Create session state keys using the already defined variables
                session_key = f"{tool_name}_template_state_{file_hash}"
                file_key = f"{tool_name}_file_state_{file_hash}"
                template_key = f"{session_key}_template_name"
                
                # Smart session state management - only reset if truly necessary
                needs_reset = (
                    session_key not in st.session_state or  # No session state exists
                    st.session_state.get(file_key) != uploaded_file.name or  # Different file
                    st.session_state.get(template_key) != selected_template_name  # Different template
                )
                
                if needs_reset:
                    st.session_state[session_key] = initial_cols
                    st.session_state[file_key] = uploaded_file.name
                    st.session_state[template_key] = selected_template_name
                    
                    # Show info when template is applied automatically
                    if selected_template_name != "<New Template>" and current_config:
                        valid_count = len([col for col in current_config['columns'] if col in original_columns])
                        if valid_count > 0:
                            st.info(f"✅ Applied template '{selected_template_name}' with {valid_count} matching columns")
                        else:
                            st.warning(f"⚠️ Template '{selected_template_name}' applied but no matching columns found")

                # Create a safe key for the multiselect widget
                safe_file_name = "".join(c for c in uploaded_file.name.split('.')[0] if c.isalnum())[:15]
                safe_template = "".join(c for c in selected_template_name if c.isalnum())[:15] if selected_template_name != "<New Template>" else "new"
                
                multiselect_key = f"{safe_tool_name}_{safe_file_name}_{safe_template}_{file_hash}"

                # Final validation - ensure session state only contains valid columns
                valid_session_defaults = [col for col in st.session_state[session_key] if col in original_columns]
                if not valid_session_defaults or len(valid_session_defaults) != len(st.session_state[session_key]):
                    # Clean up invalid columns from session state
                    st.session_state[session_key] = valid_session_defaults if valid_session_defaults else original_columns

                new_column_order = st.multiselect(
                    '**Processed Column Order**:',
                    options=original_columns,
                    default=st.session_state[session_key],
                    key=multiselect_key,
                    help="Drag to reorder columns, remove columns by deselecting them"
                )
                
                # Update session state when user makes changes
                if new_column_order != st.session_state[session_key]:
                    st.session_state[session_key] = new_column_order

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
                                    # Try to detect driver name from the data
                                    driver_name = None
                                    
                                    # Look for common driver-related column names
                                    driver_columns = [col for col in processed_df.columns 
                                                    if any(keyword in col.lower() for keyword in 
                                                          ['driver', 'assigned', 'member', 'name', 'user'])]
                                    
                                    if driver_columns:
                                        # Use the first driver column found and get unique non-null values
                                        driver_col = driver_columns[0]
                                        unique_drivers = processed_df[driver_col].dropna().unique()
                                        
                                        if len(unique_drivers) == 1:
                                            # Single driver - use their name
                                            driver_name = str(unique_drivers[0]).strip()
                                        elif len(unique_drivers) > 1:
                                            # Multiple drivers - indicate this
                                            driver_name = f"Multiple_Drivers({len(unique_drivers)})"
                                        
                                        # Clean up driver name for filename
                                        if driver_name:
                                            driver_name = "".join(c for c in driver_name 
                                                                if c.isalnum() or c in (" ", "-", "_", "(", ")")).strip()
                                    
                                    saved_path = save_processed_file(processed_df, "driver_run_sheet", driver_name)
                                    
                                    if driver_name:
                                        st.success(f"✅ Saved for driver: **{driver_name.replace('_', ' ')}**")
                                        st.success("📁 You can now use this in 'PDF Label Numbering' → 'Use Saved File'")
                                    else:
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

# Apply time-based gradient theme
gradients = get_time_based_gradient()

# Custom CSS for time-based gradients and animations
st.markdown(f"""
<style>
    /* Time-based gradient background */
    .stApp {{
        background: {gradients['background']};
        animation: gradient-shift 15s ease infinite;
        background-size: 200% 200%;
    }}

    @keyframes gradient-shift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Ambient orbs */
    .stApp::before {{
        content: '';
        position: fixed;
        top: -10%;
        left: -10%;
        width: 500px;
        height: 500px;
        background: {gradients['orb1']};
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.6;
        animation: float-orb 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }}

    .stApp::after {{
        content: '';
        position: fixed;
        bottom: -10%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: {gradients['orb2']};
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.6;
        animation: float-orb 25s ease-in-out infinite reverse;
        pointer-events: none;
        z-index: 0;
    }}

    @keyframes float-orb {{
        0%, 100% {{ transform: translate(0, 0) scale(1); }}
        33% {{ transform: translate(30px, -30px) scale(1.1); }}
        66% {{ transform: translate(-20px, 20px) scale(0.9); }}
    }}

    /* Ensure content is above the orbs */
    .main .block-container {{
        position: relative;
        z-index: 1;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }}

    [data-testid="stSidebar"] .css-1d391kg {{
        background: rgba(255, 255, 255, 0.85);
    }}

    /* Enhanced cards and containers */
    div[data-testid="stExpander"] {{
        background: rgba(255, 255, 255, 0.6);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.4);
    }}

    /* Button enhancements */
    .stButton>button {{
        border-radius: 10px;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}

    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }}

    /* Smooth transitions */
    * {{
        transition: background-color 0.3s ease;
    }}

    /* Info boxes */
    .stAlert {{
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }}

    /* Headers with subtle glow */
    h1, h2, h3 {{
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    }}
</style>
""", unsafe_allow_html=True)

st.title("⚙️ Business Automation Platform")

st.markdown("Streamline your daily file processing with reusable templates.")

st.sidebar.title("🔧 Automation Tools")
selected_tool = st.sidebar.radio(
    "Select a Processor:",
    [DRIVER_KEY, KITCHEN_KEY, PDF_LABEL_KEY, COMMS_KEY],
    help="Choose which automation tool to use"
)

# Show tool descriptions
tool_descriptions = {
    DRIVER_KEY: "📋 Process driver run sheets - organize delivery routes and stops",
    KITCHEN_KEY: "🍳 Process kitchen order lists - organize food preparation orders",
    PDF_LABEL_KEY: "🏷️ Add route numbers to PDF labels automatically",
    COMMS_KEY: "💬 Unified inbox for all customer messages - Email, Facebook, Instagram, WhatsApp & more"
}

st.sidebar.markdown("---")
st.sidebar.info(tool_descriptions[selected_tool])

# Run the selected tool
if selected_tool == PDF_LABEL_KEY:
    pdf_label_numbering_tool()
elif selected_tool == COMMS_KEY:
    customer_communication_hub()
else:
    file_processor_tool(selected_tool)