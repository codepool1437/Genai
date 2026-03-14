import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_pinecone import PineconeVectorStore
from typing import Dict, Any

from config import settings
from state import (
    GraphState, 
    ParsedProfile, 
    SkillGaps, 
    CareerRoadmap, 
    RecommendedResources, 
    FinalReport
)

# ==========================================
# Setup LLM & Vector Store
# ==========================================

# Using Llama-3 via Groq API. It's incredibly fast and great for structured output.
llm = ChatGroq(
    temperature=0.2, # Low temperature for more analytical/factual responses
    model_name="llama-3.3-70b-versatile", 
    api_key=settings.GROQ_API_KEY
)

embeddings = HuggingFaceBgeEmbeddings(
    model_name=settings.EMBEDDING_MODEL_NAME,
    model_kwargs={'device': 'cpu'}, 
    encode_kwargs={'normalize_embeddings': True}
)

def get_vector_store():
    """Helper to connect to the Pinecone index dynamically."""
    return PineconeVectorStore.from_existing_index(
        index_name=settings.PINECONE_INDEX_NAME, 
        embedding=embeddings
    )

# ==========================================
# Node 1: Profile Analyzer
# ==========================================
def analyze_profile_node(state: GraphState) -> GraphState:
    print("---NODE: ANALYZE PROFILE---")
    raw_input = state["raw_input"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert career counselor. Your job is to extract structured information from a user's free-text profile description. Extract their education, their current listed skills, and their explicit or implicit career goal."),
        ("human", "{input}")
    ])
    
    # `.with_structured_output` forces the LLM to return data matching our Pydantic model
    chain = prompt | llm.with_structured_output(ParsedProfile)
    parsed_profile = chain.invoke({"input": raw_input})
    
    return {"parsed_profile": parsed_profile}

# ==========================================
# Node 2: Skill Gap Identifier
# ==========================================
def identify_skill_gaps_node(state: GraphState) -> GraphState:
    print("---NODE: IDENTIFY SKILL GAPS---")
    parsed_profile = state["parsed_profile"]
    
    # RAG: Query Pinecone to retrieve real-world context about the career goal
    vector_store = get_vector_store()
    query = f"Skills, requirements, and responsibilities for {parsed_profile.career_goal}"
    docs = vector_store.similarity_search(query, k=3)
    role_context = [doc.page_content for doc in docs]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a career gap analyst. Based on the industry context provided and the user's current skills, identify the standard skills required for the user's career goal, and then list the missing skills the user needs to learn.\n\nIndustry Context:\n{context}"),
        ("human", "User Education: {education}\nUser Current Skills: {skills}\nCareer Goal: {goal}")
    ])
    
    chain = prompt | llm.with_structured_output(SkillGaps)
    skill_gaps = chain.invoke({
        "context": "\n".join(role_context),
        "education": parsed_profile.education,
        "skills": ", ".join(parsed_profile.current_skills),
        "goal": parsed_profile.career_goal
    })
    
    return {"skill_gaps": skill_gaps, "role_context": role_context}

# ==========================================
# Node 3: Career Path Recommender
# ==========================================
def recommend_path_node(state: GraphState) -> GraphState:
    print("---NODE: RECOMMEND CAREER PATH---")
    parsed_profile = state["parsed_profile"]
    skill_gaps = state["skill_gaps"]
    role_context = state.get("role_context", [])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a career strategist. Create a realistic, step-by-step roadmap for the user to achieve their career goal, specifically focusing on bridging their skill gaps. Use the provided industry context to ground your recommendations.\n\nIndustry Context:\n{context}"),
        ("human", "Goal: {goal}\nCurrent Skills: {current_skills}\nMissing Skills (The Gap): {missing_skills}")
    ])
    
    chain = prompt | llm.with_structured_output(CareerRoadmap)
    roadmap = chain.invoke({
        "context": "\n".join(role_context),
        "goal": parsed_profile.career_goal,
        "current_skills": ", ".join(parsed_profile.current_skills),
        "missing_skills": ", ".join(skill_gaps.missing_skills)
    })
    
    return {"career_roadmap": roadmap}

# ==========================================
# Node 4: Resource Suggester
# ==========================================
def suggest_resources_node(state: GraphState) -> GraphState:
    print("---NODE: SUGGEST RESOURCES---")
    skill_gaps = state["skill_gaps"]
    
    # RAG: Retrieve resources specifically targeting the missing skills
    vector_store = get_vector_store()
    query = f"Learning resources, courses, certifications, textbooks, or tutorials for: {', '.join(skill_gaps.missing_skills)}"
    docs = vector_store.similarity_search(query, k=3)
    resource_context = [doc.page_content for doc in docs]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a learning and development expert. Suggest practical, actionable learning resources (courses, books, projects) tailored strictly to the user's missing skills. Ground your suggestions in the provided knowledge base context from the vector database.\n\nContext:\n{context}"),
        ("human", "Missing Skills to Learn: {missing_skills}")
    ])
    
    chain = prompt | llm.with_structured_output(RecommendedResources)
    resources = chain.invoke({
        "context": "\n".join(resource_context),
        "missing_skills": ", ".join(skill_gaps.missing_skills)
    })
    
    return {"recommended_resources": resources, "resource_context": resource_context}

# ==========================================
# Node 5: Final Report Generator
# ==========================================
def generate_final_report_node(state: GraphState) -> GraphState:
    print("---NODE: COMPILE FINAL REPORT---")
    
    # This node doesn't need structured output. We just ask Llama for a nice summary
    # text, and we manually compile our Pydantic objects into the FinalReport schema.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an encouraging career coach. Write a brief, inspiring, personalized summary message (2-3 sentences max) for a user who just received their career roadmap."),
        ("human", "User Goal: {goal}\nThey need to learn: {missing_skills}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({
        "goal": state["parsed_profile"].career_goal,
        "missing_skills": ", ".join(state["skill_gaps"].missing_skills)
    })
    
    # Construct the final object
    final_report = FinalReport(
        profile=state["parsed_profile"],
        skill_gaps=state["skill_gaps"],
        roadmap=state["career_roadmap"],
        resources=state["recommended_resources"],
        summary_message=res.content
    )
    
    return {"final_plan": final_report}
