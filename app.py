import streamlit as st
import ollama
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Roadmap Generator",
    page_icon="🗺️",
    layout="wide",
)

# ── Mocked Course Database (Phase 1 PoC) ─────────────────────────────────────
# In the final version this will be replaced by ChromaDB vector search.
COURSE_DATABASE = {
    "Python": [
        {"title": "Python for Everybody", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python", "duration": "8 weeks", "level": "Beginner"},
        {"title": "Automate the Boring Stuff with Python", "platform": "Udemy", "url": "https://www.udemy.com/course/automate/", "duration": "10 weeks", "level": "Beginner"},
    ],
    "Machine Learning": [
        {"title": "Machine Learning Specialization", "platform": "Coursera (Andrew Ng)", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "duration": "3 months", "level": "Intermediate"},
        {"title": "fast.ai – Practical Deep Learning", "platform": "fast.ai", "url": "https://course.fast.ai/", "duration": "2 months", "level": "Intermediate"},
    ],
    "Data Analysis": [
        {"title": "Google Data Analytics Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-data-analytics", "duration": "6 months", "level": "Beginner"},
        {"title": "Data Analysis with Python", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "duration": "4 weeks", "level": "Beginner"},
    ],
    "Web Development": [
        {"title": "The Complete Web Developer Bootcamp", "platform": "Udemy (Angela Yu)", "url": "https://www.udemy.com/course/the-complete-web-development-bootcamp/", "duration": "3 months", "level": "Beginner"},
        {"title": "Full Stack Open", "platform": "University of Helsinki", "url": "https://fullstackopen.com/en/", "duration": "4 months", "level": "Intermediate"},
    ],
    "SQL": [
        {"title": "SQL for Data Science", "platform": "Coursera (UC Davis)", "url": "https://www.coursera.org/learn/sql-for-data-science", "duration": "4 weeks", "level": "Beginner"},
        {"title": "SQLZoo Interactive SQL", "platform": "sqlzoo.net", "url": "https://sqlzoo.net/", "duration": "2 weeks", "level": "Beginner"},
    ],
    "Cloud (AWS/GCP)": [
        {"title": "AWS Cloud Practitioner Essentials", "platform": "AWS Training", "url": "https://aws.amazon.com/training/learn-about/cloud-practitioner/", "duration": "6 weeks", "level": "Beginner"},
        {"title": "Google Cloud Associate Engineer", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/cloud-engineering-gcp", "duration": "3 months", "level": "Intermediate"},
    ],
    "Data Structures & Algorithms": [
        {"title": "DSA by freeCodeCamp", "platform": "freeCodeCamp (YouTube)", "url": "https://www.youtube.com/watch?v=8hly31xKli0", "duration": "6 hours", "level": "Beginner"},
        {"title": "Neetcode 150 DSA", "platform": "neetcode.io", "url": "https://neetcode.io/", "duration": "2 months", "level": "Intermediate"},
    ],
    "DevOps / Docker": [
        {"title": "Docker & Kubernetes Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/", "duration": "2 months", "level": "Intermediate"},
    ],
    "Statistics": [
        {"title": "Statistics with Python Specialization", "platform": "Coursera (UMich)", "url": "https://www.coursera.org/specializations/statistics-with-python", "duration": "3 months", "level": "Beginner"},
    ],
    "Deep Learning": [
        {"title": "Deep Learning Specialization", "platform": "Coursera (Andrew Ng)", "url": "https://www.coursera.org/specializations/deep-learning", "duration": "5 months", "level": "Advanced"},
    ],
}

# ── Role-to-Skills mapping ────────────────────────────────────────────────────
ROLE_SKILL_MAP = {
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Data Analysis", "Deep Learning"],
    "Data Analyst": ["Python", "SQL", "Data Analysis", "Statistics"],
    "Software Engineer": ["Python", "Data Structures & Algorithms", "Web Development", "SQL", "DevOps / Docker"],
    "ML Engineer": ["Python", "Machine Learning", "Deep Learning", "Cloud (AWS/GCP)", "DevOps / Docker"],
    "Full Stack Developer": ["Web Development", "SQL", "DevOps / Docker", "Cloud (AWS/GCP)"],
    "DevOps Engineer": ["DevOps / Docker", "Cloud (AWS/GCP)", "Python"],
    "Backend Developer": ["Python", "SQL", "DevOps / Docker", "Data Structures & Algorithms"],
}


def get_relevant_courses(target_role: str, current_skills: list[str]) -> list[dict]:
    """Retrieve courses relevant to the target role, filtering out skills the user already has."""
    relevant_skills = ROLE_SKILL_MAP.get(target_role, list(COURSE_DATABASE.keys()))
    # Filter out skills user already has (case-insensitive)
    current_lower = [s.strip().lower() for s in current_skills]
    skill_gaps = [s for s in relevant_skills if s.lower() not in current_lower]

    courses = []
    for skill in skill_gaps:
        if skill in COURSE_DATABASE:
            for course in COURSE_DATABASE[skill]:
                courses.append({"skill": skill, **course})
    return courses


def build_prompt(current_role: str, current_skills: list[str], target_role: str,
                 time_per_week: int, courses: list[dict]) -> str:
    course_text = "\n".join(
        f"- [{c['skill']}] {c['title']} on {c['platform']} ({c['duration']}, {c['level']}) — {c['url']}"
        for c in courses
    )
    skills_text = ", ".join(current_skills) if current_skills else "Not specified"

    return f"""You are an expert career counselor and learning coach.

USER PROFILE:
- Current Role: {current_role}
- Current Skills: {skills_text}
- Target Role: {target_role}
- Available Time: {time_per_week} hours per week

VERIFIED COURSES FROM OUR DATABASE (use ONLY these — do not invent courses):
{course_text}

TASK:
Create a personalized, step-by-step career roadmap for this user to transition from their current role to {target_role}.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS using markdown:

## 🎯 Career Roadmap: {current_role} → {target_role}

### 📊 Skill Gap Analysis
(List the skills the user needs to learn, based on their current skills vs target role requirements)

### 🗺️ Learning Roadmap
Break the roadmap into monthly phases. For each phase:
- **Phase X (Month Y–Z): [Phase Name]**
  - Skills to learn
  - Recommended courses from the list above (include the URL)
  - A small hands-on project to practice

### ⚡ Quick Wins (This Week)
List 2-3 things the user can do THIS WEEK to start immediately.

### 💼 What Your Resume Should Look Like After This Roadmap
Briefly describe the skills and projects the user will be able to list.

Be specific, practical, and encouraging. Only recommend courses from the verified list above."""


# ── Streamlit UI ──────────────────────────────────────────────────────────────

st.title("🗺️ AI Career Roadmap Generator")
st.markdown("*Personalized career growth plans powered by Llama 3.2 running locally on your GPU*")
st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Your Profile")

    current_role = st.text_input(
        "Current Role / Background",
        placeholder="e.g. Computer Science Student, Junior Developer, BCA Graduate",
    )

    current_skills_input = st.text_area(
        "Current Skills (one per line)",
        placeholder="Python\nHTML/CSS\nBasic SQL",
        height=120,
    )

    target_role = st.selectbox(
        "Target Role",
        options=["Select a role..."] + list(ROLE_SKILL_MAP.keys()) + ["Other (type below)"],
    )

    custom_target = ""
    if target_role == "Other (type below)":
        custom_target = st.text_input("Enter your target role")

    time_per_week = st.slider(
        "Hours available per week for learning",
        min_value=2, max_value=40, value=10, step=2,
    )

    generate_btn = st.button("🚀 Generate My Roadmap", type="primary", use_container_width=True)

with col2:
    st.subheader("🗺️ Your Personalized Roadmap")

    if generate_btn:
        final_target = custom_target if target_role == "Other (type below)" else target_role

        if not current_role.strip():
            st.error("Please enter your current role.")
        elif final_target in ("", "Select a role..."):
            st.error("Please select or enter a target role.")
        else:
            current_skills = [s.strip() for s in current_skills_input.strip().splitlines() if s.strip()]
            courses = get_relevant_courses(final_target, current_skills)

            if not courses:
                st.warning("All required skills are already in your profile! Try a more advanced target role.")
            else:
                prompt = build_prompt(current_role, current_skills, final_target, time_per_week, courses)

                with st.spinner("🤖 Llama 3.2 is generating your roadmap on your GPU..."):
                    try:
                        response = ollama.chat(
                            model="llama3.2:3b",
                            messages=[{"role": "user", "content": prompt}],
                            options={"temperature": 0.7, "num_predict": 1500},
                        )
                        roadmap_text = response["message"]["content"]
                        st.session_state["last_roadmap"] = roadmap_text
                        st.session_state["last_target"] = final_target
                    except Exception as e:
                        st.error(f"Error connecting to Ollama: {e}")
                        st.info("Make sure Ollama is running: open a terminal and run `ollama serve`")

    if "last_roadmap" in st.session_state:
        st.markdown(st.session_state["last_roadmap"])
        st.divider()
        st.download_button(
            label="📥 Download Roadmap as .txt",
            data=st.session_state["last_roadmap"],
            file_name=f"roadmap_{st.session_state.get('last_target','career').replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    else:
        st.info("Fill in your profile on the left and click **Generate My Roadmap** to get started.")
        st.markdown("""
**What this tool does:**
- Analyzes the gap between your current skills and your target role
- Retrieves relevant courses from our verified database
- Uses a local AI (Llama 3.2 3B) to create a personalized month-by-month plan
- Runs entirely on your machine — no internet required for AI generation
        """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Powered by Llama 3.2 3B (local) · RAG with verified course database · B.Tech GenAI Project 2026")
