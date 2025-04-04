# 🧠 AI RESEARCH PAPER AND NEWS ARTICLES SUMMARIZER
A simple and efficient web-based tool for summarizing AI research papers (PDFs) and news articles (URLs) using advanced NLP models. Powered by Flask and state-of-the-art transformer models like BART and BERT.

---

## 🚀 Features
- Summarize AI research papers from uploaded PDFs
- Summarize news articles from online URLs
- Built using Flask, PyTorch, Hugging Face Transformers, and more
- Lightweight and fast with a clean web interface

---

## 🛠️ Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-summarizer.git
```

### 2. Create a Virtual Environment
#### On Windows (Command Prompt)
```bash
python -m venv venv
venv\Scripts\activate
```
#### On macOS / Linux (Terminal)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install flask flask-cors PyPDF2 requests beautifulsoup4 torch transformers bert-extractive-summarizer

```

### 4. Navigate into the Project Directory and Run the Server
```bash
cd ai-text-summarizer
python server.py
```
