from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# Define the shared state data contract
class GraphState(TypedDict):
    audio_url: str
    transcript: str
    language: str
    risk_level: Literal["low", "medium", "high"]
    confidence: float
    reason: str
    explainer_output: str
    alert_status: str

# --- Step 4: Define the 5 Placeholder Node Functions ---

def ingestion_agent(state: GraphState) -> GraphState:
    print("--- [1/5] INGESTION AGENT ---")
    print(f"Processing audio URL: {state.get('audio_url')}")
    # Placeholder data passing forward
    return state

def transcript_agent(state: GraphState) -> GraphState:
    print("--- [2/5] TRANSCRIPT & LANGUAGE AGENT ---")
    # Member B will eventually replace this logic
    state["transcript"] = "Aadhaar number do immediately or account will be blocked!"
    state["language"] = "en"
    print(f"Transcript generated: '{state['transcript']}' (Lang: {state['language']})")
    return state

def risk_agent(state: GraphState) -> GraphState:
    print("--- [3/5] RISK ANALYSIS AGENT ---")
    # Member B will eventually replace this logic
    state["risk_level"] = "high"
    state["confidence"] = 0.95
    state["reason"] = "Urgent demand for sensitive financial/identity data."
    print(f"Risk Assessed: {state['risk_level'].upper()} (Confidence: {state['confidence']})")
    return state

def explainer_agent(state: GraphState) -> GraphState:
    print("--- [4A/5] EXPLOITS / EXPLAINER AGENT (Parallel Branch) ---")
    # Member B will eventually replace this logic
    state["explainer_output"] = "Audio warning generated: Potential phishing attempt detected."
    print("Explainer audio rendered.")
    return state

def family_alert_agent(state: GraphState) -> GraphState:
    print("--- [4B/5] FAMILY ALERT AGENT (Parallel Branch) ---")
    if state["risk_level"] == "high":
        # Member C will eventually plug WhatsApp API here
        state["alert_status"] = "WhatsApp emergency alert dispatched to family!"
        print(state["alert_status"])
    else:
        state["alert_status"] = "Risk low. No alert sent."
        print(state["alert_status"])
    return state

# --- Build the LangGraph Pipeline with Parallel Fan-Out ---
def create_workflow():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("ingestion", ingestion_agent)
    workflow.add_node("transcript", transcript_agent)
    workflow.add_node("risk", risk_agent)
    workflow.add_node("explainer", explainer_agent)
    workflow.add_node("family_alert", family_alert_agent)

    # Define linear flow up to risk analysis
    workflow.add_edge(START, "ingestion")
    workflow.add_edge("ingestion", "transcript")
    workflow.add_edge("transcript", "risk")

    # Define parallel fan-out from Risk Agent to Explainer and Family Alert
    workflow.add_edge("risk", "explainer")
    workflow.add_edge("risk", "family_alert")

    # Both parallel branches terminate at END
    workflow.add_edge("explainer", END)
    workflow.add_edge("family_alert", END)

    return workflow.compile()

# Expose compiled graph
app_graph = create_workflow()