import os
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from state import MedicalState

INDEX_PATH = "data/faiss_index"

FALLBACK_DOCS = [
    """Grippe (Influenza) : La grippe est une infection virale respiratoire aiguë.
Symptômes : fièvre élevée (38-40°C), frissons, courbatures, fatigue intense, toux sèche,
maux de tête, écoulement nasal. Durée : 7-10 jours. Traitement : repos, hydratation,
antipyrétiques (paracétamol). Complications possibles : pneumonie, bronchite.""",

    """Pneumonie : Infection pulmonaire souvent bactérienne (Streptococcus pneumoniae).
Symptômes : toux avec expectorations, fièvre élevée, douleur thoracique, dyspnée,
frissons. Diagnostic : radiographie pulmonaire, prise de sang (CRP élevée).
Traitement : antibiotiques (amoxicilline), hospitalisation si cas sévère.""",

    """Diabète de type 2 : Maladie métabolique chronique caractérisée par une hyperglycémie.
Symptômes : soif excessive (polydipsie), mictions fréquentes (polyurie), fatigue,
vision floue, cicatrisation lente. Traitement : régime alimentaire, exercice physique,
metformine, insuline si nécessaire. Surveillance : HbA1c < 7%.""",

    """Hypertension artérielle : Pression artérielle chroniquement élevée (>140/90 mmHg).
Symptômes : souvent asymptomatique, parfois céphalées, vertiges, acouphènes.
Facteurs de risque : obésité, tabac, stress, alimentation salée. Traitement :
antihypertenseurs (IEC, bêta-bloquants), modifications du mode de vie.""",

    """Appendicite aiguë : Inflammation de l'appendice vermiculaire.
Symptômes : douleur abdominale débutant autour du nombril puis se déplaçant en fosse
iliaque droite, nausées, vomissements, fièvre modérée (38°C), défense abdominale.
Urgence chirurgicale : appendicectomie. Risque de péritonite si non traité.""",

    """Infarctus du myocarde : Obstruction d'une artère coronaire.
Symptômes : douleur thoracique intense en étau irradiant vers le bras gauche, mâchoire,
dos. Sueurs froides, dyspnée, nausées, anxiété. URGENCE ABSOLUE : appeler le 15.
Traitement : thrombolyse ou angioplastie en urgence.""",

    """COVID-19 : Infection par le coronavirus SARS-CoV-2.
Symptômes : fièvre, toux sèche, fatigue, perte d'odorat (anosmie) et de goût (agueusie),
dyspnée, douleurs musculaires. Formes sévères : pneumonie bilatérale, SDRA.
Prévention : vaccination, masque, distanciation sociale.""",

    """Migraine : Céphalée primaire récurrente souvent unilatérale.
Symptômes : douleur pulsatile intense, nausées, vomissements, photophobie,
phonophobie. Durée : 4-72 heures. Avec ou sans aura (troubles visuels, sensitifs).
Traitement : triptans, AINS, repos dans l'obscurité.""",
]


def build_rag_index(pdf_folder: str = "data/medical_docs") -> FAISS:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_docs = []

    os.makedirs("data", exist_ok=True)

    if os.path.exists(pdf_folder):
        for fname in os.listdir(pdf_folder):
            fpath = os.path.join(pdf_folder, fname)
            try:
                if fname.endswith(".pdf"):
                    loader = PyPDFLoader(fpath)
                    docs = loader.load_and_split(splitter)
                    all_docs.extend(docs)
                elif fname.endswith(".txt"):
                    loader = TextLoader(fpath, encoding="utf-8")
                    docs = loader.load_and_split(splitter)
                    all_docs.extend(docs)
            except Exception as e:
                print(f"[RAG] Erreur lecture {fname}: {e}")

    if not all_docs:
        print("[RAG] Aucun PDF trouvé — utilisation de la base médicale intégrée.")
        all_docs = splitter.create_documents(FALLBACK_DOCS)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(all_docs, embeddings)

    os.makedirs(os.path.dirname(INDEX_PATH) if os.path.dirname(INDEX_PATH) else "data", exist_ok=True)
    vectorstore.save_local(INDEX_PATH)
    print(f"[RAG] Index construit avec {len(all_docs)} chunks.")

    get_vectorstore.clear()
    return vectorstore


@st.cache_resource
def get_vectorstore() -> FAISS:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if os.path.exists(INDEX_PATH):
        return FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return build_rag_index()


def agent_rag(state: MedicalState) -> MedicalState:
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    query = f"{state['symptoms']} {state.get('triage_result', '')}"
    docs = retriever.invoke(query)
    context = "\n\n".join([f"[Doc {i+1}]: {d.page_content}" for i, d in enumerate(docs)])

    state["rag_context"] = context
    state["current_step"] = "rag_done"
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(f"[RAG] {len(docs)} documents médicaux récupérés.")
    return state