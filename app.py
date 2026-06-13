import streamlit as st
import PyPDF2
import google.generativeai as genai
import base64
import io
import re
import time
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA
try:
    fav = Image.open("favicon.png")
    st.set_page_config(page_title="workersCV | AI Agency", page_icon=fav, layout="wide")
except:
    st.set_page_config(page_title="workersCV", page_icon="🎯", layout="wide")

# --- FUNCIÓN MÁGICA PARA EL VIDEO DE FONDO ---
def get_video_base64(video_path):
    with open(video_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Intentar cargar el video
try:
    video_base64 = get_video_base64("background.mp4")
    video_html = f'''
        <video autoplay loop muted playsinline class="video-bg">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
    '''
except:
    video_html = '<div class="video-bg" style="background:#0A0A0B;"></div>'

# 2. DISEÑO NEXUS AI CON VIDEO
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;700;800&family=Instrument+Serif:ital@1&family=Inter:wght@900&display=swap');

    #MainMenu, footer, header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* Estilo del Video de Fondo */
    .video-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: -1;
        filter: brightness(0.5); /* Oscurece un poco el video para que se lea el texto */
    }}

    .hero-section {{
        position: relative;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: white;
        padding: 0 5%;
    }}

    .h1-line1 {{ font-family: 'Barlow', sans-serif; font-size: 70px; font-weight: 800; margin: 0; line-height: 1; text-shadow: 2px 2px 20px rgba(0,0,0,0.5); }}
    .h1-line2 {{ font-family: 'Instrument Serif', serif; font-style: italic; font-size: 110px; margin: 0; line-height: 1; text-shadow: 2px 2px 20px rgba(0,0,0,0.5); }}
    .subtext {{ font-family: 'Barlow', sans-serif; font-size: 20px; color: rgba(255,255,255,0.8); max-width: 700px; margin: 30px 0; }}

    /* Widgets Glassmorphism */
    .widget {{
        position: fixed;
        bottom: 30px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 25px;
        border-radius: 20px;
        z-index: 10;
        color: white;
    }}
    .widget-left {{ left: 30px; }}
    .widget-right {{ right: 30px; border-radius: 50px; }}

    .pulse {{
        height: 8px; width: 8px; background: #DFFF00; border-radius: 50%;
        display: inline-block; margin-right: 10px; box-shadow: 0 0 10px #DFFF00;
        animation: pulse-kf 2s infinite;
    }}
    @keyframes pulse-kf {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}

    /* Área de la App */
    .tool-container {{
        background: #0A0A0B;
        padding: 80px 5%;
        display: flex;
        justify-content: center;
    }}
    .tool-card {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 30px;
        padding: 40px;
        max-width: 800px;
        width: 100%;
    }}

    div.stButton > button {{
        background: #DFFF00 !important;
        color: black !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        height: 55px !important;
        width: 100% !important;
        border: none !important;
        text-transform: uppercase;
    }}
    </style>

    {video_html}

    <div class="hero-section">
        <div style="position: absolute; top: 40px; left: 5%; font-family:'Inter'; font-weight:900; font-size:24px;">
            Workers<span style="color:#DFFF00;">CV</span>
        </div>
        <p class="h1-line1">Transformamos empresas con</p>
        <p class="h1-line2">IA de Alto Rendimiento</p>
        <p class="subtext">Optimización ATS y Preparación Profesional con Ingeniería de Datos.</p>
        <a href="#tool" style="text-decoration:none;">
            <div style="background:#DFFF00; color:black; padding:15px 40px; border-radius:50px; font-family:'Barlow'; font-weight:800; font-size:16px;">
                EXPLORAR SOLUCIONES IA
            </div>
        </a>
    </div>

    <div class="widget widget-left">
        <div style="font-family:'Barlow'; font-weight:700; font-size:11px; letter-spacing:1px;">
            <span class="pulse"></span>AI CORE: ONLINE
        </div>
        <div style="font-family:'Barlow'; opacity:0.6; font-size:10px; margin-top:5px;">
            📍 GENERAL RODRÍGUEZ, ARGENTINA
        </div>
    </div>

    <div class="widget widget-right">
        <div style="font-family:'Barlow'; font-weight:700; font-size:10px; letter-spacing:1px;">
            NEXUS ECOSYSTEM
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. LÓGICA DE LA IA
def llamar_ia(p):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(p).text
    except: return "Error de conexión."

# 4. SECCIÓN DE LA HERRAMIENTA
st.markdown('<div id="tool" class="tool-container">', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:#DFFF00; font-family:Barlow; font-weight:700; font-size:12px;">TU PERFIL (PDF)</p>', unsafe_allow_html=True)
        cv_f = st.file_uploader("cv", type="pdf", label_visibility="collapsed")
    with col2:
        st.markdown('<p style="color:#DFFF00; font-family:Barlow; font-weight:700; font-size:12px;">OFERTA LABORAL</p>', unsafe_allow_html=True)
        job = st.text_area("job", placeholder="Pega los requisitos aquí...", height=70, label_visibility="collapsed")

    cv_texto = ""
    if cv_f:
        pdf_r = PyPDF2.PdfReader(cv_f)
        for pg in pdf_r.pages: cv_texto += pg.extract_text()

    tab1, tab2, tab3 = st.tabs(["Análisis", "Optimizar", "Coach"])

    with tab1:
        if st.button("ANALIZAR COMPATIBILIDAD →"):
            with st.spinner("..."):
                res = llamar_ia(f"Score 0-100 y 2 consejos en Español. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:20px; border-left:4px solid #DFFF00; margin-top:20px;">{res}</div>', unsafe_allow_html=True)

    with tab2:
        if st.button("DISEÑAR CV ATS PRO →"):
            with st.spinner("..."):
                raw = llamar_ia(f"CV ATS en Español, una carilla. Sin horarios. Disponibilidad inmediata. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:20px; margin-top:20px;">{raw}</div>', unsafe_allow_html=True)

    with tab3:
        if st.button("PREPARAR ENTREVISTA →"):
            with st.spinner("..."):
                res = llamar_ia(f"3 preguntas difíciles para {job}")
                st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:20px; margin-top:20px;">{res}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
