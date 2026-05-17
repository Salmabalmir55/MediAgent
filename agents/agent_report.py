from langchain_groq import ChatGroq
from state import MedicalState
from datetime import datetime
import os

PROMPT_REPORT = """Tu es un médecin rédigeant un compte-rendu médical structuré.

Patient : {patient_name}
Date : {date}

Informations collectées :
- Symptômes : {symptoms}
- Triage : {triage}
- Diagnostic retenu : {diagnostic}
- Commentaire médecin : {feedback}
- Prescription proposée : {prescription}

Rédige un compte-rendu médical professionnel et structuré avec les sections :
MOTIF DE CONSULTATION / ANAMNÈSE / EXAMEN CLINIQUE (résumé) / DIAGNOSTIC / CONDUITE À TENIR / SIGNATURE"""

def agent_report(state: MedicalState) -> MedicalState:
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=os.getenv("GROQ_API_KEY"))
    prompt = PROMPT_REPORT.format(
        patient_name=state.get("patient_name", "Anonyme"),
        date=datetime.now().strftime("%d/%m/%Y à %H:%M"),
        symptoms=state["symptoms"],
        triage=state.get("triage_result", "N/A"),
        diagnostic=state.get("diagnostic", "N/A"),
        feedback=state.get("human_feedback", "Aucun"),
        prescription=state.get("prescription", "N/A"),
    )
    response = llm.invoke(prompt)
    state["report"] = response.content
    state["current_step"] = "done"
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(f"[RAPPORT] Compte-rendu généré.")
    return state