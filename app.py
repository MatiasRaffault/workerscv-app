import streamlit as st
import PyPDF2
import google.generativeai as genai
import base64
import io
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA (Ícono y Título)
try:
    fav = Image.open("favicon.png")
    st.set_page_config(page_title="workersCV", page_icon=fav, layout="centered")
except:
    st.set_page_config(page_title="workersCV", page_icon="🎯", layout="centered")

# --- FUNCIÓN PARA EL VIDEO DE FONDO ---
def get_video_base64(video_path):
    try:
        with open(video_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

video_b64 = get_video_base64("background.mp4")

# 2. CSS PROFESIONAL: DISEÑO PREMIUM Y CLICS HABILITADOS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;700;800&family=Inter:wght@900&display=swap');

    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header, [data-testid="stHeader"] {{ visibility: hidden !important; }}
    
    .stApp {{
        background-color: #0A0A0B;
    }}

    /* Video de fondo: pointer-events none para que deje hacer clic */
    .video-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
        filter: brightness(0.3);
        pointer-events: none;
    }}

    /* Contenedor de la aplicación centrado */
    .block-container {{
        max-width: 700px !important;
        padding-top: 5rem !important;
        background: transparent !important;
    }}

    /* Título principal */
    .brand-logo {{
        font-family: 'Inter', sans-serif;
        font-size: 52px;
        font-weight: 900;
        color: white;
        text-align: center;
        letter-spacing: -2px;
        margin-bottom: 5px;
    }}
    .brand-logo span {{ color: #DFFF00; }}

    .brand-subtitle {{
        font-family: 'Barlow', sans-serif;
        color: rgba(255,255,255,0.4);
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-align: center;
        margin-bottom: 40px;
    }}

    /* Tarjeta workersCV: Glassmorphism */
    .tool-card {{
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 30px;
        box-shadow: 0 40px 100px rgba(0,0,0,0.5);
    }}

    /* Botón workersCV */
    div.stButton > button {{
        background: #DFFF00 !important;
        color: black !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        height: 52px !important;
        width: 100% !important;
        border: none !important;
        text-transform: uppercase;
        font-size: 14px !important;
        transition: 0.3s ease;
    }}
    div.stButton > button:hover {{ transform: scale(1.02); }}

    /* Inputs y Tabs */
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #DFFF00 !important;
        border-radius: 12px !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: #777;
        font-weight: 700;
        font-size: 14px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #DFFF00 !important;
        color: black !important;
        border-radius: 10px 10px 0 0;
    }}

    label {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# Inyectar Video de Fondo
if video_b64:
    st.markdown(f"""
        <video autoplay loop muted playsinline class="video-bg">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)

# 3. INTERFAZ VISIBLE
st.markdown('<div class="brand-logo">Workers<span>CV</span></div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Premium AI Career Assistant</div>', unsafe_allow_html=True)

# Contenedor Principal (Tarjeta de la Herramienta)
with st.container():
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    
    # Entradas de datos
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p style="color:#DFFF00; font-weight:800; font-size:10px; letter-spacing:2px; margin-bottom:8px;">TU PERFIL (PDF)</p>', unsafe_allow_html=True)
        cv_f = st.file_uploader("cv", type="pdf", label_visibility="collapsed")
    with c2:
        st.markdown('<p style="color:#DFFF00; font-weight:800; font-size:10px; letter-spacing:2px; margin-bottom:8px;">OFERTA LABORAL</p>', unsafe_allow_html=True)
        job = st.text_area("job", placeholder="Pega los requisitos aquí...", height=68, label_visibility="collapsed")

    # Lógica de IA (Usando Secrets)
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

    # Solapas de Funciones
    tab1, tab2, tab3 = st.tabs(["🎯 Match Score", "✍️ Optimize ATS", "🎙️ Coach"])

    with tab1:
        if st.button("ANALIZAR COMPATIBILIDAD →"):
            if not cv_t or not job: st.warning("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"Score 0-100 y 2 tips en Español. CV: {cv_t} Job: {job}")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:20px; font-size:14px;">{res}</div>', unsafe_allow_html=True)

    with tab2:
        if st.button("GENERAR CV ATS PRO →"):
            if not cv_t or not job: st.warning("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"Reescribe este CV para ATS en Español, una carilla. Sin horarios. Disponibilidad inmediata. CV: {cv_t} Job: {job}")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:20px; font-size:14px;">{res}</div>', unsafe_allow_html=True)

    with tab3:
        if st.button("PREPARAR ENTREVISTA →"):
            if not cv_t or not job: st.warning("Faltan datos")
            else:
                with st.spinner("..."):
                    res = llamar_ia(f"3 preguntas difíciles para {job} según mi perfil.")
                    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; border-left:4px solid #DFFF00; margin-top:20px; font-size:14px;">{res}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><center style='opacity:0.1; font-size:10px;'>⚙️ &nbsp; &nbsp; 📱 &nbsp; &nbsp; 👤</center>", unsafe_allow_html=True)
