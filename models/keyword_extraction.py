from transformers import BertTokenizer, BertModel
import torch
from nltk.corpus import stopwords
from nltk import pos_tag

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Load stopwords
stop_words = set(stopwords.words('english'))

# Extract BERT tokens from text
def extract_keywords(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    input_ids = inputs['input_ids']
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    return tokens

# Filter keywords to remove stopwords and subwords
def filter_keywords(keywords):
    filtered_keywords = [word for word in keywords if word.lower() not in stop_words and not word.startswith("##")]
    
    # Keep only nouns and verbs (POS tagging)
    pos_filtered_keywords = [word for word, pos in pos_tag(filtered_keywords) if pos.startswith('NN') or pos.startswith('VB')]
    
    return pos_filtered_keywords

# Extract and filter keywords from segmented student answers
def extract_and_store_keywords(segmented_answers):
    all_keywords = []
    for answer in segmented_answers:
        keywords = extract_keywords(answer)
        filtered_keywords = filter_keywords(keywords)
        all_keywords.append(filtered_keywords)
    
    return all_keywords
