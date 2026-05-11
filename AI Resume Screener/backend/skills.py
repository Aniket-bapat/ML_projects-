def load_skills():
    skills = []
    with open("../datasets/skills.txt", "r") as file:
        for line in file:
            skills.append(line.strip().lower())
    return skills

def extract_skills(text, skills):
    found_skills = set()
    for skill in skills:
        if skill in text:
            found_skills.add(skill)
            
    return found_skills
