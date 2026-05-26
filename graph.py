import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

from state import MedicalState
from agents.agent_triage import agent_triage
from agents.agent_rag import agent_rag
from agents.agent_diagnostic import agent_diagnostic
from agents.agent_prescription import agent_prescription
from agents.agent_report import agent_report

<<<<<<< HEAD
=======

>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
def human_validation_node(state: MedicalState) -> MedicalState:
    state["current_step"] = "awaiting_human"
    return state

def should_continue(state: MedicalState) -> str:
    if state.get("human_approved") is True:
        return "prescription"
<<<<<<< HEAD
    return END

def build_graph():
    builder = StateGraph(MedicalState)

=======
    return END  

def build_graph():
    builder = StateGraph(MedicalState)
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    builder.add_node("triage", agent_triage)
    builder.add_node("rag", agent_rag)
    builder.add_node("diagnostic", agent_diagnostic)
    builder.add_node("human_validation", human_validation_node)
    builder.add_node("prescription", agent_prescription)
    builder.add_node("report", agent_report)
<<<<<<< HEAD

=======
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    builder.set_entry_point("triage")
    builder.add_edge("triage", "rag")
    builder.add_edge("rag", "diagnostic")
    builder.add_edge("diagnostic", "human_validation")
<<<<<<< HEAD

=======
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    builder.add_conditional_edges(
        "human_validation",
        should_continue,
        {"prescription": "prescription", END: END},
    )
    builder.add_edge("prescription", "report")
    builder.add_edge("report", END)
<<<<<<< HEAD

    memory = MemorySaver()
    return builder.compile(
        checkpointer=memory,
        interrupt_before=["human_validation"],
=======
    memory = MemorySaver()
    return builder.compile(
        checkpointer=memory,
        interrupt_before=["human_validation"],  
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    )

def run_until_human(graph, initial_state: dict, thread_id: str) -> MedicalState:
    config = {"configurable": {"thread_id": thread_id}}
    result = None
    for event in graph.stream(initial_state, config=config, stream_mode="values"):
        result = event
    if result is None:
<<<<<<< HEAD
        raise RuntimeError("Le graphe s'est termine sans atteindre le point d'arret humain.")
=======
        raise RuntimeError("Le graphe s'est terminé sans atteindre le point d'arrêt humain.")
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    return result

def resume_after_human(graph, thread_id: str, approved: bool, feedback: str) -> MedicalState:
    config = {"configurable": {"thread_id": thread_id}}
    update = {"human_approved": approved, "human_feedback": feedback}
    graph.update_state(config, update)
    result = None
    for event in graph.stream(None, config=config, stream_mode="values"):
        result = event
    if result is None:
<<<<<<< HEAD
        raise RuntimeError("Le graphe n'a pas pu reprendre apres validation humaine.")
    return result

def export_graph_for_langflow(graph, output_path: str = "mediagent_graph.json"):
    from langflow_integration import save_graph_for_langflow
    return save_graph_for_langflow(graph, output_path)
=======
        raise RuntimeError("Le graphe n'a pas pu reprendre après validation humaine.")
    return result

>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a

if __name__ == "__main__":
    g = build_graph()
    init = {
<<<<<<< HEAD
        "patient_name": "Ahmed Bennani",
        "symptoms": "Fievre a 39°C depuis 3 jours, toux seche, courbatures, perte d'odorat",
=======
        "patient_name": "Jawhara Lazrak",
        "symptoms": "Fièvre à 39°C depuis 3 jours, toux sèche, courbatures, perte d'odorat",
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
        "messages": [],
        "triage_result": None,
        "rag_context": None,
        "diagnostic": None,
        "prescription": None,
        "report": None,
        "human_approved": None,
        "human_feedback": None,
        "current_step": "start",
    }
    state = run_until_human(g, init, "test-001")
<<<<<<< HEAD
    print("\n=== DIAGNOSTIC PROPOSE ===")
    print(state.get("diagnostic"))
    print("\n→ En attente de validation humaine...")
    final = resume_after_human(g, "test-001", approved=True, feedback="Diagnostic coherent, je confirme.")
    print("\n=== RAPPORT FINAL ===")
    print(final.get("report"))
    export_graph_for_langflow(g)
=======
    print("\n=== DIAGNOSTIC PROPOSÉ ===")
    print(state.get("diagnostic"))
    print("\n→ En attente de validation humaine...")
    final = resume_after_human(g, "test-001", approved=True, feedback="Diagnostic cohérent, je confirme.")
    print("\n=== RAPPORT FINAL ===")
    print(final.get("report"))
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
