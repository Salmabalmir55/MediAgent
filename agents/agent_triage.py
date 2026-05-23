from langchain_groq import ChatGroq
from state import MedicalState
import os
import time

# ─── PROMPTS pour l'évaluation A/B ───────────────────────────────────────────
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
# ─────────────────────────────────────────────────────────────────────────────

def _call_llm_with_retry(llm, prompt: str, max_retries: int = 3):
    """Appel LLM avec retry et backoff exponentiel."""
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"[TRIAGE] Tentative {attempt+1} échouée ({e}), retry dans {wait}s...")
            time.sleep(wait)

def agent_triage(state: MedicalState) -> MedicalState:
    """Agent de triage : évalue l'urgence des symptômes du patient.
    Utilise llama-3.1-8b-instant (3-5x plus rapide) car le triage
    ne nécessite pas le modèle le plus puissant.
    """
    llm = ChatGroq(
        model="llama-3.1-8b-instant",   # ← Modèle rapide pour le triage
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
        request_timeout=30,             # ← Timeout 30s
        max_retries=2,
    )

    prompt = PROMPT_B.format(symptoms=state["symptoms"])
    response = _call_llm_with_retry(llm, prompt)

    state["triage_result"] = response.content
    state["current_step"] = "triage_done"
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(f"[TRIAGE] {response.content}")
    return state