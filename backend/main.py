import sys
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ensure the backend directory is in the Python path so imports work perfectly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph import career_agent
from state import FinalReport

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
