from PyPDF2 import PdfReader
import re
import spacy

reader = PdfReader("resume.pdf")

text = ""

for page in reader.pages:
    text += page.extract_text()
text = text.lower()


text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
text = " ".join(text.split())
print(text)


nlp = spacy.load("en_core_web_sm")

doc = nlp(text)

for token in doc:
    print(token.text, token.pos_)

skills = []
with open("skills.txt", "r") as f:
    for line in f:
        skills.append(line.strip().lower())

found_skills = set()
for token in doc:
    if token.lemma_ in skills:
        found_skills.add(token.text)

print("Skills found in resume:")
for skill in found_skills:
    print(skill)