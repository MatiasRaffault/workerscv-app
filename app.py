import streamlit as st
import PyPDF2
import google.generativeai as genai
from fpdf import FPDF
import io
import re
import time
from datetime import datetime
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA (Favicon activo)
try:
    fav = Image.open("favicon.png")
    st.set_page_config(page_title="workersCV", page_icon=fav, layout="centered", initial_sidebar_state="collapsed")
except:
    st.set_page_config(page_title="workersCV", page_icon="🎯", layout="centered", initial_sidebar_state="collapsed")

# 2. ESTILO CSS "workersCV DARK"
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    label { display: none !important; visibility: hidden !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .stApp { 
        background-color: #1A1A1A; 
        color: white;
    }
    
    .block-container { padding-top: 2rem !important; max-width: 600px !important; }

    /* Estilo workersCV */
    h1 { font-size: 50px !important; text-align: center; color: #DFFF00; margin-bottom: 5px !important; letter-spacing: -2px; }
    .legend { color: #888; text-align: center; margin-bottom: 30px; font-size: 14px; }

    .section-label {
        background-color: #DFFF00; color: black; padding: 2px 15px;
        border-radius: 50px; font-weight: 800; font-size: 10px;
        display: inline-block; margin-bottom: 8px; text-transform: uppercase;
    }

    .stCard {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px; padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    .stTextArea textarea, .stTextInput input {
        background-color: #000 !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important; color: #DFFF00 !important;
    }

    .stTabs [aria-selected="true"] { 
        background-color: #DFFF00 !important; color: black !important; font-weight: bold; border-radius: 10px 10px 0 0; 
    }

    div.stButton > button {
        background: #DFFF00 !important; color: black !important;
        border-radius: 30px !important; font-weight: 900 !important;
        height: 50px !important; border: none; text-transform: uppercase;
    }

    .ai-response {
        background: rgba(0, 0, 0, 0.6);
        border-radius: 15px; padding: 20px;
        border-left: 5px solid #DFFF00; color: #EEE; font-size: 13px; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TRADUCCIONES ---
idiomas = {
    "Español": {"ia": "Responde en Español.", "tabs": ["Análisis", "Optimizar CV", "Empresa", "Coach", "Historial"], "leg": "Optimización ATS y Simulador de Entrevistas"},
    "English": {"ia": "Respond in English.", "tabs": ["Analysis", "Optimize CV", "Company", "Coach", "History"], "leg": "ATS Optimization & Interview Simulator"},
    "Français": {"ia": "Répondez en Français.", "tabs": ["Analyse", "Optimiser", "Entreprise", "Coach", "Historique"], "leg": "Optimisation ATS"},
    "Português": {"ia": "Responda em Português.", "tabs": ["Análise", "Otimizar", "Empresa", "Coach", "Histórico"], "leg": "Otimização ATS"},
    "Deutsch": {"ia": "Antworte auf Deutsch.", "tabs": ["Analyse", "Optimieren", "Unternehmen", "Coach", "Verlauf"], "leg": "ATS-Optimierung"},
    "Italiano": {"ia": "Rispondi in Italiano.", "tabs": ["Analisi", "Ottimizza", "Azienda", "Coach", "Cronologia"], "leg": "Ottimizzazione ATS"},
}

# --- FUNCIÓN IA ---
def llamar_ia(key, p):
    try:
        genai.configure(api_key=key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        mod = next((m for m in modelos if "1.5-flash" in m), modelos[0])
        model = genai.GenerativeModel(mod, generation_config={"temperature": 0.1})
        for _ in range(2):
            try: return model.generate_content(p).text
            except: time.sleep(4); continue
        return "Error 429: Rate limit. Wait."
    except Exception as e: return str(e)

# --- INTERFAZ ---

# Selector de Idioma (Sutil arriba a la derecha)
c_title, c_lang = st.columns([4, 1])
with c_lang:
    sel_lang = st.selectbox("", list(idiomas.keys()), label_visibility="collapsed")
    t = idiomas[sel_lang]

# Título Principal centrado
st.markdown("<h1>workersCV</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='legend'>{t['leg']}</p>", unsafe_allow_html=True)

# Tarjeta Central de Entradas
st.markdown('<div class="stCard">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="section-label">API KEY</div>', unsafe_allow_html=True)
    key = st.text_input("k", type="password", placeholder="Gemini Key...")
with c2:
    st.markdown('<div class="section-label">RESUME (PDF)</div>', unsafe_allow_html=True)
    cv_f = st.file_uploader("c", type="pdf")

st.markdown('<div class="section-label">OFERTA / JOB DESCRIPTION</div>', unsafe_allow_html=True)
job = st.text_area("j", placeholder="Pega la descripción del puesto aquí...", height=80)
st.markdown('</div>', unsafe_allow_html=True)

# Procesamiento
cv_t = ""
if cv_f:
    pdf_r = PyPDF2.PdfReader(cv_f)
    for pg in pdf_r.pages: cv_t += pg.extract_text()

# Solapas
tabs = st.tabs(t["tabs"])

with tabs[0]: # MATCH
    if st.button("ANALIZAR COMPATIBILIDAD →"):
        with st.spinner("..."):
            res = llamar_ia(key, f"{t['ia']} Score 0-100 y 2 tips. CV: {cv_t} Job: {job}")
            st.markdown(f'<div class="ai-response">{res}</div>', unsafe_allow_html=True)

with tabs[1]: # OPTIMIZAR
    if st.button("GENERAR CV ATS PRO →"):
        with st.spinner("..."):
            raw = llamar_ia(key, f"{t['ia']} CV ATS, una hoja, profesional. Sin horarios. Disponibilidad inmediata. CV: {cv_t} Job: {job}")
            st.markdown(f'<div class="ai-response">{raw}</div>', unsafe_allow_html=True)

with tabs[2]: # EMPRESA
    emp = st.text_input("e", placeholder="Empresa...")
    if st.button("INVESTIGAR VALORES →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(key, f"{t['ia']} Historia y valores de {emp}")}</div>', unsafe_allow_html=True)

with tabs[3]: # COACH
    if st.button("SIMULAR PREGUNTAS →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(key, f"{t['ia']} 3 preguntas difíciles para {job}")}</div>', unsafe_allow_html=True)

with tabs[4]: # HISTORIAL
    st.info("Tus análisis recientes aparecerán aquí.")

st.markdown("<br><center style='opacity:0.1; font-size:10px;'>⚙️ &nbsp; &nbsp; 📱 &nbsp; &nbsp; 👤</center>", unsafe_allow_html=True)