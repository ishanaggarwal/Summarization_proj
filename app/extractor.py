# app/extractor.py
import spacy
nlp = spacy.load("en_core_web_sm")

# simple keyword lists
GENERAL_SKILLS = {"leadership","communication","teamwork"}
TECH_SKILLS    = {"python","java","react","aws"}

DEGREES = ["Bachelor","Master","PhD","B\.Sc","M\.Sc"]

def extract_skills(text: str):
    doc = nlp(text.lower())
    found = set()
    for token in doc:
        if token.text in TECH_SKILLS or token.text in GENERAL_SKILLS:
            found.add(token.text)
    return list(found)

def extract_location(text: str):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    return None

def extract_degree(text: str):
    for deg in DEGREES:
        if deg.lower() in text.lower():
            return deg
    return None

def classify_domain(text: str):
    txt = text.lower()
    if "product manager" in txt or "roadmap" in txt:
        return "Product Management"
    if "scalable" in txt or "api" in txt:
        return "Engineering"
    return "Other"
