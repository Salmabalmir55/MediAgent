<<<<<<< HEAD
#!/bin/bash
echo "🏥  Installation de MediAgent avec LangFlow..."
=======
echo "  Installation de MediAgent..."
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a

python -m venv venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

<<<<<<< HEAD
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
=======
pip install --upgrade pip -q
pip install -r requirements.txt -q

if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Fichier .env créé :  ajoutez votre clé GROQ dans .env"
fi

echo ""
echo "  Installation terminée !"
echo ""
echo "Étapes suivantes :"
echo "  1. Éditez .env et ajoutez : GROQ_API_KEY=votre_clé_groq"
echo "  2. Lancez l'interface : streamlit run app.py"
>>>>>>> 3a9888eb6a02c3d60df66c9e133a53a9a99a5a3a
echo ""