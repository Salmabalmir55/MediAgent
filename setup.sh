#!/bin/bash
echo "🏥  Installation de MediAgent avec LangFlow..."

python -m venv venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

uv add --upgrade pip -q
uv add -r requirements.txt -q

if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Fichier .env cree — ajoutez votre cle GROQ dans .env"
fi

echo ""
echo "  Installation terminee !"
echo ""
echo "Etapes suivantes :"
echo "  1. Editez .env et ajoutez : GROQ_API_KEY=votre_cle_groq"
echo "  2. Lancez l'interface : streamlit run app.py"
echo "  3. Pour visualiser avec LangFlow : langflow run"
echo ""