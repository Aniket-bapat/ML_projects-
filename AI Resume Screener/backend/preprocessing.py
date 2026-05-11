import re 
import spacy

nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    text = " ".join(text.split())

    doc = nlp(text)
    processed_text = []
    
    for token in doc:
        if not token.is_stop and not token.is_punct:
            processed_text.append(token.lemma_)
    return " ".join(processed_text)
