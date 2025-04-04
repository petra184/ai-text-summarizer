import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from summarizer import Summarizer

class SummarizationModel:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        print(f"Initializing summarization model on {self.device}")
        
        # Initialize BERT model for extractive summarization
        self.bert_model = Summarizer()
                
        # Load BART tokenizer and model
        self.bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn").to(self.device)

    def get_length(self, option):
        if option == "short":
            return 30, 100 
        elif option == "medium":
            return 100, 250 
        else:
            return 250, 500 
    
    def extractive(self, text, option):
        if not text or len(text.split()) < 20:
            return "Text is too short to summarize it."

        try:
            summary_output = self.bert_model.get_summary(text, "long")

            if option=="short":
                top_n = 5
            elif option=="medium":
                top_n = 9
            else:
                top_n = 15
                
            summary_output = sorted(summary_output, key=lambda x: x['total_score'], reverse=True)[:top_n]

            summary_output = sorted(summary_output, key=lambda x: x['order'])
            summary_sentences = [item['sentence'] for item in summary_output]
            return "\n".join(summary_sentences)

        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def abstractive(self, text, option):
        min_length, max_length = self.get_length(option)
        
        if not text or len(text.split()) < 20:
            return "Text is too short to summarize it."
        try:
            if len(text) > 10000:
                text = text[:10000] + "..."

            input_ids = self.bart_tokenizer.encode(
                text, 
                return_tensors="pt", 
                max_length=1024,  # BART allows larger input size than T5
                truncation=True
            ).to(self.device)
            
            summary_ids = self.bart_model.generate(
                input_ids,
                max_length=max_length,
                min_length=min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            return self.bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        except Exception as e:
            print(f"Error in abstractive summarization: {str(e)}")
            return f"Error generating summary: {str(e)}"

# Create a singleton instance
_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        _model_instance = SummarizationModel()
    return _model_instance