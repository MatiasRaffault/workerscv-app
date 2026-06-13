import streamlit as st
import PyPDF2
import google.generativeai as genai
import base64
import io
import re
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA
try:
    fav = Image.open("favicon.png")
    st.set_page_config(page_title="workersCV", page_icon=fav, layout="wide")
except:
    st.set_page_config(page_title="workersCV", page_icon="🎯", layout="wide")

# --- FUNCIÓN PARA CARGAR EL VIDEO ---
def get_video_base64(video_path):
    try:
        with open(video_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

video_b64 = get_video_base64("background.mp4")

# 2. DISEÑO PREMIUM SIN TEXTOS DE RELLENO
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;700;800&family=Inter:wght@900&display=swap');

    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* Video de Fondo */
    .video-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: -1;
        filter: brightness(0.4);
    }}

    .main-app-container {{
        position: relative;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 5vh;
        z-index: 1;
    }}

    /* Título principal */
    .brand-logo {{
        font-family: 'Inter', sans-serif;
        font-size: 45px;
        font-weight: 900;
        color: white;
        margin-bottom: 5px;
        text-align: center;
    }}
    .brand-logo span {{ color: #DFFF00; }}

    .brand-subtitle {{
        font-family: 'Barlow', sans-serif;
        color: rgba(255,255,255,0.5);
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 30px;
    }}

    /* Tarjeta de la Herramienta (Glassmorphism) */
    .tool-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 30px;
        max-width: 850px;
        width: 90%;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }}

    /* Labels verdes */
    .section-tag {{
        color: #DFFF00;
        font-family: 'Barlow', sans-serif;
        font-weight: 800;
        font-size: 10px;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }}

    /* Estilo de Inputs */
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #DFFF00 !important;
    }}

    /* Botón workersCV */
    div.stButton > button {{
        background: #DFFF00 !important;
        color: black !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        height: 50px !important;
        width: 100% !important;
        border: none !important;
        text-transform: uppercase;
        margin-top: 10px;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        color: #888;
        font-family: 'Barlow', sans-serif;
        font-weight: 700;
        font-size: 13px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #DFFF00 !important;
        color: black !important;
        border-radius: 10px 10px 0 0;
    }}

    /* Widget de Ubicación */
    .location-widget {{
        position: fixed;
        bottom: 30px;
        left: 30px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 10px 20px;
        border-radius: 15px;
        font-family: 'Barlow', sans-serif;
        font-size: 11px;
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# Inyectar Video si existe
if video_b64:
    st.markdown(f"""
        <video autoplay loop muted playsinline class="video-bg">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)

# 3. INTERFAZ DIRECTA
st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
st.markdown('<div class="brand-logo">Workers<span>CV</span></div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Análisis · Optimización · Coaching</div>', unsafe_allow_html=True)

# Tarjeta Central
with st.container():
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-tag">RESUME (PDF)</p>', unsafe_allow_html=True)
        cv_f = st.file_uploader("cv", type="pdf", label_visibility="collapsed")
    with col2:
        st.markdown('<p class="section-tag">JOB DESCRIPTION</p>', unsafe_allow_html=True)
        job = st.text_area("job", placeholder="Pega la oferta aquí...", height=68, label_visibility="collapsed")

    # Lógica de IA
    cv_texto = ""
    if cv_f:
        pdf_r = PyPDF2.PdfReader(cv_f)
        for pg in pdf_r.pages: cv_texto += pg.extract_text()

    # Función de IA usando Secrets
    def llamar_ia(p):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            return model.generate_content(p).text
        except: return "Error de conexión."

    # Tabs de Funciones
    tab1, tab2, tab3 = st.tabs(["🎯 Match Score", "✍️ Optimizar ATS", "🎙️ Coach Entrevista"])

    with tab1:
        if st.button("ANALIZAR COMPATIBILIDAD →"):
            if not cv_texto or not job: st.error("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"Score 0-100 y 2 consejos en Español. CV: {cv_texto} Job: {job}")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:20px; font-size:14px;">{res}</div>', unsafe_allow_html=True)

    with tab2:
        if st.button("DISEÑAR CV PRO →"):
            if not cv_texto or not job: st.error("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"Reescribe este CV para ATS en Español, una carilla. Sin horarios. Disponibilidad inmediata. CV: {cv_texto} Job: {job}")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:20px; font-size:14px;">{res}</div>', unsafe_allow_html=True)

    with tab3:
        if st.button("PREPARAR PREGUNTAS →"):
            if not cv_texto or not job: st.error("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"3 preguntas difíciles para {job} según mi perfil.")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:20px; font-size:14px;">{res}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Widget de Ubicación
st.markdown("""
    <div class="location-widget">
        <span style="color:#DFFF00; font-weight:800;">●</span> AI CORE: ONLINE<br>
        <span style="opacity:0.5;">📍 GENERAL RODRÍGUEZ, ARGENTINA</span>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
