from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

# ==========================================
# Pydantic Schemas for structured LLM output
# ==========================================

class ParsedProfile(BaseModel):
    """Output schema for the Profile Analyzer Agent."""
    education: str = Field(description="The user's educational background, degrees, or current studies.")
    current_skills: List[str] = Field(description="A list of skills the user currently possesses.")
    career_goal: str = Field(description="The specific job role or career goal the user wants to achieve.")

class SkillGaps(BaseModel):
    """Output schema for the Skill Gap Identifier Agent."""
    required_skills: List[str] = Field(description="A list of standard skills generally required for the user's career goal.")
    missing_skills: List[str] = Field(description="Skills required for the goal that the user currently lacks.")

class RoadmapStep(BaseModel):
    """Individual step in the career roadmap."""
    step_number: int = Field(description="The chronological order of the step.")
    title: str = Field(description="Short title for the roadmap phase.")
    description: str = Field(description="Detailed explanation of what the user should do in this step.")
    timeline: str = Field(description="Estimated time to complete this step (e.g., '1-2 months').")

class CareerRoadmap(BaseModel):
    """Output schema for the Career Path Recommender Agent."""
    steps: List[RoadmapStep] = Field(description="Sequential list of steps to achieve the career goal.")

class Resource(BaseModel):
    """Individual learning resource."""
    title: str = Field(description="Name of the course, guide, or tutorial.")
    resource_type: str = Field(description="Type of resource (e.g., 'Course', 'Book', 'Tutorial', 'Project').")
    description: str = Field(description="Why this resource is relevant to the user's skill gaps.")

class RecommendedResources(BaseModel):
    """Output schema for the Resource Suggester Agent."""
    resources: List[Resource] = Field(description="List of learning resources tailored to the missing skills.")

class FinalReport(BaseModel):
    """Structured representation of the final generated plan."""
    profile: ParsedProfile
    skill_gaps: SkillGaps
    roadmap: CareerRoadmap
    resources: RecommendedResources
    summary_message: str = Field(description="A warm, encouraging summarization message for the user.")

# ==========================================
# LangGraph State Definition
# ==========================================

class GraphState(TypedDict):
    """
    Represents the state of our LangGraph.
    Data gets added or updated here as it moves from node to node.
    """
    # Initial input
    raw_input: str
    
    # Internal agent data (populated along the way)
    parsed_profile: Optional[ParsedProfile]
    skill_gaps: Optional[SkillGaps]
    career_roadmap: Optional[CareerRoadmap]
    recommended_resources: Optional[RecommendedResources]
    
    # RAG Context (raw documents fetched from Pinecone)
    role_context: List[str]
    resource_context: List[str]
    
    # Final output
    final_plan: Optional[FinalReport]
