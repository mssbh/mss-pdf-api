#!/usr/bin/env python3
"""
Flask API for generating PDFs from HTML with professional MSS template
"""

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from weasyprint import HTML, CSS
import tempfile
import os
from datetime import datetime
import base64
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MSS Logo as base64 (will be embedded in PDF)
MSS_LOGO_BASE64 = ""

def load_logo():
    """Load MSS logo and convert to base64"""
    global MSS_LOGO_BASE64
    try:
        logo_path = os.path.join(os.path.dirname(__file__), 'mss-logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode('utf-8')
                MSS_LOGO_BASE64 = f"data:image/png;base64,{logo_data}"
                print(f"✓ Logo loaded successfully")
        else:
            print(f"⚠ Logo not found at: {logo_path}")
    except Exception as e:
        print(f"⚠ Error loading logo: {e}")

def create_professional_pdf_html(report_data):
    """
    Create professional PDF HTML matching the sample template
    """
    
    # Extract report data
    report_number = report_data.get('reportNumber', 'N/A')
    site_name = report_data.get('siteName', 'N/A')
    contact_person = report_data.get('contactPerson', 'N/A')
    phone = report_data.get('phone', 'N/A')
    visit_type = report_data.get('visitType', 'N/A')
    problem_desc = report_data.get('problemDescription', 'N/A')
    solution_desc = report_data.get('solutionDescription', 'N/A')
    start_time = report_data.get('startTime', 'N/A')
    end_time = report_data.get('endTime', 'N/A')
    employee_name = report_data.get('employeeName', 'N/A')
    images = report_data.get('images', [])
    customer_signature = report_data.get('customerSignature', None)
    notes = report_data.get('notes', '')
    
    # Format dates
    try:
        if start_time and start_time != 'N/A':
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            visit_date = start_dt.strftime('%A, %d %B %Y, %I:%M:%S %p')
            start_time_formatted = start_dt.strftime('%d/%m/%Y, %I:%M:%S %p')
        else:
            visit_date = 'N/A'
            start_time_formatted = 'N/A'
            
        if end_time and end_time != 'N/A':
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            end_time_formatted = end_dt.strftime('%d/%m/%Y, %I:%M:%S %p')
        else:
            end_time_formatted = 'N/A'
    except:
        visit_date = start_time
        start_time_formatted = start_time
        end_time_formatted = end_time
    
    # Current timestamp for footer
    current_time = datetime.now().strftime('%A, %d %B %Y, %I:%M:%S %p')
    
    # Build images HTML
    images_html = ''
    if images:
        images_html = '<div class="section"><h3 class="section-title">Site Condition and Progress Photos</h3>'
        images_html += '<div class="images-grid">'
        for img in images[:6]:  # Limit to 6 images
            if img:
                images_html += f'<img src="{img}" alt="Site photo" class="site-image">'
        images_html += '</div>'
        if len(images) > 6:
            images_html += '<p class="note">See full page photos attached at end of PDF</p>'
        images_html += '</div>'
    
    # Build signature HTML
    signature_html = ''
    if customer_signature:
        signature_html = f'''
        <div class="section">
            <h3 class="section-title">Customer Signature</h3>
            <div class="signature-box">
                <img src="{customer_signature}" alt="Customer signature" class="signature-image">
                <p class="signature-name">{contact_person}</p>
                <p class="signature-date">{current_time}</p>
            </div>
        </div>
        '''
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 15mm 15mm 20mm 15mm;
                @bottom-center {{
                    content: "Page " counter(page) " of " counter(pages);
                }}
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Arial', 'Helvetica', sans-serif;
                font-size: 10pt;
                line-height: 1.4;
                color: #333;
            }}
            
            /* Header */
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 10px;
                padding-bottom: 10px;
                border-bottom: 3px solid #2E5090;
            }}
            
            .header-left {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo {{
                width: 60px;
                height: 60px;
                object-fit: contain;
            }}
            
            .header-center {{
                flex: 1;
                padding: 0 20px;
            }}
            
            .header-center p {{
                margin: 2px 0;
                font-size: 9pt;
                color: #555;
            }}
            
            .header-center p strong {{
                color: #333;
            }}
            
            .header-right {{
                text-align: right;
                font-size: 8pt;
                color: #555;
            }}
            
            .header-right p {{
                margin: 2px 0;
            }}
            
            /* Title */
            .report-title {{
                font-size: 18pt;
                font-weight: bold;
                color: #2E5090;
                margin: 15px 0 5px 0;
            }}
            
            .form-number {{
                font-size: 9pt;
                color: #666;
                margin-bottom: 8px;
            }}
            
            /* Two-column layout */
            .info-grid {{
                display: grid;
                grid-template-columns: 150px 1fr;
                gap: 4px 15px;
                margin-bottom: 8px;
                font-size: 9pt;
            }}
            
            .field-label {{
                font-weight: bold;
                color: #333;
                padding: 2px 0;
            }}
            
            .field-value {{
                color: #555;
                padding: 2px 0;
            }}
            
            /* Sections */
            .section {{
                margin: 10px 0;
                page-break-inside: avoid;
            }}
            
            .section-title {{
                font-size: 10pt;
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }}
            
            .section-content {{
                margin-left: 10px;
                color: #555;
                font-size: 9pt;
            }}
            
            .section-content ul {{
                margin-left: 20px;
                margin-top: 3px;
            }}
            
            .section-content li {{
                margin: 2px 0;
            }}
            
            /* Images */
            .images-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 5px;
                margin: 5px 0;
            }}
            
            .site-image {{
                width: 100%;
                height: 60px;
                object-fit: cover;
                border: 1px solid #ddd;
                border-radius: 2px;
            }}
            
            .note {{
                font-size: 8pt;
                color: #666;
                font-style: italic;
                margin-top: 5px;
            }}
            
            /* Signature */
            .signature-box {{
                margin: 5px 0;
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 2px;
                background-color: #f9f9f9;
                max-width: 300px;
                display: inline-block;
            }}
            
            .signature-image {{
                max-width: 150px;
                max-height: 50px;
                display: block;
                margin-bottom: 3px;
            }}
            
            .signature-name {{
                font-weight: bold;
                margin: 2px 0;
                font-size: 9pt;
            }}
            
            .signature-date {{
                font-size: 7pt;
                color: #666;
            }}
            
            /* Footer */
            .footer {{
                position: fixed;
                bottom: 0;
                left: 15mm;
                right: 15mm;
                padding-top: 10px;
                border-top: 3px solid #2E5090;
                font-size: 8pt;
                color: #666;
                display: flex;
                justify-content: space-between;
            }}
            
            .footer-left {{
                text-align: left;
            }}
            
            .footer-center {{
                text-align: center;
                font-weight: bold;
            }}
            
            .footer-right {{
                text-align: right;
            }}
            
            /* Page breaks */
            .page-break {{
                page-break-after: always;
            }}
        </style>
    </head>
    <body>
        <!-- Header -->
        <div class="header">
            <div class="header-left">
                {f'<img src="{MSS_LOGO_BASE64}" alt="MSS Logo" class="logo">' if MSS_LOGO_BASE64 else ''}
            </div>
            <div class="header-center">
                <p><strong>Organisation:</strong> Mechatronics Smart Solutions</p>
                <p><strong>Project:</strong> {site_name}</p>
                <p><strong>Team:</strong> MSS Field Service</p>
            </div>
            <div class="header-right">
                <p><strong>Report ID:</strong> {report_number}</p>
                <p><strong>Form Version:</strong> 1.0</p>
                <p><strong>Form created:</strong> {current_time}</p>
            </div>
        </div>
        
        <!-- Title -->
        <h1 class="report-title">Site Visit Report</h1>
        <p class="form-number"><strong>Automated Form Number:</strong> {report_number}</p>
        
        <!-- Main Information -->
        <div class="info-grid">
            <div class="field-label">Date of Visit</div>
            <div class="field-value">{visit_date}</div>
            
            <div class="field-label">Project</div>
            <div class="field-value">{site_name}</div>
            
            <div class="field-label">Site Visit Conducted by</div>
            <div class="field-value">{employee_name}</div>
            
            <div class="field-label">Report No.</div>
            <div class="field-value">{report_number}</div>
            
            <div class="field-label">Contact Person</div>
            <div class="field-value">{contact_person}</div>
            
            <div class="field-label">Phone Number</div>
            <div class="field-value">{phone}</div>
            
            <div class="field-label">Visit Type</div>
            <div class="field-value">{visit_type}</div>
        </div>
        
        <!-- Site Condition and Work in Progress -->
        <div class="section">
            <h3 class="section-title">Site Condition and Work in Progress</h3>
            <div class="section-content">
                <p><strong>Work in progress:</strong></p>
                <ul>
                    <li>{problem_desc}</li>
                </ul>
            </div>
        </div>
        
        <!-- Site Condition -->
        <div class="section">
            <h3 class="section-title">Site Condition</h3>
            <div class="section-content">
                <ul>
                    <li>{solution_desc}</li>
                </ul>
            </div>
        </div>
        
        <!-- Images -->
        {images_html}
        
        <!-- Observations -->
        {f'<div class="section"><h3 class="section-title">Observations</h3><div class="section-content"><ul><li>{notes}</li></ul></div></div>' if notes else ''}
        
        <!-- Time Information -->
        <div class="section">
            <h3 class="section-title">Time</h3>
            <div class="info-grid">
                <div class="field-label">Start Time</div>
                <div class="field-value">{start_time_formatted}</div>
                
                <div class="field-label">End Time</div>
                <div class="field-value">{end_time_formatted}</div>
            </div>
        </div>
        
        <!-- Signature -->
        {signature_html}
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-left">
                Generated with MSS Reports System
            </div>
            <div class="footer-center">
                Printed version is uncontrolled
            </div>
            <div class="footer-right">
                This PDF was created at<br>{current_time}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from report data
    Expects JSON with report data
    """
    try:
        data = request.get_json()
        
        # Check if this is the old format (HTML string) or new format (report data)
        if 'html' in data:
            # Old format - use the HTML directly
            html_content = data.get('html', '')
            filename = data.get('filename', f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
            
            if not html_content:
                return jsonify({'error': 'No HTML content provided'}), 400
            
            print(f"Generating PDF (legacy mode): {filename}")
            
        else:
            # New format - create professional PDF from report data
            report_data = data
            report_number = report_data.get('reportNumber', 'UNKNOWN')
            filename = f"MSS_Report_{report_number}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
            
            print(f"Generating PDF (professional template): {filename}")
            print(f"Report Number: {report_number}")
            
            html_content = create_professional_pdf_html(report_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
        
        # Generate PDF
        HTML(string=html_content).write_pdf(tmp_path)
        
        print(f"✓ PDF generated successfully: {tmp_path}")
        
        # Send file
        return send_file(
            tmp_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temp file after a delay
        try:
            if 'tmp_path' in locals():
                import threading
                def cleanup():
                    import time
                    time.sleep(2)
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                threading.Thread(target=cleanup).start()
        except:
            pass

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'PDF generation service is running',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'template': 'Professional MSS Template'
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'MSS PDF Generation API',
        'version': '2.0.0',
        'template': 'Professional MSS Template',
        'endpoints': {
            'POST /generate-pdf': 'Generate PDF from report data or HTML',
            'GET /health': 'Health check'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("MSS PDF Generation API Server v2.0")
    print("Professional Template with MSS Branding")
    print("=" * 60)
    
    # Load logo
    load_logo()
    
    print("Server starting on http://0.0.0.0:5000")
    print("Endpoints:")
    print("  POST /generate-pdf - Generate PDF from report data")
    print("  GET  /health       - Health check")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

