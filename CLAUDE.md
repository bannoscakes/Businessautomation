# CLAUDE.md - AI Assistant Guide for Business Automation Platform

Last Updated: 2025-11-17

## Overview

This repository contains a **Business Automation Platform** - a Streamlit-based web application that provides five integrated tools for business operations. The entire application is contained in a single `app.py` file (2,622 lines) with minimal external dependencies.

**Primary Use Cases:**
- Delivery route planning and driver assignment
- Kitchen order processing and organization
- PDF label numbering for logistics
- Multi-platform customer communication management
- QR code generation with rich media landing pages

**Technology Stack:**
- Python 3.x with Streamlit framework
- Data processing: pandas, openpyxl
- PDF handling: PyPDF2, reportlab
- Media: qrcode, Pillow
- Storage: Local filesystem with JSON configs

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Repository Structure

```
/home/user/Businessautomation/
├── app.py                              # Main application (all code here)
├── requirements.txt                    # Python dependencies
├── README.md                          # User-facing documentation
├── API_SETUP_GUIDE.md                 # Comprehensive API setup guide
├── .gitignore                         # Git ignore rules
├── templates/                         # JSON configuration storage
│   ├── driver_run_sheet_processor.json
│   ├── kitchen_order_list_processor.json
│   ├── pdf_label_settings.json
│   ├── message_templates.json         # Runtime generated
│   ├── api_config.json               # Runtime generated
│   └── qr_database.json              # Runtime generated
├── saved_files/                      # Processed file outputs
├── messages/                         # Runtime: conversation data
├── qr_codes/                        # Runtime: generated QR images
└── qr_content/                      # Runtime: QR landing pages
```

## Codebase Architecture

### Single-File Monolithic Design

All application logic resides in `app.py`. The file is organized as follows:

**Lines 1-215: Imports and Core Utilities**
- Dependency imports with feature flags (PDF_SUPPORT, QR_SUPPORT)
- Template management functions: `get_template_path()`, `load_templates()`, `save_templates()`
- File operations: `save_processed_file()`, `get_saved_files()`, `load_saved_file()`
- Data processing: `clean_dataframe_for_display()`, `process_data()`

**Lines 216-697: PDF Label Numbering Tool**
- Function: `pdf_label_numbering_tool()`
- Matches order numbers from run sheets to PDF labels
- Configurable positioning, fonts, and colors
- Batch processing with driver filtering

**Lines 698-1258: Customer Communication Hub**
- Function: `customer_communication_hub()`
- Multi-platform messaging interface (Email, Facebook, Instagram, WhatsApp, Twitter/X)
- Template library for quick responses
- API configuration management
- Message statistics dashboard

**Lines 1259-2026: QR Code Content Hub**
- Function: `qr_code_content_hub()`
- Rich media QR code generator
- Supports video embeds, images, buttons, custom HTML
- Bulk generation capabilities
- Mobile-optimized landing pages

**Lines 2027-2466: Generic File Processor**
- Function: `file_processor_tool(tool_key, tool_name, tool_description)`
- Shared processing engine for Driver and Kitchen tools
- Template-based column mapping
- Multi-format support (CSV, Excel, ZIP)
- Smart header detection and validation

**Lines 2467-2622: Main Application**
- Streamlit page configuration
- Time-based gradient theming: `get_time_based_gradient()`
- Main navigation and tool routing
- Session state initialization

## Key Components and Features

### 1. Driver Run Sheet Processor (`DRIVER_KEY`)
**Purpose:** Organize delivery stops and assign to drivers

**Template Config:** `templates/driver_run_sheet_processor.json`

**Workflow:**
1. Upload CSV/Excel file with delivery data
2. Select or create template for column mapping
3. Process data with automatic organization
4. Download processed file with driver assignments
5. Files saved to `saved_files/` with timestamp

### 2. Kitchen Order List Processor (`KITCHEN_KEY`)
**Purpose:** Filter and organize food preparation orders

**Template Config:** `templates/kitchen_order_list_processor.json`

**Workflow:** Same as Driver Run Sheet but optimized for kitchen workflow

### 3. PDF Label Numbering Tool
**Purpose:** Add route numbers to PDF labels based on run sheets

**Template Config:** `templates/pdf_label_settings.json`

**Key Features:**
- Two-phase process: (1) Upload run sheet, (2) Upload PDFs
- Smart matching: Order numbers from Excel → PDF labels
- Configurable: Font family, size, position, color
- Batch processing: Process multiple drivers at once
- Preview: Shows how numbers will appear on PDFs

**Settings Structure:**
```json
{
  "font_size": 12,
  "x_position": 50,
  "y_position": 750,
  "font_family": "Helvetica-Bold",
  "text_color": {"r": 0, "g": 0, "b": 0}
}
```

### 4. Customer Communication Hub
**Purpose:** Unified inbox for multi-platform customer messaging

**Supported Platforms:**
- Email: Outlook (Microsoft Graph API), Gmail
- Social: Facebook Messenger, Instagram DM
- Messaging: WhatsApp Business API
- Social Media: Twitter/X DM

**Features:**
- Message template library with variables
- Conversation threading
- Platform-specific API configuration UI
- Message statistics and analytics
- Credential storage in `templates/api_config.json`

**Security Note:** API credentials are stored in local JSON files. Consider environment variables or secrets management for production.

### 5. QR Code Content Hub
**Purpose:** Generate QR codes with rich media landing pages

**Capabilities:**
- Video embeds (YouTube, Vimeo, direct upload)
- Image galleries
- Custom buttons with links
- Styled HTML pages
- Bulk generation from CSV
- QR code styling options

**Storage:**
- QR images: `qr_codes/`
- Landing pages: `qr_content/`
- Metadata: `templates/qr_database.json`

**Output:** Downloadable ZIP with QR codes and HTML files

## Development Conventions

### Session State Management
The app heavily relies on Streamlit's `st.session_state` for persistence across reruns.

**Key Session Variables:**
- `{tool_key}_uploaded_file` - Tracks uploaded file content
- `{tool_key}_templates` - Stores available templates
- `{tool_key}_selected_template` - Current template selection
- `{tool_key}_current_df` - Processed dataframe
- `message_templates` - Communication templates
- `conversations` - Customer message history
- `qr_database` - QR code metadata

**Reset Logic:** Session state is automatically cleared when files or templates change to prevent stale data issues.

### Template System
Templates store column mappings and settings as JSON files.

**Template Functions:**
```python
get_template_path(tool_key, template_type='processors')
load_templates(tool_key, template_type='processors')
save_templates(tool_key, templates, template_type='processors')
```

**Template Structure Example:**
```json
{
  "Template Name": {
    "columns": ["Column1", "Column2", "Column3"],
    "filters": {...},
    "settings": {...}
  }
}
```

### File Processing Pipeline
```
1. File Upload (CSV/Excel/ZIP)
2. Parse with pandas (multiple encoding attempts)
3. Detect headers (skip blank rows)
4. Template selection/creation
5. Column mapping validation
6. Data processing
7. Save to saved_files/ with timestamp
8. Provide download link
```

### Error Handling Pattern
```python
try:
    # Operation
    st.success("✅ Success message")
except SpecificException as e:
    st.error(f"❌ Error: {str(e)}")
    # Optional: Provide user guidance
```

**Best Practices:**
- Always show user-friendly error messages
- Use emojis for visual feedback (✅ ❌ ⚠️ ℹ️)
- Provide actionable guidance when errors occur
- Log detailed errors for debugging

### UI Organization Pattern
```python
# Tab-based organization
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    # Tab content

# Expandable sections for advanced options
with st.expander("Advanced Settings"):
    # Settings UI

# Multi-column layouts
col1, col2, col3 = st.columns(3)
```

### Data Cleaning
Always use `clean_dataframe_for_display()` before showing dataframes to users:
```python
display_df = clean_dataframe_for_display(df)
st.dataframe(display_df)
```

This handles:
- NaN → empty strings
- Data type conversions
- Display formatting

## Common Development Tasks

### Adding a New Tool

1. **Create Tool Function**
```python
def new_tool_name():
    """Tool description"""
    st.header("🎯 Tool Name")

    # Tool implementation
    # Use tabs for organization
    # Follow existing patterns for file upload
    # Implement session state management
    # Add error handling
```

2. **Add to Main Navigation** (line ~2597)
```python
selected_tool = st.sidebar.radio(
    "Select a tool:",
    ["Driver Run Sheet", "Kitchen Order", "PDF Labels", "Communication", "QR Codes", "New Tool"],
    index=0
)

if selected_tool == "New Tool":
    new_tool_name()
```

3. **Create Template File** (if needed)
```python
# templates/new_tool.json
{}
```

4. **Update Documentation**
- Add to README.md features list
- Update CLAUDE.md (this file)

### Modifying Template Structure

Templates are loaded/saved using these functions:
```python
# Load
templates = load_templates('TOOL_KEY')

# Modify
templates['New Template'] = {
    'columns': ['Col1', 'Col2'],
    'settings': {...}
}

# Save
save_templates('TOOL_KEY', templates)
```

### Adding API Integration

1. **Update `customer_communication_hub()`**
2. **Add API configuration UI in "API Configuration" tab**
3. **Store credentials in `api_config.json` via session state**
4. **Add platform to supported platforms list**
5. **Update `API_SETUP_GUIDE.md` with setup instructions**

### Modifying PDF Processing

PDF numbering logic is in `pdf_label_numbering_tool()`:
- Settings loaded from `templates/pdf_label_settings.json`
- Uses reportlab for PDF manipulation
- Font positioning is absolute (x, y coordinates)
- Color specified as RGB dict: `{"r": 0, "g": 0, "b": 0}`

**To change numbering appearance:**
```python
# Modify settings in UI or JSON:
{
    "font_size": 14,           # Increase size
    "x_position": 100,         # Move right
    "y_position": 700,         # Move down
    "font_family": "Helvetica", # Change font
    "text_color": {"r": 255, "g": 0, "b": 0}  # Red text
}
```

### Adding QR Code Features

QR generation is in `qr_code_content_hub()`:
- Individual creation: Tab 1
- Bulk creation: Tab 2
- QR database management: Tab 3

**QR Database Structure:**
```json
{
  "qr_unique_id": {
    "name": "QR Name",
    "created": "2025-11-17 10:30:00",
    "scans": 0,
    "content_type": "video|image|button",
    "content_data": {...}
  }
}
```

## Code Quality Guidelines

### When Making Changes

1. **Preserve User Experience**
   - Don't break existing workflows
   - Maintain emoji usage for feedback
   - Keep UI responsive and intuitive

2. **Follow Existing Patterns**
   - Use session state for persistence
   - Implement try/except error handling
   - Use tabs for multi-section UIs
   - Clean dataframes before display

3. **Maintain Single-File Structure**
   - All changes go in `app.py`
   - No need to create separate modules
   - Functions should be well-documented with docstrings

4. **Test Manually**
   - No automated testing exists
   - Test in Streamlit UI after changes
   - Verify file upload/download workflows
   - Check template persistence

5. **Update Documentation**
   - Modify this CLAUDE.md file
   - Update README.md if user-facing features change
   - Update API_SETUP_GUIDE.md for new integrations

### Security Considerations

**Current Security Posture:**
- API credentials stored in `templates/api_config.json` (local filesystem)
- No encryption at rest
- No authentication on the app itself
- Suitable for local/trusted network use

**For Production Deployment:**
- Use Streamlit secrets management
- Implement authentication (streamlit-authenticator)
- Use environment variables for sensitive data
- Enable HTTPS
- Review OWASP Top 10 vulnerabilities

**File Upload Security:**
- Currently accepts CSV/Excel/ZIP/PDF files
- Limited to 200MB (Streamlit default)
- No virus scanning
- Files processed in memory, saved locally

### Performance Considerations

**Current Limitations:**
- Large files (>100MB) may cause slowdowns
- PDF processing is synchronous (blocking)
- No caching for repeated operations
- All data processing happens on each rerun

**Optimization Opportunities:**
- Use `@st.cache_data` for expensive operations
- Implement pagination for large dataframes
- Add progress bars for long operations
- Consider background tasks for PDF processing

## Time-Based Theming

The app implements dynamic CSS gradients that change based on time of day:

**Time Periods:**
- Morning (6-12): Blue/teal gradients
- Afternoon (12-18): Orange/amber gradients
- Evening (18-22): Purple/pink gradients
- Night (22-6): Dark blue/indigo gradients

**Function:** `get_time_based_gradient()` (line ~2503)

**To modify:** Update gradient definitions in the function

## Git Workflow

**Branch Strategy:**
- Main branch: `main` (production-ready code)
- Feature branches: Use `claude/` prefix for AI-generated branches
- PR workflow: Merge via pull requests

**Recent Changes:**
- Import organization and cleanup
- Time-based gradient theming
- Code refactoring and optimization

**When Committing:**
```bash
git add .
git commit -m "Brief description of changes"
git push -u origin branch-name
```

## Testing Strategy

**Current State:** No automated tests

**Manual Testing Checklist:**
- [ ] App launches without errors
- [ ] All 5 tools load correctly
- [ ] File upload works (CSV, Excel, ZIP, PDF)
- [ ] Template save/load functions
- [ ] Data processing produces correct output
- [ ] Download links work
- [ ] Session state persists across interactions
- [ ] Error messages are user-friendly

**Future Recommendations:**
- Add pytest for unit tests
- Test file processing functions
- Mock API integrations
- UI testing with Selenium or Playwright

## Troubleshooting Guide

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**File encoding issues:**
- App tries multiple encodings: utf-8 → latin-1 → cp1252
- If all fail, check source file encoding

**Template not appearing:**
- Check `templates/` directory exists
- Verify JSON is valid (use JSON validator)
- Clear session state (refresh browser)

**PDF processing fails:**
- Ensure PDF_SUPPORT feature flag is True
- Check PyPDF2 and reportlab are installed
- Verify PDF is not password-protected

**QR codes not generating:**
- Ensure QR_SUPPORT feature flag is True
- Check qrcode and Pillow are installed
- Verify output directories exist

### Debug Mode

To enable detailed error messages:
```python
# In app.py, add after imports:
import streamlit as st
st.set_option('client.showErrorDetails', True)
```

## API Integration Reference

See `API_SETUP_GUIDE.md` for detailed setup instructions for:
- Microsoft Graph API (Outlook)
- Gmail API
- Facebook Graph API
- Instagram Graph API
- WhatsApp Business API
- Twitter/X API

**Quick Start:**
1. Navigate to "Customer Communication Hub"
2. Click "API Configuration" tab
3. Follow platform-specific setup guides
4. Enter credentials in UI
5. Test connection

## File Format Specifications

### CSV/Excel Upload Requirements
- Headers should be in first non-empty row
- Supported formats: `.csv`, `.xlsx`, `.xls`
- ZIP files should contain CSV/Excel files
- Column names should be consistent with templates

### PDF Label Format
- PDFs should have consistent layout
- Order numbers should be in predictable positions
- Single or multi-page PDFs supported
- Output PDFs maintain original formatting + numbers

### QR Content CSV Format
```csv
Name,Content Type,Video URL,Image URL,Button Text,Button Link
"My QR","video","https://youtube.com/watch?v=...","","",""
"Another QR","button","","","Click Here","https://example.com"
```

## Dependencies Management

**Core Dependencies:**
```
streamlit>=1.28.0      # Web framework
pandas>=1.5.0          # Data processing
openpyxl>=3.0.0        # Excel support
```

**Optional Dependencies** (feature flags):
```
PyPDF2>=3.0.0          # PDF reading (PDF_SUPPORT)
reportlab>=4.0.0       # PDF writing (PDF_SUPPORT)
qrcode>=7.4.0          # QR generation (QR_SUPPORT)
Pillow>=10.0.0         # Image processing (QR_SUPPORT)
```

**To add new dependency:**
1. Add to `requirements.txt`
2. Import with try/except and feature flag
3. Show user-friendly message if missing

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push to GitHub
2. Connect repository at share.streamlit.io
3. Select `app.py` as main file
4. Deploy

### Docker (not currently configured)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Production Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run with nohup
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

## Key Contact Points for AI Assistance

When working on this codebase, AI assistants should:

### ✅ Do:
- Maintain the single-file structure
- Follow existing naming conventions
- Use emojis in user-facing messages
- Implement comprehensive error handling
- Test changes in Streamlit UI
- Update documentation when adding features
- Preserve session state patterns
- Use tabs and expanders for UI organization

### ❌ Don't:
- Split into multiple files without explicit request
- Remove existing features without confirmation
- Change core workflow patterns
- Break template compatibility
- Modify `.gitignore` without reason
- Add dependencies without considering feature flags
- Skip error handling
- Forget to update CLAUDE.md after significant changes

### 🤔 Ask User Before:
- Major architectural changes
- Adding heavy dependencies
- Changing template structures (breaks compatibility)
- Modifying file storage locations
- Implementing authentication/security features
- Database migrations (currently file-based)

## Version History

- **2025-11-17**: Initial CLAUDE.md created
  - Documented current codebase structure
  - Added comprehensive development guidelines
  - Included all 5 tools and their specifications

## Future Improvement Opportunities

Based on codebase analysis, consider:

1. **Modularization**: Split `app.py` into modules (when codebase grows)
2. **Testing**: Add pytest, create test suite
3. **Type Hints**: Add Python type annotations
4. **Logging**: Implement proper logging instead of print statements
5. **Database**: Consider SQLite/PostgreSQL for data persistence
6. **Authentication**: Add user login system
7. **API Rate Limiting**: Implement for communication hub
8. **Async Processing**: Background tasks for PDF/QR generation
9. **CI/CD**: GitHub Actions for automated testing/deployment
10. **Docker**: Containerization for consistent deployment

---

**For questions or clarifications about this codebase, consult:**
1. This CLAUDE.md file
2. README.md for user-facing features
3. API_SETUP_GUIDE.md for API integrations
4. Source code comments in app.py
5. Git commit history for recent changes

**Last verified against:** commit 1303172 (2025-11-17)
