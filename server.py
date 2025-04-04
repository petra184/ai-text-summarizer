from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS if accessing from a different origin
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Serve index.html from the root directory
@app.route('/')
def serve_index():
    return send_from_directory('', 'index.html')

# Serve static files (CSS, JS)
@app.route('/<path:filename>')

def serve_static(filename):
    return send_from_directory('', filename)

def summarize():
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Process the file (Extract text from PDF, DOCX, etc. - implement logic here)
        summary = f"Summarized content from {file.filename}"

    elif "text" in request.form:
        text_content = request.form["text"]
        summary = f"Summarized text: {text_content[:100]}..."  # Example

    else:
        return jsonify({"error": "No text or file provided"}), 400

    return jsonify({"summary": summary})


    
if __name__ == '__main__':
    app.run(debug=True)

