from langchain_groq import ChatGroq
from state import MedicalState
import os

PROMPT_A = """Tu es un agent de triage médical.
Analyse les symptômes suivants et classe l'urgence : FAIBLE, MODÉRÉE ou ÉLEVÉE.
Symptômes : {symptoms}
Réponds en 2-3 phrases maximum."""

PROMPT_B = """Tu es un agent de triage médical expert travaillant dans un hôpital.
Ta mission est d'évaluer l'urgence d'un patient selon ses symptômes déclarés.

Symptômes rapportés : {symptoms}

Instructions :
1. Identifie les symptômes clés présents.
2. Évalue le niveau d'urgence : FAIBLE / MODÉRÉE / ÉLEVÉE / CRITIQUE.
3. Justifie ton évaluation en 2-3 phrases.
4. Indique les premières observations importantes pour le médecin."""


def agent_triage(state: MedicalState) -> MedicalState:
    """Agent de triage : évalue l'urgence des symptômes du patient."""
    llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0, api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = PROMPT_B.format(symptoms=state["symptoms"])

    response = llm.invoke(prompt)
    state["triage_result"] = response.content
    state["current_step"] = "triage_done"
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(f"[TRIAGE] {response.content}")
    return state