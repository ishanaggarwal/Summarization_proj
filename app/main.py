# app/main.py
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
from .processor import extract_from_pdf, extract_from_docx, extract_from_image
from .extractor import extract_skills, extract_location, extract_degree, classify_domain
from .embedder import embed_text
from .vectorstore import add_profile, search
import shutil, os

app = FastAPI()

class Profile(BaseModel):
    id: str
    skills: List[str]
    location: Optional[str] = None
    degree: Optional[str] = None
    domain: str

@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    # save temporarily
    suffix = os.path.splitext(file.filename)[1].lower()
    tmp = f"/tmp/{file.filename}"
    with open(tmp, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # text extraction
    if suffix == ".pdf":
        text = extract_from_pdf(tmp)
    elif suffix in {".docx",".doc"}:
        text = extract_from_docx(tmp)
    else:
        text = extract_from_image(tmp)

    # field extraction
    skills   = extract_skills(text)
    loc      = extract_location(text)
    degree   = extract_degree(text)
    domain   = classify_domain(text)

    # embedding & index
    emb = embed_text(text)
    profile_id = os.path.basename(tmp)
    add_profile(profile_id, emb, {
        "skills": skills,
        "location": loc,
        "degree": degree,
        "domain": domain
    })

    return Profile(id=profile_id, skills=skills, location=loc, degree=degree, domain=domain)

@app.get("/search/")
def search_profiles(q: str, k: int = 5):
    emb = embed_text(q)
    return search(emb, top_k=k)
