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

# 1. CONFIGURACIÓN DE PÁGINA (Favicon con la W sola)
try:
    fav = Image.open("favicon.png")
    st.set_page_config(page_title="workersCV", page_icon=fav, layout="centered", initial_sidebar_state="collapsed")
except:
    st.set_page_config(page_title="workersCV", page_icon="🎯", layout="centered", initial_sidebar_state="collapsed")

# 2. ESTILO "workersCV" DARK PREMIUM (Sin API Key)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    label { display: none !important; visibility: hidden !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .stApp { 
        background-color: #1A1A1A; 
        color: white;
    }
    
    .block-container { padding-top: 1.5rem !important; max-width: 600px !important; }

    h1 { font-size: 50px !important; text-align: center; color: #DFFF00; margin-bottom: 2px !important; letter-spacing: -2px; font-weight: 900; }
    .legend { color: #888; text-align: center; margin-bottom: 25px; font-size: 13px; line-height: 1.4; }

    .section-label {
        background-color: #DFFF00; color: black; padding: 2px 15px;
        border-radius: 50px; font-weight: 800; font-size: 10px;
        display: inline-block; margin-bottom: 8px; text-transform: uppercase;
    }

    .stCard {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px; padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
    }

    .stTextArea textarea {
        background-color: #000 !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important; color: #DFFF00 !important;
        font-size: 13px !important;
    }

    .stTabs [data-baseweb="tab"] { font-size: 11px !important; color: #777; height: 35px; }
    .stTabs [aria-selected="true"] { 
        background-color: #DFFF00 !important; color: black !important; font-weight: bold; border-radius: 10px 10px 0 0; 
    }

    div.stButton > button {
        background: #DFFF00 !important; color: black !important;
        border-radius: 30px !important; font-weight: 900 !important;
        height: 48px !important; width: 100%; border: none; text-transform: uppercase;
    }

    .ai-response {
        background: rgba(0, 0, 0, 0.6);
        border-radius: 15px; padding: 15px;
        border-left: 5px solid #DFFF00; color: #EEE; font-size: 13px; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TRADUCCIONES ---
idiomas = {
    "Español": {"leg": "Optimización ATS y Simulador de Entrevistas. Libre y profesional.", "tabs": ["Análisis", "Optimizar CV", "Empresa", "Coach", "Historial"], "ia": "Responde en Español."},
    "English": {"leg": "ATS Optimization & Interview Simulator. Free and professional.", "tabs": ["Analysis", "Optimize CV", "Company", "Coach", "History"], "ia": "Respond in English."},
    "Français": {"leg": "Optimisation ATS et simulateur d'entretien.", "tabs": ["Analyse", "Optimiser", "Entreprise", "Coach", "Historique"], "ia": "Répondez en Français."},
    "Português": {"leg": "Otimização de ATS e simulador de entrevista.", "tabs": ["Análise", "Otimizar", "Empresa", "Coach", "Histórico"], "ia": "Responda em Português."},
    "Deutsch": {"leg": "ATS-Optimierung und Interview-Simulator.", "tabs": ["Analyse", "Optimieren", "Unternehmen", "Coach", "Verlauf"], "ia": "Antworte auf Deutsch."},
    "Italiano": {"leg": "Ottimizzazione ATS e simulatore di interviste.", "tabs": ["Analisi", "Ottimizza", "Azienda", "Coach", "Cronologia"], "ia": "Rispondi in Italiano."},
    "Русский": {"leg": "Оптимизация ATS и симулятор интервью.", "tabs": ["Анализ", "Оптимизация", "Компания", "Коуч", "История"], "ia": "Отвечай по-русски."},
    "中文": {"leg": "ATS 优化和面试模拟器。", "tabs": ["分析", "优化", "公司", "教练", "历史"], "ia": "用中文回答。"},
    "日本語": {"leg": "ATS最適化と面接シミュレーター。", "tabs": ["分析", "最適化", "企業", "コーチ", "履歴"], "ia": "日本語で答えて。"},
    "한국어": {"leg": "ATS 최적화 및 인터뷰 시뮬레이터.", "tabs": ["분석", "최적화", "기업", "코치", "히스토리"], "ia": "한국어로 답변해."}
}

# --- LÓGICA IA (Usa st.secrets de forma invisible) ---
def llamar_ia(p):
    try:
        # Busca la llave en la configuración interna (Secrets)
        api_key_interna = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key_interna)
        
        # Scanner automático de modelos activos
        vivos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        modelo_nombre = next((m for m in vivos if "1.5-flash" in m), vivos[0])
        
        model = genai.GenerativeModel(modelo_nombre, generation_config={"temperature": 0.1})
        
        # Reintento por si Google está saturado
        for _ in range(2):
            try: return model.generate_content(p).text
            except: time.sleep(3); continue
        return "⚠️ Servidor ocupado. Reintenta en 10 segundos."
    except Exception as e:
        return "Error: No se pudo conectar con el cerebro de workersCV. Verifica los Secrets."

# --- GENERADORES DE ARCHIVOS ---
def limpiar(t): return re.sub(r'\*|_|#', '', t).strip()

def crear_word(t):
    doc = Document()
    doc.add_paragraph(limpiar(t))
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

class PDF(FPDF):
    def add_cv_data(self, raw):
        self.add_page(); self.set_font("Arial", size=10)
        safe = limpiar(raw).encode('latin-1', 'ignore').decode('latin-1')
        self.multi_cell(0, 5, safe)

# --- INTERFAZ workersCV ---
if "historial" not in st.session_state: st.session_state.historial = []

# Selector de Idioma (Sutil arriba a la derecha)
_, col_l = st.columns([4, 1])
with col_l:
    sel_lang = st.selectbox("", list(idiomas.keys()), label_visibility="collapsed")
    t = idiomas[sel_lang]

st.markdown("<h1>workersCV</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='legend'>{t['leg']}</p>", unsafe_allow_html=True)

# Tarjeta Central (SIN API KEY)
st.markdown('<div class="stCard">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="section-label">TU CV (PDF)</div>', unsafe_allow_html=True)
    cv_f = st.file_uploader("c", type="pdf")
with c2:
    st.markdown('<div class="section-label">OFERTA LABORAL</div>', unsafe_allow_html=True)
    job = st.text_area("j", placeholder="Pega los requisitos aquí...", height=70)
st.markdown('</div>', unsafe_allow_html=True)

# Lógica de lectura
cv_texto = ""
if cv_f:
    r = PyPDF2.PdfReader(cv_f)
    for pg in r.pages: cv_texto += pg.extract_text()

tabs = st.tabs(t["tabs"])

with tabs[0]: # ANÁLISIS
    if st.button("ANALIZAR COMPATIBILIDAD →"):
        if not cv_texto or not job: st.error("Faltan datos")
        else:
            with st.spinner("..."):
                res = llamar_ia(f"{t['ia']} Score 0-100 y 2 consejos. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div class="ai-response">{res}</div>', unsafe_allow_html=True)
                score = re.search(r'\d+', res).group() if re.search(r'\d+', res) else "0"
                st.session_state.historial.insert(0, {"f": datetime.now().strftime("%H:%M"), "s": score})

with tabs[1]: # OPTIMIZAR
    if st.button("DISEÑAR CV ATS PRO →"):
        if not cv_texto or not job: st.error("Faltan datos")
        else:
            with st.spinner("..."):
                raw = llamar_ia(f"{t['ia']} Reescribe mi CV para ATS, una carilla. Sin horarios. Disponibilidad inmediata. CV: {cv_texto} Job: {job}")
                st.markdown(f'<div class="ai-response">{raw}</div>', unsafe_allow_html=True)
                
                c_pdf, c_word = st.columns(2)
                with c_pdf:
                    pdf = PDF(); pdf.add_cv_data(raw)
                    st.download_button("📥 PDF", data=pdf.output(dest='S').encode('latin-1'), file_name="workersCV_Pro.pdf")
                with c_word:
                    st.download_button("📝 WORD", data=crear_word(raw), file_name="workersCV_Pro.docx")

with tabs[2]: # EMPRESA
    emp_n = st.text_input("e", placeholder="Nombre de la empresa...")
    if st.button("INVESTIGAR VALORES →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(f"{t['ia']} Historia y cultura de {emp_n}")}</div>', unsafe_allow_html=True)

with tabs[3]: # COACH
    if st.button("SIMULAR ENTREVISTA →"):
        st.markdown(f'<div class="ai-response">{llamar_ia(f"{t['ia']} 3 preguntas de entrevista para {job} según mi CV")}</div>', unsafe_allow_html=True)

with tabs[4]: # HISTORIAL
    for i in st.session_state.historial[:5]:
        st.write(f"🕒 {i['f']} - Match: **{i['s']}%**")

st.markdown("<br><center style='opacity:0.1; font-size:10px;'>⚙️ &nbsp; &nbsp; 📱 &nbsp; &nbsp; 👤</center>", unsafe_allow_html=True)