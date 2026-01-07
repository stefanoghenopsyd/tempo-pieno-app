import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Test Gestione del Tempo", page_icon="⏱️", layout="wide")

# --- DEFINIZIONE PROFILI E LOGICA ---
PROFILES = {
    "Architetto Perfezionista": {
        "traits": ["Analitico", "Razionale", "Concentrato"],
        "desc": "Sei meticoloso e logico. Il tuo rischio è il 'Maximizing': cercare la perfezione assoluta a costo di non agire.",
        "strategy": "Adotta il Satisficing. Usa l'MVP Mentale: 'Fatto è meglio di perfetto'."
    },
    "Pompiere Reattivo": {
        "traits": ["Sintetico", "Razionale", "Distratto"],
        "desc": "Pragmatico e veloce, ma vivi di emergenze (Fire-fighting Culture).",
        "strategy": "Difendi il Quadrante 2. Blocca tempo inviolabile per la prevenzione."
    },
    "Navigatore in Tempesta": {
        "traits": ["Sintetico", "Emotivo", "Distratto"],
        "desc": "Creativo ed empatico, ma soffri di FoMO e caos organizzativo.",
        "strategy": "Usa i 'Patti di Ulisse' (barriere esterne) e l'Assertività Empatica."
    },
    "Analista Bloccato": {
        "traits": ["Analitico", "Emotivo", "Distratto"],
        "desc": "Vorresti approfondire tutto ma l'ansia ti blocca e ti rifugi nelle distrazioni.",
        "strategy": "Usa il metodo GTD (Next Action) e la Regola dei 2 Minuti per sbloccarti."
    },
    "Visionario Disconnesso": {
        "traits": ["Sintetico", "Emotivo", "Concentrato"],
        "desc": "Capace di Deep Work ma pessimo con le scadenze (Chronos).",
        "strategy": "Ancora il flusso creativo a scadenze artificiali (Milestones)."
    },
    "Stacanovista Digitale": {
        "traits": ["Analitico", "Razionale", "Distratto"],
        "desc": "Lavori molto e con logica, ma paghi una 'tassa cognitiva' alta per la reperibilità continua.",
        "strategy": "Comunicazione asincrona obbligatoria e disconnessione totale nel weekend."
    }
}

QUESTIONS = [
    # Analitico (A) vs Sintetico (B)
    {"id": "P1_Q1", "polarita": "Analitico_Sintetico", "text": "Di fronte a una decisione complessa o all'avvio di un progetto:", "options": {"A": "Analizzo ogni scenario (paura di perdere dettagli).", "B": "Parto subito con il quadro generale (correggo in corsa)."}},
    {"id": "P1_Q2", "polarita": "Analitico_Sintetico", "text": "Quando devi consegnare un lavoro:", "options": {"A": "Fatico a dire 'basta', rifinisco all'infinito.", "B": "Consegno appena è accettabile."}},
    {"id": "P1_Q3", "polarita": "Analitico_Sintetico", "text": "La tua To-Do List:", "options": {"A": "Lunga e dettagliatissima.", "B": "Sommaria o inesistente."}},
    # Razionale (A) vs Emotivo (B)
    {"id": "P2_Q1", "polarita": "Razionale_Emotivo", "text": "Motivo principale della procrastinazione?", "options": {"A": "Errore di calcolo tempi/priorità.", "B": "Ansia/Noia (evitamento emotivo)."}},
    {"id": "P2_Q2", "polarita": "Razionale_Emotivo", "text": "Reazione agli imprevisti?", "options": {"A": "Fastidio, ma ricalcolo l'agenda.", "B": "Senso di colpa/sopraffazione (dico Sì per non deludere)."}},
    {"id": "P2_Q3", "polarita": "Razionale_Emotivo", "text": "Cosa ti motiva?", "options": {"A": "Scadenze e KPI.", "B": "Il 'senso' e la passione."}},
    # Concentrazione (A) vs Distrazione (B)
    {"id": "P3_Q1", "polarita": "Concentrazione_Distrazione", "text": "Gestione email/chat?", "options": {"A": "A orari fissi o ignorate durante il lavoro.", "B": "Risposta in tempo reale (notifiche attive)."}},
    {"id": "P3_Q2", "polarita": "Concentrazione_Distrazione", "text": "Modo di lavorare ideale?", "options": {"A": "Deep Work (blocchi lunghi).", "B": "Multitasking (più cose insieme)."}},
    {"id": "P3_Q3", "polarita": "Concentrazione_Distrazione", "text": "Sensazione a fine giornata?", "options": {"A": "Stanco ma soddisfatto (poche cose fatte bene).", "B": "Esausto e inconcludente (Shallow Work)."}}
]

def save_to_google_sheet(data):
    """Salva su Google Sheets usando st.secrets per la sicurezza su GitHub"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Carica le credenziali dai Secrets di Streamlit invece che dal file locale
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Sostituisci con il nome esatto del tuo foglio Google
        sheet = client.open("TimeManagementResults").sheet1 
        
        row = [str(datetime.now())] + list(data.values())
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Errore di connessione al Database: {e}")
        return False

def calculate_results(responses):
    scores = {"Analitico_Sintetico": {"A": 0, "B": 0}, "Razionale_Emotivo": {"A": 0, "B": 0}, "Concentrazione_Distrazione": {"A": 0, "B": 0}}
    
    p1_list, p2_list, p3_list = [], [], []
    
    for q in QUESTIONS:
        val = responses[q["id"]]
        scores[q["polarita"]][val] += 1
        if q["polarita"] == "Analitico_Sintetico": p1_list.append(val)
        elif q["polarita"] == "Razionale_Emotivo": p2_list.append(val)
        else: p3_list.append(val)
        
    p1 = "Analitico" if p1_list.count("A") > p1_list.count("B") else "Sintetico"
    p2 = "Razionale" if p2_list.count("A") > p2_list.count("B") else "Emotivo"
    p3 = "Concentrato" if p3_list.count("A") > p3_list.count("B") else "Distratto"
    
    user_traits = [p1, p2, p3]
    
    matched_profile = None
    for name, details in PROFILES.items():
        if details["traits"] == user_traits:
            matched_profile = (name, details)
            break
    
    if not matched_profile:
        matched_profile = ("Profilo Ibrido", {"desc": "Hai una combinazione unica. Guarda il grafico per i dettagli.", "strategy": "Analizza le singole polarità."})
        
    return scores, matched_profile, user_traits

def draw_chart(scores):
    categories = ['Stile Cognitivo', 'Stile Emotivo', 'Attenzione']
    val_a = [scores['Analitico_Sintetico']['A'], scores['Razionale_Emotivo']['A'], scores['Concentrazione_Distrazione']['A']]
    val_b = [-scores['Analitico_Sintetico']['B'], -scores['Razionale_Emotivo']['B'], -scores['Concentrazione_Distrazione']['B']]

    fig = go.Figure()
    fig.add_trace(go.Bar(y=categories, x=val_b, name='Sintetico / Emotivo / Distratto', orientation='h', marker=dict(color='#FF7F50')))
    fig.add_trace(go.Bar(y=categories, x=val_a, name='Analitico / Razionale / Concentrato', orientation='h', marker=dict(color='#4682B4')))
    
    fig.update_layout(title="La tua Bussola Gestionale", barmode='relative', xaxis=dict(range=[-3.5, 3.5], tickvals=[-3, 0, 3], ticktext=['Polarità B', 'Centro', 'Polarità A']), height=400)
    return fig

# --- UI PRINCIPALE ---
st.title("⏱️ Tempo Pieno: Che gestore sei?")

with st.expander("ℹ️ Introduzione e Istruzioni", expanded=True):
    st.markdown("""
    Benvenuto nel test diagnostico basato sul metodo **Tempo Pieno**.
    Non misureremo quanto sei veloce, ma **come funzioni**.
    
    Il test indaga tre polarità:
    1.  **Analitico vs Sintetico**: Come prendi decisioni.
    2.  **Razionale vs Emotivo**: Cosa innesca la tua azione (o inazione).
    3.  **Concentrazione vs Distrazione**: Come gestisci l'attenzione.
    """)

with st.form("quiz_form"):
    responses = {}
    st.markdown("### 1. Come decidi?")
    for q in QUESTIONS[:3]:
        responses[q["id"]] = st.radio(q["text"], ["A", "B"], format_func=lambda x: q["options"][x], key=q["id"], horizontal=False)
    
    st.markdown("### 2. Cosa ti muove?")
    for q in QUESTIONS[3:6]:
        responses[q["id"]] = st.radio(q["text"], ["A", "B"], format_func=lambda x: q["options"][x], key=q["id"], horizontal=False)
        
    st.markdown("### 3. Come lavori?")
    for q in QUESTIONS[6:]:
        responses[q["id"]] = st.radio(q["text"], ["A", "B"], format_func=lambda x: q["options"][x], key=q["id"], horizontal=False)
        
    submitted = st.form_submit_button("Analizza il mio Profilo", type="primary")

if submitted:
    scores, (p_name, p_data), traits = calculate_results(responses)
    
    # Sezione Risultati
    st.divider()
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.header(f"Sei un: {p_name}")
        st.caption(f"Tratti: {traits[0]} - {traits[1]} - {traits[2]}")
        st.markdown(f"**Analisi:** {p_data['desc']}")
        st.success(f"**Strategia Chiave:** {p_data['strategy']}")
    
    with c2:
        st.plotly_chart(draw_chart(scores), use_container_width=True)

    # Salvataggio Dati
    save_data = {"Profilo": p_name, "Analitico": scores['Analitico_Sintetico']['A'], "Sintetico": scores['Analitico_Sintetico']['B'], "Razionale": scores['Razionale_Emotivo']['A'], "Emotivo": scores['Razionale_Emotivo']['B'], "Concentrato": scores['Concentrazione_Distrazione']['A'], "Distratto": scores['Concentrazione_Distrazione']['B']}
    
    # Verifica se i segreti esistono prima di tentare il salvataggio
    if "gcp_service_account" in st.secrets:
        if save_to_google_sheet(save_data):
            st.toast("Dati salvati nel database!", icon="✅")
    else:
        st.warning("⚠️ Modalità Demo: Configura i 'Secrets' su Streamlit Cloud per abilitare il salvataggio su Drive.")
