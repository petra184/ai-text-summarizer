from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Serve index.html
@app.route('/')
def serve_index():
    return render_template('index.html')

# Summarize route
@app.route('/summarize', methods=['POST'])
def summarize():
    summary_type = request.form.get("type", "not provided")
    summary_length = request.form.get("length", "not provided")

    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        try:
            text = pdf_to_text(file)
            return jsonify({"summary": f"{text}"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif "text" in request.form:
        text_content = request.form["text"]
        return jsonify({"summary": f"{text_content}"})

    else:
        return jsonify({"error": "No text or file provided"}), 400

def pdf_to_text(file) -> str:
    file_stream = BytesIO(file.read())
    reader = PdfReader(file_stream)

    all_text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        all_text += page_text.replace("\n", " ")

    clean_text = " ".join(all_text.split())  # remove extra whitespace
    return clean_text
    

if __name__ == '__main__':
    app.run(debug=True)
