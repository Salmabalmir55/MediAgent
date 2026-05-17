import streamlit as st
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="MediAgent — Assistant Medical IA",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a73e8, #0d47a1);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .agent-card {
        background: #f8f9fa;
        border-left: 4px solid #1a73e8;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .agent-card.rag    { border-color: #0b8043; }
    .agent-card.diag   { border-color: #e37400; }
    .agent-card.human  { border-color: #c62828; }
    .agent-card.presc  { border-color: #6a1b9a; }
    .agent-card.report { border-color: #00838f; }
    .step-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .badge-triage { background: #e3f2fd; color: #1a73e8; }
    .badge-rag    { background: #e8f5e9; color: #0b8043; }
    .badge-diag   { background: #fff3e0; color: #e37400; }
    .badge-human  { background: #ffebee; color: #c62828; }
    .badge-presc  { background: #f3e5f5; color: #6a1b9a; }
    .badge-report { background: #e0f7fa; color: #00838f; }
    .report-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        font-family: 'Georgia', serif;
        line-height: 1.7;
    }
    .stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

try:
    from graph import build_graph, run_until_human, resume_after_human
    GRAPH_AVAILABLE = True
except ImportError as e:
    GRAPH_AVAILABLE = False
    st.error(f"Erreur d'import du graphe : {e}")

@st.cache_resource
def get_graph():
    return build_graph()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

for key in ["state", "step", "rag_built"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "state" else (False if key == "rag_built" else "idle")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/caduceus.png", width=70)
    st.title("MediAgent")
    st.caption("Systeme Multi-Agent Medical : LangGraph + RAG")
    st.divider()

    st.subheader("Configuration")

    api_key = os.getenv("GROQ_API_KEY", "")

    if api_key:
        st.success("Cle API Groq chargee depuis .env")
    else:
        api_key = st.text_input(
            "Cle API Groq",
            type="password",
            help="En production, definissez GROQ_API_KEY dans votre fichier .env",
        )
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.info("Pour eviter de saisir la cle a chaque fois, ajoutez-la dans le fichier .env")

    st.divider()

    st.subheader("Base documentaire RAG")

    if st.button("Construire l'index RAG", use_container_width=True):
        if not api_key:
            st.error("Entrez votre cle API d'abord.")
        else:
            with st.spinner("Construction de l'index FAISS..."):
                try:
                    from agents.agent_rag import build_rag_index
                    build_rag_index()
                    st.session_state.rag_built = True
                    st.success("Index RAG pret !")
                except Exception as e:
                    st.error(f"Erreur : {e}")

    if st.session_state.rag_built:
        st.success("Index RAG disponible")

    st.divider()

    st.subheader("Evaluation A/B")
    if st.button("Lancer l'evaluation des prompts", use_container_width=True):
        if not api_key:
            st.error("Entrez votre cle API d'abord.")
        else:
            with st.spinner("Evaluation en cours (10 appels LLM)..."):
                try:
                    from evaluation import run_evaluation
                    eval_results = run_evaluation()
                    st.metric("Score Prompt A", f"{eval_results['score_a']:.0f}%")
                    st.metric("Score Prompt B", f"{eval_results['score_b']:.0f}%")
                    winner = "B (detaille)" if eval_results['score_b'] >= eval_results['score_a'] else "A (court)"
                    st.success(f"Meilleur prompt : {winner}")
                except Exception as e:
                    st.error(f"Erreur evaluation : {e}")

    st.divider()
    if st.button("Nouvelle consultation", use_container_width=True):
        st.session_state.state = None
        st.session_state.step = "idle"
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

st.markdown("""
<div class="main-header">
    <h2 style="margin:0">MediAgent — Assistant Medical Intelligent</h2>
    <p style="margin:4px 0 0 0; opacity:0.85">
        Systeme multi-agent &middot; LangGraph &middot; RAG &middot; Human-in-the-Loop
    </p>
</div>
""", unsafe_allow_html=True)

steps = ["Triage", "RAG", "Diagnostic", "Validation", "Prescription", "Rapport"]
step_map = {
    "idle": 0, "triage_done": 1, "rag_done": 2,
    "diagnostic_done": 3, "awaiting_human": 3,
    "prescription_done": 4, "done": 5,
}
current_idx = step_map.get(st.session_state.step or "idle", 0)
cols_prog = st.columns(len(steps))
for i, (col, label) in enumerate(zip(cols_prog, steps)):
    with col:
        if i < current_idx:
            st.success(label)
        elif i == current_idx:
            st.info(label)
        else:
            st.markdown(f"<div style='text-align:center;color:#aaa'>{label}</div>", unsafe_allow_html=True)

st.markdown("---")

if st.session_state.step in [None, "idle"]:
    st.subheader("Informations patient")
    col1, col2 = st.columns([1, 2])
    with col1:
        patient_name = st.text_input("Nom du patient", placeholder="Ex : Fatima El Amrani")
    with col2:
        symptoms = st.text_area(
            "Symptomes declares",
            placeholder="Ex : Fievre a 39 C depuis 3 jours, toux seche, perte d'odorat, courbatures...",
            height=120,
        )

    if st.button("Lancer l'analyse par les agents", type="primary", use_container_width=True):
        if not api_key:
            st.error("Veuillez entrer votre cle API Groq dans la barre laterale.")
        elif not patient_name or not symptoms:
            st.warning("Remplissez le nom du patient et les symptomes.")
        else:
            initial_state = {
                "patient_name": patient_name,
                "symptoms": symptoms,
                "messages": [],
                "triage_result": None,
                "rag_context": None,
                "diagnostic": None,
                "prescription": None,
                "report": None,
                "human_approved": None,
                "human_feedback": None,
                "current_step": "start",
            }

            progress_placeholder = st.empty()
            with progress_placeholder.container():
                st.info("Etape 1/3 — Agent Triage en cours... (modele rapide)")

            try:
                if GRAPH_AVAILABLE:
                    graph = get_graph()
                    state = run_until_human(graph, initial_state, st.session_state.thread_id)

                    progress_placeholder.empty()
                    st.session_state.state = state
                    st.session_state.step = state.get("current_step", "diagnostic_done")
                    st.rerun()
            except Exception as e:
                progress_placeholder.empty()
                st.error(f"Erreur lors de l'analyse : {e}")
                st.exception(e)

if st.session_state.step in ["diagnostic_done", "awaiting_human"] and st.session_state.state:
    state = st.session_state.state
    st.subheader("Resultats des agents IA")

    tab1, tab2, tab3 = st.tabs(["Triage", "Documents RAG", "Diagnostic"])

    with tab1:
        st.markdown('<span class="step-badge badge-triage">Agent Triage</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="agent-card">{state.get("triage_result","")}</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<span class="step-badge badge-rag">Agent RAG</span>', unsafe_allow_html=True)
        context = state.get("rag_context", "")
        for block in context.split("\n\n") if context else []:
            if block.strip():
                st.markdown(f'<div class="agent-card rag">{block}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<span class="step-badge badge-diag">Agent Diagnostic</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="agent-card diag">{state.get("diagnostic","")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Validation Medicale — Human-in-the-Loop")
    st.warning("Le systeme attend votre decision avant de continuer. Veuillez examiner le diagnostic propose.")

    with st.form("human_form"):
        feedback = st.text_area(
            "Votre commentaire / correction (obligatoire)",
            placeholder="Ex : Diagnostic coherent. Ajouter un bilan sanguin NFS-CRP.",
            height=100,
        )
        col_a, col_b = st.columns(2)
        with col_a:
            approve = st.form_submit_button("Approuver et continuer", type="primary", use_container_width=True)
        with col_b:
            reject = st.form_submit_button("Rejeter la consultation", use_container_width=True)

    if approve and feedback:
        with st.spinner("Generation prescription + rapport..."):
            try:
                graph = get_graph()
                final = resume_after_human(
                    graph,
                    st.session_state.thread_id,
                    approved=True,
                    feedback=feedback,
                )
                st.session_state.state = final
                st.session_state.step = "done"
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")
                st.exception(e)
    elif approve and not feedback:
        st.error("Veuillez entrer un commentaire avant d'approuver.")
    elif reject:
        st.session_state.step = "idle"
        st.warning("Consultation rejetee. Vous pouvez relancer une nouvelle analyse.")

if st.session_state.step == "done" and st.session_state.state:
    state = st.session_state.state
    st.success("Consultation complete !")
    st.subheader("Compte-Rendu Medical Final")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f'<div class="report-box">{state.get("report","").replace(chr(10),"<br>")}</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.subheader("Prescription")
        st.markdown(
            f'<div class="agent-card presc">{state.get("prescription","")}</div>',
            unsafe_allow_html=True,
        )

    st.download_button(
        label="Telecharger le rapport (TXT)",
        data=(
            f"RAPPORT MEDICAL\n\n{state.get('report','')}"
            f"\n\n---\nPRESCRIPTION\n\n{state.get('prescription','')}"
        ),
        file_name=f"rapport_{state.get('patient_name','patient').replace(' ','_')}.txt",
        mime="text/plain",
    )