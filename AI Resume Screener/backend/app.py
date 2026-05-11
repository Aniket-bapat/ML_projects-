from fastapi import UploadFile
from fastapi.params import File

from fastapi import FastAPI
import shutil

from parser import extract_text_from_pdf
from preprocessing import preprocess_text
from skills import load_skills, extract_skills
from matcher import calculate_similarity

app = FastAPI()

skills_db = load_skills()


@app.post("/upload")

async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = ""
):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    raw_text = extract_text_from_pdf(file_path)

    # Preprocess
    processed_resume = preprocess_text(raw_text)

    processed_jd = preprocess_text(job_description)
    print(processed_resume)
    # Extract skills
    found_skills = extract_skills(processed_resume, skills_db)

    # Similarity
    score = calculate_similarity(
        processed_resume,
        processed_jd
    )

    return {
        "match_score": round(score, 2),
        "skills_found": found_skills
    }