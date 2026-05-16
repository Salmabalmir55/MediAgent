from langchain_groq import ChatGroq
from state import MedicalState
import os

PROMPT_PRESCRIPTION = """Tu es un médecin responsable de la prescription.

Diagnostic validé par le médecin : {diagnostic}
Retour du médecin : {feedback}
Symptômes initiaux : {symptoms}

Génère une proposition de prise en charge incluant :
1. Traitement médicamenteux suggéré (avec posologie générique)
2. Mesures non médicamenteuses (repos, hydratation, régime...)
3. Durée estimée du traitement
4. Suivi recommandé (quand revoir le patient)
5. Informations au patient"""

def agent_prescription(state: MedicalState) -> MedicalState:
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=os.getenv("GROQ_API_KEY"))
    prompt = PROMPT_PRESCRIPTION.format(
        diagnostic=state.get("diagnostic", "Non disponible"),
        feedback=state.get("human_feedback", "Aucune correction"),
        symptoms=state["symptoms"],
    )
    response = llm.invoke(prompt)
    state["prescription"] = response.content
    state["current_step"] = "prescription_done"
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(f"[PRESCRIPTION] {response.content}")
    return state