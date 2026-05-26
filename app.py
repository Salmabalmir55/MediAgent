import streamlit as st
import os
import uuid
import warnings
from dotenv import load_dotenv
import json
import re

# Import pour la génération de PDF native et robuste côté serveur
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*Accessing `__path__`.*")

load_dotenv(override=True)

st.set_page_config(
    page_title="MediAgent — Assistant Médical IA",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ENGINE GRAPHIQUE CSS (Interface Streamlit uniquement)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stSidebar"], .stMarkdown {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(120deg, #ffffff 30%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .agent-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 5px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #f1f5f9;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        backdrop-filter: blur(8px);
    }
    .agent-card.rag    { border-left-color: #10b981; }
    .agent-card.diag   { border-left-color: #f59e0b; }
    .agent-card.human  { border-left-color: #ef4444; }
    .agent-card.presc  { border-left-color: #8b5cf6; }
    .agent-card.report { border-left-color: #14b8a6; }
    
    .step-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .badge-triage { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-rag    { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-diag   { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-human  { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-presc  { background-color: rgba(139, 92, 246, 0.15); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }
    .badge-report { background-color: rgba(20, 184, 166, 0.15); color: #2dd4bf; border: 1px solid rgba(20, 184, 166, 0.3); }
    
    .report-box, .prescription-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 2.5rem;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        color: #0f172a;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .flow-wrapper {
        overflow-x: auto;
        padding: 1.5rem 0;
    }
    .flow-container {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        flex-wrap: nowrap;
        gap: 12px;
        min-width: 900px;
    }
    .flow-node {
        flex: 1;
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 16px 8px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .flow-node-icon { font-size: 24px; }
    .flow-node-name { font-weight: 600; font-size: 13px; margin-top: 8px; color: #ffffff; }
    .flow-node-role { font-size: 11px; color: #94a3b8; margin-top: 2px; }
    
    .flow-arrow { font-size: 20px; color: #64748b; }
    .flow-arrow-interrupt {
        font-size: 10px;
        font-weight: 700;
        color: #ef4444;
        text-align: center;
        background: rgba(239, 68, 68, 0.1);
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    .custom-progress-step {
        text-align: center;
        padding: 12px 6px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .prog-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .prog-active {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #3b82f6;
    }
    .prog-idle {
        background-color: rgba(255, 255, 255, 0.05);
        color: #64748b;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# MOTEUR DE GÉNÉRATION NATIVE PDF (REPORTLAB)
def build_pdf_bytes(patient_name, report_text, prescription_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Styles customisés
    style_title_rep = ParagraphStyle('RepTitle', parent=styles['Heading1'], textColor=colors.HexColor('#1e40af'), fontSize=18, spaceAfter=12, fontName="Helvetica-Bold")
    style_title_pre = ParagraphStyle('PresTitle', parent=styles['Heading1'], textColor=colors.HexColor('#7c3aed'), fontSize=18, spaceAfter=12, fontName="Helvetica-Bold")
    style_meta = ParagraphStyle('MetaText', parent=styles['Normal'], textColor=colors.HexColor('#64748b'), fontSize=10, spaceAfter=20, fontName="Helvetica-Oblique")
    style_body = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], textColor=colors.HexColor('#0f172a'), fontSize=11, leading=16, spaceAfter=10, alignment=TA_JUSTIFY, fontName="Helvetica")
    
    # --- PAGE 1 : COMPTE-RENDU ---
    story.append(Paragraph("📋 COMPTE-RENDU CLINIQUE SYNTHÉTIQUE", style_title_rep))
    story.append(Paragraph(f"<b>Patient :</b> {patient_name} | Document généré par le Hub Clinique MediAgent", style_meta))
    
    # Nettoyage et injection du texte du compte-rendu
    clean_report = report_text.replace("**", "")
    for paragraph in clean_report.split('\n'):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), style_body))
            
    # Saut de page pour séparer l'ordonnance (40px simulé + page propre)
    story.append(PageBreak())
    
    # --- PAGE 2 : ORDONNANCE ---
    story.append(Paragraph("💊 ORDONNANCE MÉDICALE THÉRAPEUTIQUE", style_title_pre))
    story.append(Paragraph(f"<b>Patient :</b> {patient_name} | Avis médical requis avant délivrance", style_meta))
    
    # Nettoyage et injection du texte de l'ordonnance
    clean_prescription = prescription_text.replace("**", "")
    for paragraph in clean_prescription.split('\n'):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), style_body))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

try:
    from graph import build_graph, run_until_human, resume_after_human
    GRAPH_AVAILABLE = True
except ImportError as e:
    GRAPH_AVAILABLE = False
    st.error(f"Erreur d'import du graphe : {e}")

try:
    from evaluation import run_evaluation
    EVAL_AVAILABLE = True
except ImportError:
    EVAL_AVAILABLE = False

try:
    from langflow_integration import save_graph_for_langflow, get_graph_json, get_graph_structure_summary
    LANGFLOW_AVAILABLE = True
except ImportError:
    LANGFLOW_AVAILABLE = False

@st.cache_resource
def get_graph():
    return build_graph()

def render_enhanced_graph_visualization():
    st.markdown("### 🕸️ Flux d'interaction des agents LangGraph")
    st.caption("Workflow séquentiel interactif avec point d'arrêt humain (Human-in-the-Loop)")
    
    agents_info = [
        {"name": "Triage", "role": "Urgence", "color": "#3b82f6", "icon": "🚨"},
        {"name": "RAG", "role": "Documents", "color": "#10b981", "icon": "📚"},
        {"name": "Diagnostic", "role": "Analyse", "color": "#f59e0b", "icon": "🩺"},
        {"name": "Validation", "role": "Médecin", "color": "#ef4444", "icon": "👨‍⚕️"},
        {"name": "Prescription", "role": "Traitement", "color": "#8b5cf6", "icon": "💊"},
        {"name": "Rapport", "role": "Synthèse", "color": "#14b8a6", "icon": "📄"}
    ]
    
    st.markdown('<div class="flow-wrapper"><div class="flow-container">', unsafe_allow_html=True)
    for i, agent in enumerate(agents_info):
        st.markdown(f"""
        <div class="flow-node" style="border-bottom: 3px solid {agent['color']};">
            <div class="flow-node-icon">{agent['icon']}</div>
            <div class="flow-node-name">{agent['name']}</div>
            <div class="flow-node-role">{agent['role']}</div>
        </div>
        """, unsafe_allow_html=True)
        if i < len(agents_info) - 1:
            if i == 3:
                st.markdown('<div class="flow-arrow-interrupt">⏸️ WAIT</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="flow-arrow">➡️</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown("---")

def render_simple_graph_visualization():
    if not LANGFLOW_AVAILABLE:
        st.warning("Module langflow_integration non disponible")
        return
    try:
        graph = get_graph()
        graph_summary = get_graph_structure_summary(graph)
        st.markdown("### Visualisation du Graphe Multi-Agent")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Nombre d'agents", graph_summary["total_nodes"])
        with col2: st.metric("Point d'entrée", graph_summary.get("entry_point", "triage"))
        with col3: st.metric("Points d'arrêt", len(graph_summary.get("checkpoints", [])))
            
        agents = graph_summary.get("agents", [])
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#14b8a6"]
        st.markdown("#### Flux du workflow")
        cols = st.columns(len(agents))
        for i, (col, agent) in enumerate(zip(cols, agents)):
            color = colors[i % len(colors)]
            with col:
                st.markdown(f"""
                <div style='text-align:center; padding:12px; background:rgba(255,255,255,0.02); border-radius:12px; border-bottom:3px solid {color}; margin:4px'>
                    <strong style='color:{color}'>{agent.upper().replace('_', ' ')}</strong>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur visualisation graphe: {e}")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

for key in ["state", "step", "rag_built", "show_graph", "use_enhanced_graph"]:
    if key not in st.session_state:
        if key == "show_graph": st.session_state[key] = False
        elif key == "use_enhanced_graph": st.session_state[key] = True
        else: st.session_state[key] = None if key == "state" else (False if key == "rag_built" else "idle")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/caduceus.png", width=65)
    st.title("🩺 MediAgent")
    st.caption("Système Décisionnel Clinique")
    st.divider()
    
    st.subheader("⚙️ Configuration")
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key:
        st.success("✅ Connexion Groq Active")
    else:
        api_key = st.text_input("Clé API Groq", type="password")
        if api_key: os.environ["GROQ_API_KEY"] = api_key
            
    st.divider()
    st.subheader("📚 Moteur Documentaire RAG")
    if st.button("🔨 Synchroniser la Base RAG", use_container_width=True):
        if not api_key:
            st.error("Entrez votre clé API d'abord.")
        else:
            with st.spinner("Indexation vectorielle FAISS..."):
                try:
                    from agents.agent_rag import build_rag_index
                    build_rag_index()
                    st.session_state.rag_built = True
                    st.success("✅ Index RAG opérationnel")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    
    if st.session_state.rag_built: st.info("💡 Index RAG chargé en mémoire")
        
    st.divider()
    st.subheader("🕸️ Topologie de Graphe")
    view_mode = st.radio("Pipeline UI", ["✨ Architecture Visuelle", "🔧 Schéma Brut Blueprint"])
    st.session_state.use_enhanced_graph = (view_mode == "✨ Architecture Visuelle")
    
    if st.button("📊 Afficher la Carte Métier", use_container_width=True): st.session_state.show_graph = True
    if st.session_state.get("show_graph", False):
        if st.button("❌ Fermer le Graphique", use_container_width=True):
            st.session_state.show_graph = False
            st.rerun()
            
    st.divider()
    if st.button("🔄 Nouvelle Session", use_container_width=True):
        st.session_state.state = None
        st.session_state.step = "idle"
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.show_graph = False
        st.rerun()

st.markdown("""
<div class="main-header">
<h1>🏥 MediAgent — Hub Clinique IA</h1>
<p style="margin:8px 0 0 0; opacity:0.8; font-size:1.05rem; font-weight:300;">Architecture Décisionnelle Distribuée de Haute Precision via LangGraph & RAG Core</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("show_graph", False):
    if st.session_state.use_enhanced_graph: render_enhanced_graph_visualization()
    else: render_simple_graph_visualization()

steps = ["Triage", "RAG Engine", "Diagnostic", "Validation", "Prescription", "Rapport"]
step_map = {"idle": 0, "triage_done": 1, "rag_done": 2, "diagnostic_done": 3, "awaiting_human": 3, "prescription_done": 4, "done": 5}
current_idx = step_map.get(st.session_state.step or "idle", 0)
cols = st.columns(6)
for i, (col, label) in enumerate(zip(cols, steps)):
    with col:
        if i < current_idx: st.markdown(f'<div class="custom-progress-step prog-success">✓ {label}</div>', unsafe_allow_html=True)
        elif i == current_idx: st.markdown(f'<div class="custom-progress-step prog-active">⏳ {label}</div>', unsafe_allow_html=True)
        else: st.markdown(f'<div class="custom-progress-step prog-idle">{label}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.step in [None, "idle"]:
    st.subheader("📝 Dossier d'Admission Patient")
    col1, col2 = st.columns([1, 2])
    with col1: patient_name = st.text_input("Identité Patient", placeholder="Ex: Fatima El Amrani")
    with col2: symptoms = st.text_area("Anamnèse & Symptomatologie Clinique", placeholder="Saisissez les observations cliniques détaillées...", height=120)
        
    if st.button("🚀 Soumettre au Consilium d'Agents", type="primary", use_container_width=True):
        if not api_key: st.error("Clé API absente.")
        elif not patient_name or not symptoms: st.warning("Champs requis manquants.")
        else:
            initial_state = {"patient_name": patient_name, "symptoms": symptoms, "messages": [], "triage_result": None, "rag_context": None, "diagnostic": None, "prescription": None, "report": None, "human_approved": None, "human_feedback": None, "current_step": "start"}
            progress_placeholder = st.empty()
            with progress_placeholder.container(): st.info("🔄 Orchestration LangGraph : Analyse de l'Agent Triage...")
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
                st.error(f"Erreur d'exécution : {e}")

if st.session_state.step in ["diagnostic_done", "awaiting_human"] and st.session_state.state:
    state = st.session_state.state
    st.subheader("📊 Métriques Émises par les Agents")
    tab1, tab2, tab3 = st.tabs(["🚨 Triage Initial", "📚 Contexte Vectoriel RAG", "🩺 Proposition Diagnostic"])
    
    with tab1:
        st.markdown('<span class="step-badge badge-triage">Agent Triage</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="agent-card">{state.get("triage_result","")}</div>', unsafe_allow_html=True)
    with tab2:
        st.markdown('<span class="step-badge badge-rag">Agent RAG</span>', unsafe_allow_html=True)
        context = state.get("rag_context", "")
        for block in context.split("\n\n") if context else []:
            if block.strip(): st.markdown(f'<div class="agent-card rag">{block}</div>', unsafe_allow_html=True)
    with tab3:
        st.markdown('<span class="step-badge badge-diag">Agent Diagnostic</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="agent-card diag">{state.get("diagnostic","")}</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("👨‍⚕️ Arbitrage Humain Mandataire (Human-in-the-Loop)")
    with st.form("human_form"):
        feedback = st.text_area("Directives de modification ou d'approbation", placeholder="Ex: Diagnostic validé.", height=100)
        col_a, col_b = st.columns(2)
        with col_a: approve = st.form_submit_button("✅ Signer & Autoriser la Prescription", type="primary", use_container_width=True)
        with col_b: reject = st.form_submit_button("❌ Rejeter le Dossier", use_container_width=True)
            
    if approve and feedback:
        with st.spinner("Calcul de la Prescription & Génération..."):
            try:
                graph = get_graph()
                final = resume_after_human(graph, st.session_state.thread_id, approved=True, feedback=feedback)
                st.session_state.state = final
                st.session_state.step = "done"
                st.rerun()
            except Exception as e: st.error(f"Erreur d'autorisation : {e}")
    elif approve and not feedback: st.error("Veuillez renseigner un commentaire de visa médical.")
    elif reject:
        st.session_state.step = "idle"
        st.warning("Dossier rejeté par l'expert médical.")

if st.session_state.step == "done" and st.session_state.state:
    state = st.session_state.state
    st.success("🎉 Processus d'évaluation clinique finalisé avec succès.")
    st.subheader("📋 Documents Officiels Générés")
    
    raw_report = state.get("report", "")
    raw_prescription = state.get("prescription", "")
    p_name = state.get("patient_name", "Patient")
    
    def format_to_premium_html(text):
        if not text: return ""
        html_text = text.replace("\n", "<br>")
        html_text = re.sub(r'\*\*\s*([A-Z0-9]{1,3}\..*?)\s*\*\*|\*\*\s*([IVXLCDM]+\..*?)\s*\*\*', 
                           r'<h2 style="color: #1e3a8a; margin-top: 1.6rem; margin-bottom: 0.6rem; font-size: 1.35rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; font-weight:600;">\1\2</h2>', html_text)
        html_text = re.sub(r'\*\*\s*([a-z]\).*?)\s*\*\*|\*\*\s*([0-9]+\.[0-9]+\..*?)\s*\*\*', 
                           r'<h3 style="color: #2563eb; margin-top: 1.2rem; margin-bottom: 0.4rem; font-size: 1.15rem; font-weight:600;">\1\2</h3>', html_text)
        html_text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #0f172a; font-weight: 600;">\1</strong>', html_text)
        return html_text

    html_report = format_to_premium_html(raw_report)
    html_prescription = format_to_premium_html(raw_prescription)
    
    # --- DÉCOUPAGE STRATÉGIQUE DES ÉLÉMENTS HTML (Résolution du bug d'affichage lié aux f-strings) ---
    st.markdown('<div style="background:#f8fafc; padding:20px; border-radius:16px; margin-bottom:20px; color:#0f172a;">', unsafe_allow_html=True)
    
    # 1. Rendu étanche du Compte-rendu Clinique
    st.markdown(f"""
        <div class="report-box">
            <h1 style="color: #1e40af; font-size: 1.6rem; margin-top:0; margin-bottom:1.5rem; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; font-weight:700;">📋 COMPTE-RENDU CLINIQUE SYNTHÉTIQUE</h1>
            <p style="color:#64748b; font-size:0.9rem; margin-bottom:1.5rem;"><b>Patient :</b> {p_name} | <b>Document sécurisé</b></p>
            {html_report}
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Rendu de la ligne de séparation pointillée
    st.markdown('<div style="margin-top: 40px; margin-bottom: 40px; border-top: 2px dashed #cbd5e1;"></div>', unsafe_allow_html=True)
    
    # 3. Rendu étanche de l'Ordonnance Thérapeutique
    st.markdown(f"""
        <div class="prescription-box">
            <h1 style="color: #7c3aed; font-size: 1.6rem; margin-top:0; margin-bottom:1.5rem; border-bottom: 2px solid #8b5cf6; padding-bottom: 8px; font-weight:700;">💊 ORDONNANCE MÉDICALE THÉRAPEUTIQUE</h1>
            <p style="color:#64748b; font-size:0.9rem; margin-bottom:1.5rem;"><b>Patient :</b> {p_name} | <b>Avis médical requis avant délivrance</b></p>
            {html_prescription}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- BLOC DE TÉLÉCHARGEMENT & EXPORTATION ---
    st.markdown("### 📥 Téléchargements et Exports")
    down_col1, down_col2 = st.columns(2)
    
    with down_col1:
        # Export TXT Unifié
        unified_txt = f"DOSSIER MEDICAL CLINIQUE\nPATIENT: {p_name.upper()}\n\n" + raw_report + "\n\n" + raw_prescription
        st.download_button(
            label="📄 Télécharger le Dossier (.TXT)",
            data=unified_txt,
            file_name=f"dossier_{p_name.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with down_col2:
        # GÉNÉRATION ET TÉLÉCHARGEMENT DU PDF NATIF
        pdf_data = build_pdf_bytes(p_name, raw_report, raw_prescription)
        st.download_button(
            label="📥 Télécharger le Dossier Global (PDF)",
            data=pdf_data,
            file_name=f"dossier_clinique_{p_name.replace(' ','_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )