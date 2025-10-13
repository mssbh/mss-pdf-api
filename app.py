#!/usr/bin/env python3
"""
Flask API for generating PDFs from HTML
This solves all client-side PDF generation issues
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

def clean_html(html_content):
    """Clean HTML and prepare it for PDF conversion"""
    # Remove any script tags
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # Add basic styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 1cm;
            }}
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                font-size: 12pt;
            }}
            h1, h2, h3 {{
                color: #1a1a1a;
                margin-top: 1em;
                margin-bottom: 0.5em;
            }}
            h2 {{
                font-size: 18pt;
                border-bottom: 2px solid #333;
                padding-bottom: 5px;
            }}
            h3 {{
                font-size: 14pt;
                margin-bottom: 10px;
            }}
            .info-section {{
                background-color: #f5f5f5;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 15px;
            }}
            .field {{
                margin-bottom: 10px;
            }}
            .field-label {{
                font-size: 10pt;
                color: #666;
                margin-bottom: 3px;
            }}
            .field-value {{
                font-weight: 500;
                font-size: 11pt;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f5f5f5;
                font-weight: bold;
            }}
            button {{
                display: none !important;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    return styled_html

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from HTML content
    Expects JSON: { "html": "<html>...</html>", "filename": "report.pdf" }
    """
    try:
        data = request.get_json()
        html_content = data.get('html', '')
        filename = data.get('filename', f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        if not html_content:
            return jsonify({'error': 'No HTML content provided'}), 400
        
        print(f"Generating PDF: {filename}")
        print(f"HTML content length: {len(html_content)} characters")
        
        # Clean and style HTML
        full_html = clean_html(html_content)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
            
        # Generate PDF
        HTML(string=full_html).write_pdf(tmp_path)
        
        print(f"PDF generated successfully: {tmp_path}")
        
        # Send file
        return send_file(
            tmp_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
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
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'MSS PDF Generation API',
        'version': '1.0.0',
        'endpoints': {
            'POST /generate-pdf': 'Generate PDF from HTML',
            'GET /health': 'Health check'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("MSS PDF Generation API Server")
    print("=" * 60)
    print("Server starting on http://0.0.0.0:5000")
    print("Endpoints:")
    print("  POST /generate-pdf - Generate PDF from HTML")
    print("  GET  /health       - Health check")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

