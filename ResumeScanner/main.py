from pypdf import PdfReader,PdfWriter
reader = PdfReader("LOR 2.pdf")
resume_text = ""
for page in reader.pages:
    resume_text += page.extract_text() + "\n"
reader2 = PdfReader("LOR 3.pdf")
job_description_text = ""
for page in reader2.pages:
    job_description_text += page.extract_text() + "\n"

def clean_text(text):
    return text.lower().replace("\n"," ")

def match_skills(resume,job_description):
    resume = clean_text(resume)
    job_description = clean_text(job_description)

    resume_skills = set(resume.split())
    job_description_skills = set(job_description.split())

    match = resume_skills & job_description_skills
    score = len(match)/len(job_description_skills) * 100

    return score, match

score, skills = match_skills(resume_text, job_description_text)

print(f"Match Score: {score:.2f}%")
print(f"Matched Words: {', '.join(skills)}")