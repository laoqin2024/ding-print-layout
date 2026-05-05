================================================================================
EXPORT SUMMARY FOR GEMINI
================================================================================

All core components have been exported to the following files:

1. EXPORT_FOR_GEMINI_00_PROJECT_CONTEXT.txt
   - Project architecture overview
   - Directory structure
   - DingTalk integration details
   - Recent fixes and attachment background feature

2. EXPORT_FOR_GEMINI_01_frontend_print.js.txt
   - Frontend JavaScript for print preview
   - PDF.js integration
   - dd.config and dd.ready implementation
   - DingTalk native print API usage

3. EXPORT_FOR_GEMINI_02_backend_printing_routes.py.txt
   - Flask route handlers
   - /print_view endpoint
   - /open_approval endpoint
   - Designer vs legacy system routing logic

4. EXPORT_FOR_GEMINI_03_pdf_service.py.txt
   - Complete PDF generation service (971 lines)
   - PyMuPDF (fitz) integration
   - Signature overlay logic
   - Template rendering
   - Attachment handling

5. EXPORT_FOR_GEMINI_04_template_print.html.txt
   - Jinja2 template for legacy print preview
   - HTML structure
   - PDF.js canvas rendering
   - Print button and controls

6. EXPORT_FOR_GEMINI_05_template_designer_print.html.txt
   - Jinja2 template for designer-based print
   - Designer API integration
   - Real-time PDF generation

================================================================================
HOW TO USE THESE FILES
================================================================================

1. Copy each file's content to Gemini
2. Start with EXPORT_FOR_GEMINI_00_PROJECT_CONTEXT.txt for overview
3. Then provide the specific files Gemini needs to analyze

All files are located in:
/Volumes/MyDisk/App programs/dingtalk-h5-app/

You can view them with:
cat EXPORT_FOR_GEMINI_*.txt

Or copy individual files:
cat EXPORT_FOR_GEMINI_01_frontend_print.js.txt | pbcopy

================================================================================
KEY POINTS FOR GEMINI
================================================================================

1. **DingTalk Print API**:
   - Uses dd.biz.util.print() for native printing
   - Falls back to window.print() if unavailable
   - Requires dd.config initialization with jsApiList: ['biz.util.print']

2. **Two Print Systems**:
   - Legacy: Uses process_configs.json + pdf_service.py overlay
   - Designer: Uses print_layouts.json + PyMuPDF direct rendering

3. **Attachment Background**:
   - DingTalk returns fileId, not direct URL
   - Must call API to get download URL
   - Recently fixed (2026-05-04)

4. **PDF Generation**:
   - Backend: PyMuPDF (fitz) for PDF manipulation
   - Frontend: PDF.js for rendering in browser
   - Templates stored in templates/pdf_templates/

5. **Recent Issues Fixed**:
   - Attachment fileId → download URL conversion
   - cover_source_mode state synchronization
   - Manual enable preference (no auto-load)

================================================================================
