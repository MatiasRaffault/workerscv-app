import streamlit as st
import PyPDF2
import google.generativeai as genai
import base64
import requests
import io
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA
try:
    fav = Image.open("favicon.png")
    st.set_page_config(page_title="workersCV", page_icon=fav, layout="wide")
except:
    st.set_page_config(page_title="workersCV", page_icon="🎯", layout="wide")

# --- FUNCIÓN PARA DETECTAR UBICACIÓN REAL ---
def obtener_ubicacion():
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        return f"{data['city'].upper()}, {data['country'].upper()}"
    except:
        return "UBICACIÓN DESCONOCIDA"

ubicacion_usuario = obtener_ubicacion()

# --- FUNCIÓN PARA EL VIDEO DE FONDO ---
def get_video_base64(video_path):
    try:
        with open(video_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

video_b64 = get_video_base64("background.mp4")

# 2. CSS AVANZADO: CENTRADO ABSOLUTO Y REPARACIÓN DE VIDEO
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;700;800&family=Inter:wght@900&display=swap');

    /* Reset total de Streamlit */
    #MainMenu, footer, header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    
    /* Video de fondo corregido */
    .video-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
        filter: brightness(0.4);
    }}

    /* Contenedor principal: Centrado perfecto */
    .viewport-wrapper {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 100vw;
        height: 100vh;
        position: relative;
        z-index: 1;
    }}

    /* Títulos */
    .brand-header {{
        text-align: center;
        margin-bottom: 20px;
    }}
    .brand-logo {{
        font-family: 'Inter', sans-serif;
        font-size: 50px;
        font-weight: 900;
        color: white;
        letter-spacing: -2px;
    }}
    .brand-logo span {{ color: #DFFF00; }}
    .brand-subtitle {{
        font-family: 'Barlow', sans-serif;
        color: rgba(255,255,255,0.4);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 4px;
    }}

    /* Tarjeta de la Herramienta: Glassmorphism */
    .tool-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 40px;
        width: 750px;
        max-width: 90vw;
        box-shadow: 0 40px 100px rgba(0,0,0,0.5);
    }}

    /* Estilos de botones y texto */
    div.stButton > button {{
        background: #DFFF00 !important;
        color: black !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        height: 50px !important;
        border: none !important;
        width: 100%;
        text-transform: uppercase;
    }}
    
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #DFFF00 !important;
        border-radius: 15px !important;
    }}

    /* Widgets en las esquinas */
    .status-widget {{
        position: fixed;
        bottom: 30px;
        left: 30px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 12px 20px;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        font-family: 'Barlow', sans-serif;
        z-index: 100;
    }}
    .pulse {{
        height: 8px; width: 8px; background: #DFFF00; border-radius: 50%;
        display: inline-block; margin-right: 8px; box-shadow: 0 0 10px #DFFF00;
        animation: pulse-kf 2s infinite;
    }}
    @keyframes pulse-kf {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    </style>
    """, unsafe_allow_html=True)

# Inyectar Video detrás de todo
if video_b64:
    st.markdown(f"""
        <video autoplay loop muted playsinline class="video-bg">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)

# 3. ESTRUCTURA DE LA APP (Centrada)
st.markdown('<div class="viewport-wrapper">', unsafe_allow_html=True)

with st.container():
    # Header
    st.markdown(f"""
        <div class="brand-header">
            <div class="brand-logo">Workers<span>CV</span></div>
            <div class="brand-subtitle">Artificial Intelligence Agency</div>
        </div>
    """, unsafe_allow_html=True)

    # Tarjeta de Vidrio
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:#DFFF00; font-weight:800; font-size:10px; letter-spacing:2px;">UPLOAD PDF</p>', unsafe_allow_html=True)
        cv_f = st.file_uploader("cv", type="pdf", label_visibility="collapsed")
    with col2:
        st.markdown('<p style="color:#DFFF00; font-weight:800; font-size:10px; letter-spacing:2px;">JOB DESCRIPTION</p>', unsafe_allow_html=True)
        job = st.text_area("job", placeholder="Pega la oferta aquí...", height=68, label_visibility="collapsed")

    # Lógica de IA (Usando Secrets)
    def llamar_ia(p):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            return model.generate_content(p).text
        except: return "Error de conexión."

    cv_texto = ""
    if cv_f:
        pdf_r = PyPDF2.PdfReader(cv_f)
        for pg in pdf_r.pages: cv_texto += pg.extract_text()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Match Score", "Optimize ATS", "Interview Coach"])

    with tab1:
        if st.button("RUN ANALYSIS →"):
            if not cv_texto or not job: st.warning("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"Análisis Score 0-100 y tips en Español: CV {cv_texto} vs Job {job}")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:15px; font-size:13px;">{res}</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.button("Tailor CV →"):
             with st.spinner("..."):
                    res = llamar_ia(f"Optimiza este CV para ATS en Español: CV {cv_texto} vs Job {job}")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; margin-top:15px; font-size:13px;">{res}</div>', unsafe_allow_html=True)

    with tab3:
        if st.button("Practice Questions →"):
             with st.spinner("..."):
                    res = llamar_ia(f"3 preguntas difíciles para {job} según mi perfil.")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; margin-top:15px; font-size:13px;">{res}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Cierre de tool-card

# Widgets Flotantes
st.markdown(f"""
    <div class="status-widget">
        <span class="pulse"></span>AI CORE: ONLINE<br>
        <span style="opacity:0.5; font-size:10px;">📍 {ubicacion_usuario}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Cierre de viewport-wrapper
