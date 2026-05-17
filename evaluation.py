

import os
import re
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq  # ← Changement : Groq au lieu d'OpenAI
from agents.agent_triage import PROMPT_A, PROMPT_B

TEST_CASES = [
    {
        "id": 1,
        "symptoms": "Légère toux depuis 2 jours, pas de fièvre, état général conservé.",
        "expected_urgency": "FAIBLE",
    },
    {
        "id": 2,
        "symptoms": "Fièvre à 38.5°C, courbatures, toux sèche, perte d'odorat depuis 4 jours.",
        "expected_urgency": "MODÉRÉE",
    },
    {
        "id": 3,
        "symptoms": "Douleur thoracique intense irradiant vers le bras gauche, sueurs froides, dyspnée.",
        "expected_urgency": "ÉLEVÉE",
    },
    {
        "id": 4,
        "symptoms": "Douleur abdominale en fosse iliaque droite, fièvre à 38°C, nausées et vomissements.",
        "expected_urgency": "ÉLEVÉE",
    },
    {
        "id": 5,
        "symptoms": "Maux de tête modérés, fatigue, légère congestion nasale, sans fièvre.",
        "expected_urgency": "FAIBLE",
    },
]

def extract_urgency(text: str) -> str:
    """Extrait le niveau d'urgence de la réponse du LLM de manière robuste."""
    text_upper = text.upper()
    
    patterns = {
        "CRITIQUE": r"\b(CRITIQUE|URGENCE\s*ABSOLUE|VITAL|MORT)\b",
        "ÉLEVÉE": r"\b(ÉLEVÉE|ÉLEVE|HAUTE|GRAVE|URGENT|IMMÉDIATE)\b",
        "MODÉRÉE": r"\b(MODÉRÉE|MODEREE|MOYENNE)\b",
        "FAIBLE": r"\b(FAIBLE|LÉGÈRE|LEGERE|MINEURE)\b",
    }
    
    for level, pattern in patterns.items():
        if re.search(pattern, text_upper):
            return level
    
    if "CRITIQUE" in text_upper:
        return "CRITIQUE"
    if "ÉLEVÉE" in text_upper or "ELEVEE" in text_upper:
        return "ÉLEVÉE"
    if "MODÉRÉE" in text_upper or "MODEREE" in text_upper:
        return "MODÉRÉE"
    if "FAIBLE" in text_upper:
        return "FAIBLE"
    
    return "INCONNU"

def evaluate_prompt(prompt_template: str, prompt_name: str) -> list:
    # ← Changement : utilisation de Groq
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=os.getenv("GROQ_API_KEY"))
    results = []

    for case in TEST_CASES:
        prompt = prompt_template.format(symptoms=case["symptoms"])
        response = llm.invoke(prompt).content
        expected = case["expected_urgency"]
        detected = extract_urgency(response)
        
        # Vérification de correspondance
        correct = (detected == expected) or \
                  (expected == "ÉLEVÉE" and detected == "CRITIQUE")

        results.append({
            "case_id": case["id"],
            "prompt": prompt_name,
            "expected": expected,
            "detected": detected,
            "correct": correct,
            "response_preview": response[:120] + "...",
        })
    return results

def run_evaluation():
    print("=" * 60)
    print("   ÉVALUATION A/B DES PROMPTS — AGENT TRIAGE MÉDICAL (GROQ)")
    print("=" * 60)

    results_a = evaluate_prompt(PROMPT_A, "Prompt A (court)")
    results_b = evaluate_prompt(PROMPT_B, "Prompt B (détaillé)")

    all_results = results_a + results_b
    score_a = sum(1 for r in results_a if r["correct"]) / len(results_a) * 100
    score_b = sum(1 for r in results_b if r["correct"]) / len(results_b) * 100
    
    correct_a = sum(1 for r in results_a if r["correct"])
    correct_b = sum(1 for r in results_b if r["correct"])

    print(f"\n{'CAS':<5} {'PROMPT':<25} {'ATTENDU':<10} {'DÉTECTÉ':<10} {'OK?'}")
    print("-" * 60)
    for r in all_results:
        ok = "✅" if r["correct"] else "❌"
        print(f"{r['case_id']:<5} {r['prompt']:<25} {r['expected']:<10} {r['detected']:<10} {ok}")

    print("\n" + "=" * 60)
    print(f"  Score Prompt A (court)    : {score_a:.0f}% ({correct_a}/{len(results_a)} cas corrects)")
    print(f"  Score Prompt B (détaillé) : {score_b:.0f}% ({correct_b}/{len(results_b)} cas corrects)")
    winner = "Prompt B" if score_b >= score_a else "Prompt A"
    print(f"\n  → Meilleur prompt : {winner}")
    print("=" * 60)

    return {"score_a": score_a, "score_b": score_b, "results": all_results}

if __name__ == "__main__":
    run_evaluation()
