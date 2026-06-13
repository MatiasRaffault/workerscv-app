import streamlit as st
import PyPDF2
import google.generativeai as genai
from fpdf import FPDF
from docx import Document
import io
import re
import time
from datetime import datetime
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA
try:
    fav = Image.open("favicon.png")
    st.set_page_config(page_title="workersCV", page_icon=fav, layout="centered")
except:
    st.set_page_config(page_title="workersCV", page_icon="🎯", layout="centered")

# 2. CSS AVANZADO (ESTILO MODERNO Y MINIMALISTA)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');

    /* Reset general */
    * { font-family: 'Inter', sans-serif; }
    
    [data-testid="stSidebar"] { display: none !important; }
    label { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .stApp { 
        background-color: #0A0A0B; 
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(223, 255, 0, 0.03) 0%, transparent 40%),
            radial-gradient(circle at 100% 100%, rgba(223, 255, 0, 0.03) 0%, transparent 40%);
        color: #E4E4E7;
    }
    
    .block-container { padding-top: 2rem !important; max-width: 700px !important; }

    /* Logo y Título */
    .brand-title {
        font-size: 64px; text-align: center; color: #DFFF00; 
        margin-bottom: 0px; font-weight: 900; letter-spacing: -3px;
        line-height: 1;
    }
    .brand-subtitle {
        color: #71717A; text-align: center; margin-bottom: 40px; 
        font-size: 16px; font-weight: 300; letter-spacing: 1px;
    }

    /* Tarjetas de Vidrio */
    .stCard {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border-radius: 24px; padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 25px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    }

    /* Etiquetas de Sección */
    .section-label {
        color: #DFFF00; font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 2px;
        margin-bottom: 12px; opacity: 0.8;
    }

    /* Inputs Modernos */
    .stTextArea textarea {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important; color: #DFFF00 !important;
        padding: 15px !important; font-size: 14px !important;
    }

    /* Pestañas (Tabs) Estilizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; border-radius: 12px; border: none;
        background-color: rgba(255,255,255,0.03); color: #71717A;
        font-size: 13px; font-weight: 500; transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #DFFF00 !important; color: #000 !important; font-weight: 700;
    }

    /* Botón de Acción */
    div.stButton > button {
        background: #DFFF00 !important; color: #000 !important;
        border-radius: 16px !important; font-weight: 800 !important;
        height: 56px !important; width: 100%; border: none;
        font-size: 16px !important; text-transform: uppercase;
        letter-spacing: 1px; transition: transform 0.2s;
    }
    div.stButton > button:hover { transform: translateY(-2px); }

    /* Respuesta de la IA */
    .ai-response {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px; padding: 25px;
        border-left: 4px solid #DFFF00; color: #D1D1D6;
        font-size: 15px; line-height: 1.7;
    }

    /* Iconos inferiores */
    .footer-icons {
        margin-top: 40px; opacity: 0.1; text-align: center; font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DICCIONARIO IDIOMAS ---
idiomas = {
    "Español": {"leg": "Optimización ATS y Preparación de Entrevistas.", "tabs": ["Análisis", "Optimizar", "Empresa", "Coach", "Historial"], "ia": "Responde en Español."},
    "English": {"leg": "ATS Optimization & Interview Readiness.", "tabs": ["Analysis", "Optimize", "Company", "Coach", "History"], "ia": "Respond in English."},
    "Français": {"leg": "Optimisation ATS et Préparation.", "tabs": ["Analyse", "Optimiser", "Entreprise", "Coach", "Historique"], "ia": "Répondez en Français."},
    "Português": {"leg": "Otimização de ATS e Preparação.", "tabs": ["Análise", "Otimizar", "Empresa", "Coach", "Histórico"], "ia": "Responda em Português."},
}

# --- LÓGICA IA ---
def llamar_ia(p):
    try:
        api_key_interna = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key_interna)
        vivos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        modelo_nombre = next((m for m in vivos if "1.5-flash" in m), vivos[0])
        model = genai.GenerativeModel(modelo_nombre, generation_config={"temperature": 0.1})
        for _ in range(2):
            try: return model.generate_content(p).text
            except: time.sleep(3); continue
        return "⚠️ Servidor ocupado. Reintenta."
    except Exception as e:
        return "Error: Verifica la configuración de Secrets."

# --- GENERADORES ---
def limpiar(t): return re.sub(r'\*|_|#', '', t).strip()

class PDF(FPDF):
    def add_cv_data(self, raw):
        self.add_page(); self.set_font("Arial", size=10)
        safe = limpiar(raw).encode('latin-1', 'ignore').decode('latin-1')
        self.multi_cell(0, 5, safe)

# --- INTERFAZ workersCV ---
if "historial" not in st.session_state: st.session_state.historial = []

# Selector de Idioma Minimalista
_, col_l = st.columns([4, 1.2])
with col_l:
    sel_lang = st.selectbox("", list(idiomas.keys()), label_visibility="collapsed")
    t = idiomas[sel_lang]

st.markdown("<h1 class='brand-title'>workersCV</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='brand-subtitle'>{t['leg']}</p>", unsafe_allow_html=True)

# PANEL CENTRAL
st.markdown('<div class="stCard">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="section-label">Tu CV (PDF)</div>', unsafe_allow_html=True)
    cv_f = st.file_uploader("c", type="pdf")
with c2:
    st.markdown('<div class="section-label">Oferta Laboral</div>', unsafe_allow_html=True)
    job = st.text_area("j", placeholder="Pega la oferta aquí...", height=100)
st.markdown('</div>', unsafe_allow_html=True)

# Lógica
cv_texto = ""
if cv_f:
    r = PyPDF2.PdfReader(cv_f)
    for pg in r.pages: cv_texto += pg.extract_text()

tabs = st.tabs(t["tabs"])

with tabs[0]: # ANÁLISIS
    if st.button("ANALIZAR MATCH →"):
        if not cv_texto or not job: st.error("Faltan datos")
        else:
            with st.spinner("Analizando..."):
                res = llamar_ia(f"{t['ia']} Score 0-100 y 2 consejos. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div class="ai-response">{res}</div>', unsafe_allow_html=True)
                score = re.search(r'\d+', res).group() if re.search(r'\d+', res) else "0"
                st.session_state.historial.insert(0, {"f": datetime.now().strftime("%H:%M"), "s": score})

with tabs[1]: # OPTIMIZAR
    if st.button("DISEÑAR CV ATS PRO →"):
        if not cv_texto or not job: st.error("Faltan datos")
        else:
            with st.spinner("Optimizando..."):
                raw = llamar_ia(f"{t['ia']} Reescribe mi CV para ATS, una carilla. Sin horarios. Disponibilidad inmediata. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div class="ai-response">{raw}</div>', unsafe_allow_html=True)
                pdf = PDF(); pdf.add_cv_data(raw)
                st.download_button("📥 DESCARGAR PDF", data=pdf.output(dest='S').encode('latin-1'), file_name="workersCV_Pro.pdf")

with tabs[2]: # EMPRESA
    emp_n = st.text_input("e", placeholder="Nombre de la empresa...")
    if st.button("INVESTIGAR VALORES →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(f"{t['ia']} Historia y cultura de {emp_n}")}</div>', unsafe_allow_html=True)

with tabs[3]: # COACH
    if st.button("SIMULAR PREGUNTAS →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(f"{t['ia']} 3 preguntas clave según mi perfil para este puesto")}</div>', unsafe_allow_html=True)

with tabs[4]: # HISTORIAL
    for i in st.session_state.historial[:5]:
        st.write(f"🕒 {i['f']} - Match Score: **{i['s']}%**")

st.markdown("<div class='footer-icons'>⚙️ &nbsp; &nbsp; 📱 &nbsp; &nbsp; 👤</div>", unsafe_allow_html=True)
