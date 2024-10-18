from transformers import RobertaTokenizer, RobertaModel
from sklearn.metrics.pairwise import cosine_similarity
import torch

# Initialize RoBERTa model and tokenizer
roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
roberta_model = RobertaModel.from_pretrained('roberta-base')

# Get sentence embeddings using RoBERTa
def get_sentence_embedding(sentence):
    inputs = roberta_tokenizer(sentence, return_tensors='pt', truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = roberta_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
    return embeddings

# Get embeddings for a list of keywords
def get_keywords_embeddings(keywords_list):
    embeddings = []
    for keywords in keywords_list:
        sentence = ' '.join(keywords)
        embeddings.append(get_sentence_embedding(sentence))
    return embeddings

# Calculate similarity scores between student and reference embeddings
def calculate_similarity_between_embeddings(student_embeddings, reference_embeddings):
    similarity_scores = []
    for student_emb in student_embeddings:
        student_scores = []
        for reference_emb in reference_embeddings:
            similarity_score = cosine_similarity(student_emb, reference_emb)
            student_scores.append(similarity_score[0][0])
        similarity_scores.append(student_scores)
    return similarity_scores
