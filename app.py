import streamlit as st
import PyPDF2
import google.generativeai as genai
from fpdf import FPDF
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

# 2. CSS PROFESIONAL Y MÓVIL (FIX DE SCROLL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');

    * { font-family: 'Inter', sans-serif; }
    
    [data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Fix para permitir scroll en celulares */
    html, body, [data-testid="stAppViewContainer"] {
        overflow-y: auto !important;
    }

    .stApp { 
        background-color: #0A0A0B; 
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(223, 255, 0, 0.04) 0%, transparent 40%),
            radial-gradient(circle at 100% 100%, rgba(223, 255, 0, 0.04) 0%, transparent 40%);
        color: #E4E4E7;
    }
    
    .block-container { padding-top: 1rem !important; max-width: 700px !important; }

    /* Logo y Título */
    .brand-title {
        font-size: 52px; text-align: center; color: #DFFF00; 
        margin-bottom: 0px; font-weight: 900; letter-spacing: -3px;
        line-height: 1;
    }
    @media (max-width: 480px) { .brand-title { font-size: 40px; } }

    .brand-subtitle {
        color: #71717A; text-align: center; margin-bottom: 30px; 
        font-size: 14px; font-weight: 300; letter-spacing: 1px;
    }

    /* Tarjetas de Vidrio */
    .stCard {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 20px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 15px;
    }

    /* Labels de sección */
    .section-label {
        color: #DFFF00; font-size: 10px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 2px;
        margin-bottom: 8px; opacity: 0.9;
    }

    /* Inputs y Áreas de Texto */
    .stTextArea textarea {
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important; color: #DFFF00 !important;
        font-size: 14px !important;
    }

    /* Tabs Móviles */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px; border-radius: 10px; border: none;
        background-color: rgba(255,255,255,0.03); color: #71717A;
        font-size: 12px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #DFFF00 !important; color: #000 !important; font-weight: 700;
    }

    /* Botón de Acción */
    div.stButton > button {
        background: #DFFF00 !important; color: #000 !important;
        border-radius: 14px !important; font-weight: 800 !important;
        height: 50px !important; width: 100%; border: none;
        text-transform: uppercase; letter-spacing: 1px;
    }

    .ai-response {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px; padding: 20px;
        border-left: 4px solid #DFFF00; color: #D1D1D6;
        font-size: 14px; line-height: 1.6;
    }

    /* Fix para el selector de idioma en móvil */
    .stSelectbox label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS (LOS 10 SOLICITADOS) ---
idiomas_data = {
    "Español": {"leg": "Optimización ATS y Preparación Profesional.", "tabs": ["Análisis", "Optimizar", "Empresa", "Coach", "Historial"], "ia": "Responde en Español."},
    "English": {"leg": "ATS Optimization & Interview Readiness.", "tabs": ["Analysis", "Optimize", "Company", "Coach", "History"], "ia": "Respond in English."},
    "Français": {"leg": "Optimisation ATS et Préparation.", "tabs": ["Analyse", "Optimiser", "Entreprise", "Coach", "Historique"], "ia": "Répondez en Français."},
    "Português": {"leg": "Otimização de ATS e Preparação.", "tabs": ["Análise", "Otimizar", "Empresa", "Coach", "Histórico"], "ia": "Responda em Português."},
    "Deutsch": {"leg": "ATS-Optimierung und Vorbereitung.", "tabs": ["Analyse", "Optimieren", "Unternehmen", "Coach", "Verlauf"], "ia": "Antworte auf Deutsch."},
    "Italiano": {"leg": "Ottimizzazione ATS e Preparazione.", "tabs": ["Analisi", "Ottimizza", "Azienda", "Coach", "Cronologia"], "ia": "Rispondi in Italiano."},
    "Русский": {"leg": "Оптимиización ATS и подготовка.", "tabs": ["Анализ", "Оптимизация", "Компания", "Коуч", "История"], "ia": "Отвечай по-русски."},
    "中文": {"leg": "ATS 优化和准备。", "tabs": ["分析", "优化", "公司", "教练", "历史"], "ia": "用中文回答。"},
    "日本語": {"leg": "ATS最適化と準備。", "tabs": ["分析", "最適化", "企業", "コーチ", "履歴"], "ia": "日本語で答えて。"},
    "한국어": {"leg": "ATS 최적화 및 준비.", "tabs": ["분석", "최적화", "기업", "코치", "히스토리"], "ia": "한국어로 답변해."}
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
        return "Error de conexión. Verifica la configuración."

# --- INTERFAZ ---
if "historial" not in st.session_state: st.session_state.historial = []

# Selector de Idioma (Sección superior limpia)
lang_col1, lang_col2 = st.columns([2, 1])
with lang_col2:
    sel_lang = st.selectbox("Idioma", list(idiomas_data.keys()), label_visibility="collapsed")
    t = idiomas_data[sel_lang]

st.markdown("<h1 class='brand-title'>workersCV</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='brand-subtitle'>{t['leg']}</p>", unsafe_allow_html=True)

# PANEL CENTRAL
st.markdown('<div class="stCard">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="section-label">Tu CV (PDF)</div>', unsafe_allow_html=True)
    cv_f = st.file_uploader("c", type="pdf", label_visibility="collapsed")
with c2:
    st.markdown('<div class="section-label">Oferta Laboral</div>', unsafe_allow_html=True)
    job = st.text_area("j", placeholder="Pega la oferta aquí...", height=80, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Lógica
cv_texto = ""
if cv_f:
    r = PyPDF2.PdfReader(cv_f)
    for pg in r.pages: cv_texto += pg.extract_text()

tabs = st.tabs(t["tabs"])

with tabs[0]: # ANÁLISIS
    if st.button("ANALIZAR MATCH →"):
        if not cv_texto or not job: st.warning("Faltan datos")
        else:
            with st.spinner("..."):
                res = llamar_ia(f"{t['ia']} Score 0-100 y 2 consejos. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div class="ai-response">{res}</div>', unsafe_allow_html=True)
                score = re.search(r'\d+', res).group() if re.search(r'\d+', res) else "0"
                st.session_state.historial.insert(0, {"f": datetime.now().strftime("%H:%M"), "s": score})

with tabs[1]: # OPTIMIZAR
    if st.button("DISEÑAR CV ATS PRO →"):
        if not cv_texto or not job: st.warning("Faltan datos")
        else:
            with st.spinner("..."):
                raw = llamar_ia(f"{t['ia']} CV ATS, una hoja. Sin horarios. Disponibilidad inmediata. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div class="ai-response">{raw}</div>', unsafe_allow_html=True)

with tabs[2]: # EMPRESA
    emp_n = st.text_input("e", placeholder="Nombre de la empresa...", label_visibility="collapsed")
    if st.button("INVESTIGAR VALORES →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(f"{t['ia']} Historia y cultura de {emp_n}")}</div>', unsafe_allow_html=True)

with tabs[3]: # COACH
    if st.button("SIMULAR PREGUNTAS →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(f"{t['ia']} 3 preguntas difíciles para este puesto según mi CV")}</div>', unsafe_allow_html=True)

with tabs[4]: # HISTORIAL
    for i in st.session_state.historial[:5]:
        st.write(f"🕒 {i['f']} - Match Score: **{i['s']}%**")

st.markdown("<br><center style='opacity:0.05;'>⚙️ &nbsp; &nbsp; 📱 &nbsp; &nbsp; 👤</center>", unsafe_allow_html=True)
