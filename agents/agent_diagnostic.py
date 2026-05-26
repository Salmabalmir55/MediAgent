from langchain_groq import ChatGroq
from state import MedicalState
import os

PROMPT_DIAGNOSTIC = """Tu es un médecin généraliste expert en diagnostic médical.

Symptômes du patient : {symptoms}

Évaluation de triage : {triage}

Informations médicales de référence (issues de la base documentaire) :
{context}

Sur la base de ces informations, propose :
1. Un ou deux diagnostics probables (du plus au moins probable)
2. Les examens complémentaires à envisager (prise de sang, imagerie, etc.)
3. Le niveau de certitude de ton diagnostic (faible / moyen / élevé)
4. Les signaux d'alerte qui nécessiteraient une urgence immédiate"""

def agent_diagnostic(state: MedicalState) -> MedicalState:
<<<<<<< HEAD
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=os.getenv("GROQ_API_KEY"))
=======
    llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0.2, api_key=os.getenv("GROQ_API_KEY"))
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    prompt = PROMPT_DIAGNOSTIC.format(
        symptoms=state["symptoms"],
        triage=state.get("triage_result", "Non disponible"),
        context=state.get("rag_context", "Aucun document trouvé"),
    )
    response = llm.invoke(prompt)
    state["diagnostic"] = response.content
    state["current_step"] = "diagnostic_done"
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(f"[DIAGNOSTIC] {response.content}")
    return state