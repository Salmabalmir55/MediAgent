from typing import TypedDict, Optional, List

class MedicalState(TypedDict):
<<<<<<< HEAD
    # Entrée patient
    patient_name: str
    symptoms: str

    # Résultats des agents
=======
    patient_name: str
    symptoms: str

>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    triage_result: Optional[str]
    rag_context: Optional[str]
    diagnostic: Optional[str]
    prescription: Optional[str]
    report: Optional[str]

<<<<<<< HEAD
    # Human-in-the-loop
    human_approved: Optional[bool]
    human_feedback: Optional[str]

    # Métadonnées
=======
    human_approved: Optional[bool]
    human_feedback: Optional[str]

>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
    current_step: str
    messages: List[str]
