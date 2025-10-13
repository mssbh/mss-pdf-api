# MSS PDF Generation API

Simple Flask API for generating PDFs from HTML content.

## Files

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration for deployment

## Deployment

See `RENDER_DEPLOYMENT_GUIDE.md` for step-by-step instructions to deploy on Render.com.

## Local Testing

```bash
pip install -r requirements.txt
python app.py
```

API will be available at `http://localhost:5000`

## Endpoints

- `POST /generate-pdf` - Generate PDF from HTML
- `GET /health` - Health check
- `GET /` - API information

## Usage

```javascript
const response = await fetch('https://your-api-url.com/generate-pdf', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    html: '<h1>Report</h1><p>Content...</p>',
    filename: 'report.pdf'
  })
});

const blob = await response.blob();
// Download the PDF
```

