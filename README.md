# 🏥 MediAgent — Système Multi-Agent Médical

> Projet de Fin de Module — Master SDIA · LangGraph 2026  
> Prof. RETAL Sara

## Description

Système multi-agent intelligent pour l'aide au diagnostic médical, implémenté avec **LangGraph**. Il combine :
- 🤖 **Orchestration multi-agent** (triage → RAG → diagnostic → prescription → rapport)
- 📚 **RAG Agentique** avec FAISS pour la recherche documentaire médicale
- 👨‍⚕️ **Human-in-the-Loop** : validation médicale obligatoire avant la prescription
- 📊 **Évaluation A/B** des prompts de l'agent de triage
- 🌐 **Interface Web** Streamlit interactive

## Architecture des agents

```
Patient
  ↓
[Agent Triage]     — Évalue l'urgence (FAIBLE / MODÉRÉE / ÉLEVÉE / CRITIQUE)
  ↓
[Agent RAG]        — Recherche dans la base FAISS les docs médicaux pertinents
  ↓
[Agent Diagnostic] — Propose un diagnostic basé sur le triage + contexte RAG
  ↓
⛔ HUMAN-IN-THE-LOOP — Le médecin valide, corrige ou rejette
  ↓
[Agent Prescription] — Génère la prise en charge médicamenteuse + conseils
  ↓
[Agent Rapport]    — Rédige le compte-rendu médical final
```

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/mediagent.git
cd mediagent

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API
cp .env.example .env
# Éditez .env et ajoutez votre clé OpenAI : OPENAI_API_KEY=sk-...

# 5. Lancer l'interface
streamlit run app.py
```

## Utilisation

### Interface Web (recommandée)
```bash
streamlit run app.py
```
1. Entrez votre clé API dans la barre latérale
2. Cliquez **"Construire l'index RAG"** (une seule fois)
3. Entrez le nom du patient et ses symptômes
4. Suivez les étapes des agents
5. Validez le diagnostic en tant que médecin
6. Téléchargez le rapport final

### Test en ligne de commande
```bash
python graph.py
```

### Évaluation A/B des prompts
```bash
python evaluation.py
```

## Structure du projet

```
mediagent/
├── app.py                   # Interface Streamlit
├── graph.py                 # Orchestration LangGraph
├── state.py                 # État partagé entre agents
├── evaluation.py            # Évaluation A/B des prompts
├── requirements.txt
├── .env.example
├── agents/
│   ├── agent_triage.py      # Agent d'évaluation d'urgence
│   ├── agent_rag.py         # Agent de recherche documentaire
│   ├── agent_diagnostic.py  # Agent de diagnostic médical
│   ├── agent_prescription.py# Agent de prescription
│   └── agent_report.py      # Agent de compte-rendu
└── data/
    ├── medical_docs/        # Déposez vos PDFs médicaux ici
    └── faiss_index/         # Index FAISS (généré automatiquement)
```

## Technologies utilisées

| Composant | Technologie |
|-----------|-------------|
| Orchestration | LangGraph |
| LLM | GPT-4o-mini (OpenAI) |
| RAG | FAISS + LangChain |
| Embeddings | text-embedding-ada-002 |
| Interface | Streamlit |
| État | TypedDict + MemorySaver |

## Groupe

- **Étudiant 1** : Architecture LangGraph, agents, RAG, Human-in-the-Loop  
- **Étudiant 2** : Interface Streamlit, évaluation prompts, rapport PDF, GitHub

---
Master SDIA — Systèmes Multi-Agents — 2026
