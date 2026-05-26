from typing import TypedDict, Optional, List

class MedicalState(TypedDict):
    patient_name: str
    symptoms: str

    triage_result: Optional[str]
    rag_context: Optional[str]
    diagnostic: Optional[str]
    prescription: Optional[str]
    report: Optional[str]

    human_approved: Optional[bool]
    human_feedback: Optional[str]

    current_step: str
    messages: List[str]
