from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from summary_ai import *
import re
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/validate-url', methods=['POST'])
def validate_url():
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({"valid": False, "message": "No URL provided"})
    
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return jsonify({"valid": False, "message": "Invalid URL format"})
    except:
        return jsonify({"valid": False, "message": "Invalid URL format"})
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, timeout=5, headers=headers)
        
        if response.status_code >= 400:
            return jsonify({"valid": False, "message": f"URL returned status code {response.status_code}"})
        
        return jsonify({"valid": True})
    except requests.exceptions.RequestException:
        return jsonify({"valid": False, "message": f"Could not access URL"})


@app.route('/summarize', methods=['POST'])
def summarize():
    summary_type = request.form.get("type", "extractive")
    summary_length = request.form.get("length", "medium")

    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        try:
            print(file)
            text = pdf_to_text(file)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif "text" in request.form:
        text = request.form["text"]

    elif "url" in request.form:
        url = request.form["url"]
        try:
            text = url_to_text(url)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No text, file, or URL provided"}), 400
    
    if len(text.split()) < 20:
        return jsonify({"error": "Text is too short to summarize it."}), 400
    
    try:
        model = get_model()
        if summary_type == "extractive":
            summary = model.extractive(text, summary_length)
        else:
            clean_text = cleaning_text(text)
            summary = model.abstractive(clean_text, summary_length)
        
        return jsonify({"summary": summary})
    
    except Exception as e:
        print(f"Summary generation failed: {e}")
        return jsonify({"error": f"Error generating summary: {str(e)}"}), 500


def pdf_to_text(file) -> str:
    try:
        file_stream = BytesIO(file.read())
        reader = PdfReader(file_stream)
        all_text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            all_text += page_text.replace("\n", " ")
        clean_text = " ".join(all_text.split())
        return clean_text
    except Exception as e:
        print(f"PDF parsing error: {e}")
        raise

def url_to_text(url) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # exception for HTTP errors
    
    # Parsing  HTML content
    parsing = BeautifulSoup(response.text, 'html.parser')
    
    for script in parsing(["script", "style", "header", "footer", "nav"]):
        script.extract()
    
    text = parsing.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def cleaning_text(text):
    patterns = [
        r"(?i)click here to.*", 
        r"(?i)read more.*",     
        r"(?i)subscribe.*",    
        r"(?i)follow us.*",
        r"(?i)Source.*",
        r"(?i)Visit.*",
        r"(?i)www.*",          
        r"(?i)advertisement",   
        r"\b\d{1,2}:\d{2}\s*(AM|PM)?\b",  
        r"\[[^\]]*\]",          
        r"http\S+",            
        r"\s{2,}",              
        r"(?i)Ad.*",
        r"(?i)Feedback.*",  
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text)

    return text.strip()

if __name__ == '__main__':
    app.run(debug=True)