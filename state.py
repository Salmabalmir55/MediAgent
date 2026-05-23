from typing import TypedDict, Optional, List

class MedicalState(TypedDict):
    # Entrée patient
    patient_name: str
    symptoms: str

    # Résultats des agents
    triage_result: Optional[str]
    rag_context: Optional[str]
    diagnostic: Optional[str]
    prescription: Optional[str]
    report: Optional[str]

    # Human-in-the-loop
    human_approved: Optional[bool]
    human_feedback: Optional[str]

    # Métadonnées
    current_step: str
    messages: List[str]
