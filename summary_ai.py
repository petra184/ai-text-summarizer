import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from summarizer import Summarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer


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
            return 30, 200 
        elif option == "medium":
            return 200, 450 
        else:
            return 450, 1000 
    
    def extractive(self, text, option):
        if not text or len(text.split()) < 20:
            return "Text is too short to summarize it."
        try:
            # Choose number of sentences based on option
            if option == "short":
                sent_count = 3
            elif option == "medium":
                sent_count = 5
            else:
                sent_count = 10

            # Parse and summarize using LexRank
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summarizer = LexRankSummarizer()
            summary = summarizer(parser.document, sentences_count=sent_count)

            # Join summarized sentences
            return "\n".join(str(sentence) for sentence in summary)

        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def abstractive(self, text, option):
        min_length, max_length = self.get_length(option)

        if not text or len(text.split()) < 20:
            return "Text is too short to summarize it."

        try:
            extractive_summary = self.extractive(text, option)

            if not extractive_summary or len(extractive_summary.split()) < 20:
                return "Text is too short after extraction to generate an abstractive summary."

            input_ids = self.bart_tokenizer.encode(
                extractive_summary, 
                return_tensors="pt", 
                max_length=1024,
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