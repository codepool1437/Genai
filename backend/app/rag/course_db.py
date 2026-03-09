# Mocked course database for Review 1.
# In Review 2, this is replaced by ChromaDB vector search using real embeddings.

COURSES: list[dict] = [
    # Python
    {"skill": "Python", "title": "Python for Everybody", "platform": "Coursera",
     "url": "https://www.coursera.org/specializations/python", "duration": "8 weeks", "level": "Beginner"},
    {"skill": "Python", "title": "Automate the Boring Stuff with Python", "platform": "Udemy",
     "url": "https://www.udemy.com/course/automate/", "duration": "10 weeks", "level": "Beginner"},
    {"skill": "Python", "title": "Python Data Science Handbook (free)", "platform": "GitHub / O'Reilly",
     "url": "https://jakevdp.github.io/PythonDataScienceHandbook/", "duration": "Self-paced", "level": "Intermediate"},

    # Machine Learning
    {"skill": "Machine Learning", "title": "Machine Learning Specialization", "platform": "Coursera (Andrew Ng)",
     "url": "https://www.coursera.org/specializations/machine-learning-introduction", "duration": "3 months", "level": "Intermediate"},
    {"skill": "Machine Learning", "title": "fast.ai – Practical Deep Learning", "platform": "fast.ai",
     "url": "https://course.fast.ai/", "duration": "2 months", "level": "Intermediate"},

    # Deep Learning
    {"skill": "Deep Learning", "title": "Deep Learning Specialization", "platform": "Coursera (Andrew Ng)",
     "url": "https://www.coursera.org/specializations/deep-learning", "duration": "5 months", "level": "Advanced"},
    {"skill": "Deep Learning", "title": "Zero to Mastery TensorFlow", "platform": "Udemy",
     "url": "https://www.udemy.com/course/tensorflow-developer-certificate-machine-learning-zero-to-mastery/", "duration": "3 months", "level": "Intermediate"},

    # Data Analysis
    {"skill": "Data Analysis", "title": "Google Data Analytics Certificate", "platform": "Coursera",
     "url": "https://www.coursera.org/professional-certificates/google-data-analytics", "duration": "6 months", "level": "Beginner"},
    {"skill": "Data Analysis", "title": "Data Analysis with Python", "platform": "freeCodeCamp",
     "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "duration": "4 weeks", "level": "Beginner"},

    # Statistics
    {"skill": "Statistics", "title": "Statistics with Python Specialization", "platform": "Coursera (UMich)",
     "url": "https://www.coursera.org/specializations/statistics-with-python", "duration": "3 months", "level": "Beginner"},
    {"skill": "Statistics", "title": "Khan Academy Statistics & Probability", "platform": "Khan Academy",
     "url": "https://www.khanacademy.org/math/statistics-probability", "duration": "Self-paced", "level": "Beginner"},

    # SQL
    {"skill": "SQL", "title": "SQL for Data Science", "platform": "Coursera (UC Davis)",
     "url": "https://www.coursera.org/learn/sql-for-data-science", "duration": "4 weeks", "level": "Beginner"},
    {"skill": "SQL", "title": "SQLZoo Interactive SQL Tutorial", "platform": "sqlzoo.net",
     "url": "https://sqlzoo.net/", "duration": "2 weeks", "level": "Beginner"},
    {"skill": "SQL", "title": "Mode SQL Tutorial", "platform": "Mode Analytics",
     "url": "https://mode.com/sql-tutorial/", "duration": "2 weeks", "level": "Intermediate"},

    # Web Development
    {"skill": "Web Development", "title": "The Complete Web Developer Bootcamp", "platform": "Udemy (Angela Yu)",
     "url": "https://www.udemy.com/course/the-complete-web-development-bootcamp/", "duration": "3 months", "level": "Beginner"},
    {"skill": "Web Development", "title": "Full Stack Open", "platform": "University of Helsinki",
     "url": "https://fullstackopen.com/en/", "duration": "4 months", "level": "Intermediate"},
    {"skill": "Web Development", "title": "The Odin Project", "platform": "theodinproject.com",
     "url": "https://www.theodinproject.com/", "duration": "6 months", "level": "Beginner"},

    # Cloud
    {"skill": "Cloud (AWS/GCP)", "title": "AWS Cloud Practitioner Essentials", "platform": "AWS Training",
     "url": "https://aws.amazon.com/training/learn-about/cloud-practitioner/", "duration": "6 weeks", "level": "Beginner"},
    {"skill": "Cloud (AWS/GCP)", "title": "Google Cloud Associate Engineer", "platform": "Coursera",
     "url": "https://www.coursera.org/professional-certificates/cloud-engineering-gcp", "duration": "3 months", "level": "Intermediate"},

    # DevOps
    {"skill": "DevOps / Docker", "title": "Docker & Kubernetes Bootcamp", "platform": "Udemy",
     "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/", "duration": "2 months", "level": "Intermediate"},
    {"skill": "DevOps / Docker", "title": "90 Days of DevOps (free)", "platform": "GitHub",
     "url": "https://github.com/MichaelCade/90DaysOfDevOps", "duration": "90 days", "level": "Intermediate"},

    # DSA
    {"skill": "Data Structures & Algorithms", "title": "DSA by freeCodeCamp", "platform": "YouTube",
     "url": "https://www.youtube.com/watch?v=8hly31xKli0", "duration": "6 hours", "level": "Beginner"},
    {"skill": "Data Structures & Algorithms", "title": "Neetcode 150", "platform": "neetcode.io",
     "url": "https://neetcode.io/", "duration": "2 months", "level": "Intermediate"},

    # NLP / GenAI
    {"skill": "NLP / GenAI", "title": "Hugging Face NLP Course (free)", "platform": "Hugging Face",
     "url": "https://huggingface.co/learn/nlp-course/", "duration": "6 weeks", "level": "Intermediate"},
    {"skill": "NLP / GenAI", "title": "LangChain for LLM Applications", "platform": "DeepLearning.AI",
     "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/", "duration": "2 weeks", "level": "Intermediate"},
]

# Job-to-required-skills mapping
ROLE_SKILL_MAP: dict[str, list[str]] = {
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Data Analysis", "Deep Learning"],
    "Data Analyst": ["Python", "SQL", "Data Analysis", "Statistics"],
    "Software Engineer": ["Python", "Data Structures & Algorithms", "Web Development", "SQL", "DevOps / Docker"],
    "ML Engineer": ["Python", "Machine Learning", "Deep Learning", "Cloud (AWS/GCP)", "DevOps / Docker"],
    "Full Stack Developer": ["Web Development", "SQL", "DevOps / Docker", "Cloud (AWS/GCP)"],
    "DevOps Engineer": ["DevOps / Docker", "Cloud (AWS/GCP)", "Python"],
    "Backend Developer": ["Python", "SQL", "DevOps / Docker", "Data Structures & Algorithms"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP / GenAI", "Cloud (AWS/GCP)"],
}


def retrieve_courses(target_role: str, current_skills: list[str]) -> list[dict]:
    """
    Retrieve relevant courses for target_role that the user hasn't already mastered.
    This is the mocked RAG retrieval step — in Review 2 replaced by ChromaDB semantic search.
    """
    required_skills = ROLE_SKILL_MAP.get(target_role, [s["skill"] for s in COURSES])
    current_lower = {s.strip().lower() for s in current_skills}
    skill_gaps = [s for s in required_skills if s.lower() not in current_lower]

    results = []
    for course in COURSES:
        if course["skill"] in skill_gaps:
            results.append(course)
    return results


def all_courses_as_context(courses: list[dict]) -> str:
    """Format courses as a numbered list for injection into LLM prompts."""
    if not courses:
        return "No courses found."
    lines = []
    for i, c in enumerate(courses, 1):
        lines.append(
            f"{i}. [{c['skill']}] {c['title']} — {c['platform']} | {c['duration']} | {c['level']}\n   URL: {c['url']}"
        )
    return "\n".join(lines)
