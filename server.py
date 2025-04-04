from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Serve index.html
@app.route('/')
def serve_index():
    return render_template('index.html')

# Validate URL route
@app.route('/validate-url', methods=['POST'])
def validate_url():
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({"valid": False, "message": "No URL provided"})
    
    # Check if URL has a valid format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return jsonify({"valid": False, "message": "Invalid URL format"})
    except:
        return jsonify({"valid": False, "message": "Invalid URL format"})
    
    # Check if URL is accessible
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, timeout=5, headers=headers)
        
        # Check if response is successful
        if response.status_code >= 400:
            return jsonify({"valid": False, "message": f"URL returned status code {response.status_code}"})
        
        return jsonify({"valid": True})
    except requests.exceptions.RequestException as e:
        return jsonify({"valid": False, "message": f"Could not access URL: {str(e)}"})

# Summarize route
@app.route('/summarize', methods=['POST'])
def summarize():
    summary_type = request.form.get("type", "extractive")
    summary_length = request.form.get("length", "medium")

    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        try:
            text = pdf_to_text(file)
            # In a real implementation, you would pass this text to your AI model
            return jsonify({"summary": {text}})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif "text" in request.form:
        text = request.form["text"]
        # In a real implementation, you would pass this text to your AI model
        return jsonify({"summary": text})

    elif "url" in request.form:
        url = request.form["url"]
        try:
            text = extract_text_from_url(url)
            # In a real implementation, you would pass this text to your AI model
            return jsonify({"summary": text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": "No text, file, or URL provided"}), 400

def pdf_to_text(file) -> str:
    file_stream = BytesIO(file.read())
    reader = PdfReader(file_stream)

    all_text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        all_text += page_text.replace("\n", " ")

    clean_text = " ".join(all_text.split())  # remove extra whitespace
    return clean_text

def extract_text_from_url(url) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.extract()
    
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    
    # Remove blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    # Clean up text - remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

if __name__ == '__main__':
    app.run(debug=True)