from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import GraphState
from agents import (
    analyze_profile_node,
    identify_skill_gaps_node,
    recommend_path_node,
    suggest_resources_node,
    generate_final_report_node
)

# Initialize the state graph with our defined state schema
workflow = StateGraph(GraphState)

# 1. Add all the nodes we created in agents.py
workflow.add_node("analyze_profile", analyze_profile_node)
workflow.add_node("identify_skill_gaps", identify_skill_gaps_node)
workflow.add_node("recommend_path", recommend_path_node)
workflow.add_node("suggest_resources", suggest_resources_node)
workflow.add_node("generate_final_report", generate_final_report_node)

# 2. Define the routing (Edges)
# For now, this is a smooth, linear pipeline representing the happy path
workflow.add_edge(START, "analyze_profile")
workflow.add_edge("analyze_profile", "identify_skill_gaps")
workflow.add_edge("identify_skill_gaps", "recommend_path")
workflow.add_edge("recommend_path", "suggest_resources")
workflow.add_edge("suggest_resources", "generate_final_report")
workflow.add_edge("generate_final_report", END)

# 3. Setup Memory Persistence
# We are using MemorySaver here which acts perfectly as our session cache.
# It uses the `thread_id` from the config to remember context for returning users.
memory = MemorySaver()

# 4. Compile the graph
career_agent = workflow.compile(checkpointer=memory)

print("✅ LangGraph compiled successfully with Checkpoint memory.")
