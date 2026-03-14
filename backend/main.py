import sys
import os
import uuid
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from PyPDF2 import PdfReader

# Ensure the backend directory is in the Python path so imports work perfectly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph import career_agent
from agents import llm
from state import FinalReport, ParsedCVInfo
from langchain_core.prompts import ChatPromptTemplate

# Initialize the FastAPI App
app = FastAPI(
    title="Career Guidance AI Backend",
    description="RAG-powered LangGraph APIs for personalized career guidance",
    version="1.0.0"
)

# Enable CORS so your React frontend running on a different port can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Open for development; restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Schema Definitions for API Requests
# ==========================================
class ProfileRequest(BaseModel):
    raw_text: str
    session_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str

# ==========================================
# API Endpoints
# ==========================================

@app.post("/api/analyze-profile")
def analyze_profile(request: ProfileRequest):
    """
    Main endpoint to kick off the LangGraph profile analysis and roadmap generation.
    """
    try:
        # Generate a unique session ID if the user doesn't provide one
        session_id = request.session_id or str(uuid.uuid4())
        
        # Configuration for LangGraph Memory (this is how it remembers the user!)
        config = {"configurable": {"thread_id": session_id}}
        
        print(f"🚀 Starting graph execution for session: {session_id}")
        
        # Run the workflow. We pass the initial state {"raw_input": user_text}
        result = career_agent.invoke({"raw_input": request.raw_text}, config=config)
        
        if "final_plan" not in result or result["final_plan"] is None:
            raise HTTPException(status_code=500, detail="Failed to generate career plan.")
            
        print("✅ Graph execution complete.")
        
        # Return the structured data (converting the Pydantic FinalReport to dict)
        return {
            "session_id": session_id,
            "report": result["final_plan"].model_dump()
        }
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/progress/{session_id}")
def get_progress(session_id: str):
    """
    Fetch the user's previously generated data using LangGraph memory CheckpointSaver.
    """
    config = {"configurable": {"thread_id": session_id}}
    state = career_agent.get_state(config)
    
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="No session found.")
        
    return {
        "session_id": session_id,
        # Return the last known final plan if it exists
        "report": state.values.get("final_plan", {}).model_dump() if hasattr(state.values.get("final_plan"), "model_dump") else None,
        "raw_input": state.values.get("raw_input", "")
    }

@app.get("/")
def health_check():
    """Simple API check if server is running."""
    return {"status": "ok", "message": "Career Guidance API is running!"}

@app.post("/api/profile/extract")
async def extract_profile_from_cv(file: UploadFile = File(...)):
    """
    Extracts text from an uploaded CV (PDF format) and returns it.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Read the file content
        content = await file.read()
        
        # Use PyPDF2 to extract text
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF. It might be scanned or empty.")
            
        # Use LLM to structure the extracted boring text into actual profile properties
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert resume parser. Extract the candidate's details into the specific schema fields. Be concise."),
            ("human", "Here is the raw extracted text from the CV:\n{cv_text}")
        ])
        
        chain = prompt | llm.with_structured_output(ParsedCVInfo)
        structured_cv = chain.invoke({"cv_text": text.strip()})

        return {
            "status": "success",
            "extracted_data": structured_cv.model_dump()
        }
    except Exception as e:
        print(f"❌ Error during CV extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process CV: {str(e)}")

@app.post("/api/chat")
def chat_with_advisor(request: ChatRequest):
    """
    Discuss the career roadmap with the AI advisor.
    Pulls specific context using LangGraph Checkpoint memory.
    """
    try:
        # Fetch the user's specific context from LangGraph memory
        config = {"configurable": {"thread_id": request.session_id}}
        state = career_agent.get_state(config)
        
        roadmap_context = "No roadmap explicitly generated yet."
        if state and state.values and "final_plan" in state.values:
            # We must convert the Pydantic object back into a string context
            roadmap_context = str(state.values["final_plan"].model_dump())

        # Combine system role prompt + memory injection
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert, encouraging career AI advisor. You are helping a user who has just generated their personalized career roadmap. Use the following context about their roadmap to answer their questions accurately and thoughtfully. Keep responses concise but helpful. STRICT RULE: You must ONLY answer questions related to the user's career, education, skills, and the generated roadmap. If the user asks about unrelated topics (like movies, sports, coding tasks not related to their plan, etc.), you must politely decline and remind the user that you are here to chat specifically regarding the career path and roadmap created for them.\n\nUser Roadmap Details from Memory:\n{roadmap_context}"),
            ("human", "{message}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({
            "roadmap_context": roadmap_context,
            "message": request.message
        })
        
        return {"response": response.content}
        
    except Exception as e:
        print(f"❌ Error during chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate chat response")
