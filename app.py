import streamlit as st
import PyPDF2
import google.generativeai as genai
import base64
import io
import re
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA (Favicon y Título)
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

# 2. CSS DE ALTA INGENIERÍA: FIX DE POSICIÓN Y UBICACIÓN
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;700;800&family=Inter:wght@900&display=swap');

    /* Reset total: obligamos a Streamlit a no dejar espacios blancos arriba */
    #MainMenu, footer, header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
    
    .stApp {{
        background-color: #0A0A0B;
    }}

    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
    }}

    /* Video de fondo: fijo y detrás de todo */
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

    /* Contenedor de la aplicación: Centrado Absoluto en Pantalla */
    .main-wrapper {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 10;
        overflow: hidden;
    }}

    /* Título de Marca */
    .brand-logo {{
        font-family: 'Inter', sans-serif;
        font-size: 48px;
        font-weight: 900;
        color: white;
        margin-bottom: 5px;
        letter-spacing: -2px;
    }}
    .brand-logo span {{ color: #DFFF00; }}
    
    .brand-subtitle {{
        font-family: 'Barlow', sans-serif;
        color: rgba(255,255,255,0.4);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin-bottom: 25px;
    }}

    /* Tarjeta workersCV: Efecto Vidrio */
    .tool-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 35px;
        width: 720px;
        max-width: 90vw;
        box-shadow: 0 40px 100px rgba(0,0,0,0.6);
    }}

    /* Personalización de Inputs y Tabs */
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #DFFF00 !important;
        border-radius: 15px !important;
    }}

    div.stButton > button {{
        background: #DFFF00 !important;
        color: black !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        height: 48px !important;
        border: none !important;
        width: 100%;
        text-transform: uppercase;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{ transform: scale(1.02); box-shadow: 0 0 20px rgba(223,255,0,0.3); }}

    .stTabs [aria-selected="true"] {{
        background-color: #DFFF00 !important;
        color: black !important;
        font-weight: bold;
        border-radius: 10px 10px 0 0;
    }}

    /* Widget de Ubicación Inferior */
    .status-widget {{
        position: fixed;
        bottom: 30px;
        left: 40px;
        z-index: 100;
        color: white;
        font-family: 'Barlow', sans-serif;
    }}
    .pulse {{
        height: 8px; width: 8px; background: #DFFF00; border-radius: 50%;
        display: inline-block; margin-right: 10px; box-shadow: 0 0 10px #DFFF00;
        animation: pulse-kf 2s infinite;
    }}
    @keyframes pulse-kf {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    </style>

    <!-- HTML para el Video -->
    <video autoplay loop muted playsinline class="video-bg">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <!-- Ubicación Real con JS -->
    <div class="status-widget">
        <div style="font-weight:700; font-size:11px; letter-spacing:1px;">
            <span class="pulse"></span>AI CORE: ONLINE
        </div>
        <div id="city-name" style="opacity:0.5; font-size:10px; margin-top:5px; text-transform:uppercase;">DETECTANDO UBICACIÓN...</div>
    </div>

    <script>
        fetch('https://ipapi.co/json/')
        .then(response => response.json())
        .then(data => {{
            document.getElementById('city-name').innerText = '📍 ' + data.city.toUpperCase() + ', ' + data.country_name.toUpperCase();
        }});
    </script>
""", unsafe_allow_html=True)

# 3. INTERFAZ DE LA HERRAMIENTA
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# Logo y Subtítulo
st.markdown('<div class="brand-logo">Workers<span>CV</span></div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Premium AI Career Assistant</div>', unsafe_allow_html=True)

# Tarjeta Central
with st.container():
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:#DFFF00; font-weight:800; font-size:10px; letter-spacing:2px; margin-bottom:5px;">TU PERFIL (PDF)</p>', unsafe_allow_html=True)
        cv_f = st.file_uploader("cv", type="pdf", label_visibility="collapsed")
    with col2:
        st.markdown('<p style="color:#DFFF00; font-weight:800; font-size:10px; letter-spacing:2px; margin-bottom:5px;">OFERTA LABORAL</p>', unsafe_allow_html=True)
        job = st.text_area("job", placeholder="Pega los requisitos aquí...", height=68, label_visibility="collapsed")

    # Función IA
    def llamar_ia(p):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            return model.generate_content(p).text
        except: return "Error de conexión con la IA."

    cv_t = ""
    if cv_f:
        pdf_r = PyPDF2.PdfReader(cv_f)
        for pg in pdf_r.pages: cv_t += pg.extract_text()

    tabs = st.tabs(["🎯 Match Score", "✍️ Optimize CV", "🎙️ Coach"])

    with tabs[0]:
        if st.button("RUN ANALYSIS →"):
            if not cv_t or not job: st.warning("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"Score 0-100 y 2 tips en Español. CV: {cv_t} Job: {job}")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:15px; font-size:13px;">{res}</div>', unsafe_allow_html=True)

    with tabs[1]:
        if st.button("TAILOR RESUME →"):
            with st.spinner("..."):
                res = llamar_ia(f"Reescribe este CV para ATS en Español: {cv_t} Job: {job}")
                st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:15px; font-size:13px;">{res}</div>', unsafe_allow_html=True)

    with tabs[2]:
        if st.button("GET COACHING →"):
            with st.spinner("..."):
                res = llamar_ia(f"3 preguntas difíciles para {job}")
                st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:15px; font-size:13px;">{res}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Cierre de main-wrapper
