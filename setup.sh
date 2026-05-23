#!/bin/bash
# ─── Script d'installation MediAgent (version Groq) ──────────────────────────
echo "🏥  Installation de MediAgent..."

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Installer les dépendances
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Copier le template .env si pas encore fait
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  Fichier .env créé — ajoutez votre clé GROQ dans .env"
fi

echo ""
echo "✅  Installation terminée !"
echo ""
echo "Étapes suivantes :"
echo "  1. Éditez .env et ajoutez : GROQ_API_KEY=votre_clé_groq"
echo "  2. Lancez l'interface : streamlit run app.py"
echo ""