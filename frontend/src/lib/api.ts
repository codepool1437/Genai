// URL of our local Python FastAPI server
const API_BASE_URL = "http://localhost:8000/api";

// ---------------------------------------------------------
// TypeScript Interfaces predicting the Python Backend output
// ---------------------------------------------------------

export interface ParsedProfile {
  education: string;
  current_skills: string[];
  career_goal: string;
}

export interface SkillGaps {
  required_skills: string[];
  missing_skills: string[];
}

export interface RoadmapStep {
  step_number: number;
  title: string;
  description: string;
  timeline: string;
}

export interface CareerRoadmap {
  steps: RoadmapStep[];
}

export interface Resource {
  title: string;
  resource_type: string;
  description: string;
}

export interface RecommendedResources {
  resources: Resource[];
}

export interface FinalReport {
  profile: ParsedProfile;
  skill_gaps: SkillGaps;
  roadmap: CareerRoadmap;
  resources: RecommendedResources;
  summary_message: string;
}

export interface AnalyzeProfileResponse {
  session_id: string;
  report: FinalReport;
}

// ---------------------------------------------------------
// API Call Functions
// ---------------------------------------------------------

/**
 * Sends the user's free-text profile to the LangGraph backend.
 * @param rawText What the user typed in the text area.
 * @param sessionId Optional: Provide this if updating an existing session.
 * @returns A promise resolving to the final generated career report.
 */
export async function analyzeProfile(rawText: string, sessionId?: string): Promise<AnalyzeProfileResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze-profile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        raw_text: rawText,
        session_id: sessionId || null,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to analyze profile.");
    }

    return await response.json();
  } catch (error) {
    console.error("API Error - analyzeProfile:", error);
    throw error;
  }
}

/**
 * Retrieves the previously generated career plan for a returning user.
 * @param sessionId The ID returned from the first `analyzeProfile` call.
 * @returns The saved final report from LangGraph memory.
 */
export async function getProgress(sessionId: string): Promise<AnalyzeProfileResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/progress/${sessionId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch progress for session ${sessionId}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API Error - getProgress:", error);
    throw error;
  }
}
export function apiUrl(path: string): string {
  return `${API_BASE_URL.replace('/api', '')}${path}`;
}
